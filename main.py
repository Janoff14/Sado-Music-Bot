# ===================================================================
# IMPORTS AND CONFIGURATION
# ===================================================================
# This section handles all necessary imports and loads environment variables

import os
import sqlite3
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import traceback
from urllib.parse import urlparse
import psycopg2

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS user_settings (
    user_id BIGINT PRIMARY KEY,
    lang TEXT DEFAULT 'uz',
    anonymous_default INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS artists (
    artist_id TEXT PRIMARY KEY,
    tg_user_id BIGINT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    payment_link TEXT,
    profile_url TEXT,
    default_genre TEXT,
    bio TEXT,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS submissions (
    submission_id TEXT PRIMARY KEY,
    artist_id TEXT NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
    submitter_user_id BIGINT NOT NULL,
    title TEXT NOT NULL,
    genre TEXT NOT NULL,
    caption TEXT,
    telegram_file_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    admin_message_id BIGINT,
    created_at INTEGER NOT NULL,
    reviewed_at INTEGER
);

CREATE TABLE IF NOT EXISTS tracks (
    track_id TEXT PRIMARY KEY,
    artist_id TEXT NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    genre TEXT NOT NULL,
    caption TEXT,
    telegram_file_id TEXT,
    channel_message_id BIGINT NOT NULL,
    discussion_anchor_message_id BIGINT DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS donation_events (
    donation_id TEXT PRIMARY KEY,
    track_id TEXT NOT NULL REFERENCES tracks(track_id) ON DELETE CASCADE,
    artist_id TEXT NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
    donor_user_id BIGINT,
    donor_name TEXT,
    donor_username TEXT,
    amount INTEGER NOT NULL,
    note TEXT,
    is_anonymous INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    confirmed_at INTEGER
);

CREATE INDEX IF NOT EXISTS idx_submissions_artist_id ON submissions(artist_id);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_tracks_artist_id ON tracks(artist_id);
CREATE INDEX IF NOT EXISTS idx_tracks_status ON tracks(status);
CREATE INDEX IF NOT EXISTS idx_donations_track_id ON donation_events(track_id);
CREATE INDEX IF NOT EXISTS idx_donations_artist_id ON donation_events(artist_id);
CREATE INDEX IF NOT EXISTS idx_donations_status ON donation_events(status);
"""

def init_db() -> None:
    print("INIT_DB: starting")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("INIT_DB: DATABASE_URL env var is missing")
    p = urlparse(db_url)
    print(f"INIT_DB: connecting host={p.hostname} db={p.path.lstrip('/')} user={p.username}")
    try:
        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cur:
                statements = [s.strip() for s in SCHEMA_SQL.split(";") if s.strip()]
                for stmt in statements:
                    cur.execute(stmt)
            conn.commit()
        print("INIT_DB: done OK (tables ensured)")
    except Exception as e:
        print("INIT_DB: FAILED:", repr(e))
        traceback.print_exc()
        raise

# Load environment variables from .env file
load_dotenv()

# Telegram bot framework imports
from telegram import (
    InlineKeyboardButton,    # For creating inline buttons
    InlineKeyboardMarkup,    # For arranging inline buttons
    Update,                  # Represents incoming updates
)
from telegram.ext import (
    Application,             # Main bot application
    CallbackQueryHandler,    # Handles button clicks
    CommandHandler,          # Handles /commands
    ContextTypes,            # Type hints for context
    ConversationHandler,     # Multi-step conversations
    MessageHandler,          # Handles regular messages
    filters,                 # Message filters
)

# ===================================================================
# BOT CONFIGURATION
# ===================================================================

# Bot token from BotFather (loaded from .env file)
TOKEN = os.getenv("BOT_TOKEN")

# Database path - stores all bot data (artists, tracks, etc.)
DB_PATH = Path(__file__).with_name("bot.db")

# Available music genres for track categorization
GENRES = ["Pop", "Rock", "Indie", "Hip Hop", "Rap", "Electronic", "Other"]

# Channel mapping: which channel to post tracks based on genre
# NOTE: Bot must be admin in all these channels to post tracks
GENRE_CHANNELS = {
    "Pop": "@sado_pop1",
    "Rock": "@sado_rock",
    "Indie": "@sado_discovery",
    "Hip Hop": "@sado_hiphop",
    "Rap": "@sado_hiphop",
    "Electronic": "@sado_discovery",
    "Other": "@sado_discovery",
}

# Admin user ID who can approve/reject track submissions
# NOTE: Change this to your Telegram user ID
ADMIN_ID = 2029020229

# ===================================================================
# DATABASE LAYER
# ===================================================================
# These functions handle all interactions with the SQLite database
# Database stores: artists, tracks, user settings, and language preferences

# -------------------- Database Connection --------------------
def db() -> sqlite3.Connection:
    """
    Creates and returns a database connection.
    Sets row_factory to sqlite3.Row for dict-like access to rows.
    """
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row  # Allows accessing columns by name
    return con


# -------------------- Database Initialization --------------------
def db_init() -> None:
    """
    Initialize all database tables if they don't exist.
    Called once when the bot starts.

    Tables created:
    - user_settings: Language preferences for each user
    - artists: Artist profiles (name, payment link, bio, etc.)
    - tracks: Submitted tracks with status (PENDING/APPROVED/REJECTED)
    """
    with db() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                lang TEXT NOT NULL
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS artists (
                artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_user_id INTEGER UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                payment_link TEXT NOT NULL,
                default_genre TEXT,
                bio TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS tracks (
                track_id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                genre TEXT NOT NULL,
                caption TEXT,
                telegram_file_id TEXT NOT NULL,
                status TEXT NOT NULL, -- PENDING / APPROVED / REJECTED
                submitted_at TEXT NOT NULL,
                FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
            )
            """
        )
        con.commit()


# ===================================================================
# DATABASE QUERY FUNCTIONS
# ===================================================================
# Functions for retrieving and modifying data in the database

# -------------------- User Language Settings --------------------
def db_get_lang(user_id: int) -> str | None:
    """Get user's selected language (uz=Uzbek, ru=Russian)"""
    with db() as con:
        row = con.execute("SELECT lang FROM users WHERE user_id=?", (user_id,)).fetchone()
        return row["lang"] if row else None


def db_set_lang(user_id: int, lang: str) -> None:
    """Save user's language preference (uz or ru)"""
    with db() as con:
        con.execute(
            """
            INSERT INTO users(user_id, lang) VALUES(?, ?)
            ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang
            """,
            (user_id, lang),
        )
        con.commit()


# -------------------- Artist Profile Management --------------------
def db_get_artist_by_tg(tg_user_id: int) -> sqlite3.Row | None:
    """Get artist profile by their Telegram user ID"""
    with db() as con:
        return con.execute(
            "SELECT * FROM artists WHERE tg_user_id=?",
            (tg_user_id,),
        ).fetchone()


def db_create_artist(
    tg_user_id: int,
    display_name: str,
    payment_link: str,
    default_genre: str | None,
    bio: str | None,
) -> int:
    """
    Create a new artist profile in the database.
    Returns the newly created artist_id.
    """
    with db() as con:
        cur = con.execute(
            """
            INSERT INTO artists(tg_user_id, display_name, payment_link, default_genre, bio, created_at)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (tg_user_id, display_name, payment_link, default_genre, bio, datetime.utcnow().isoformat()),
        )
        con.commit()
        return int(cur.lastrowid)


def db_update_artist_field(artist_id: int, field: str, value: str | None) -> None:
    """
    Update a specific field in an artist's profile.
    Allowed fields: display_name, payment_link, default_genre, bio
    """
    if field not in {"display_name", "payment_link", "default_genre", "bio"}:
        raise ValueError("Invalid field")
    with db() as con:
        con.execute(f"UPDATE artists SET {field}=? WHERE artist_id=?", (value, artist_id))
        con.commit()


# -------------------- Track Submission Management --------------------
def db_add_track_pending(
    artist_id: int,
    title: str,
    genre: str,
    caption: str | None,
    telegram_file_id: str,
) -> int:
    """
    Add a new track with PENDING status (awaiting admin approval).
    Returns the new track_id.
    """
    with db() as con:
        cur = con.execute(
            """
            INSERT INTO tracks(artist_id, title, genre, caption, telegram_file_id, status, submitted_at)
            VALUES(?, ?, ?, ?, ?, 'PENDING', ?)
            """,
            (artist_id, title, genre, caption, telegram_file_id, datetime.utcnow().isoformat()),
        )
        con.commit()
        return int(cur.lastrowid)


def db_list_artist_tracks(artist_id: int, limit: int = 10) -> list[sqlite3.Row]:
    """Get list of tracks for an artist (most recent first)"""
    with db() as con:
        rows = con.execute(
            """
            SELECT track_id, title, genre, status, submitted_at
            FROM tracks
            WHERE artist_id=?
            ORDER BY track_id DESC
            LIMIT ?
            """,
            (artist_id, limit),
        ).fetchall()
        return list(rows)


def db_get_track(track_id: int) -> sqlite3.Row | None:
    """Get track details by track ID"""
    with db() as con:
        return con.execute(
            "SELECT * FROM tracks WHERE track_id=?",
            (track_id,),
        ).fetchone()


def db_update_track_status(track_id: int, status: str) -> None:
    """
    Update track status: PENDING -> APPROVED or REJECTED
    Called by admin after reviewing the submission
    """
    with db() as con:
        con.execute(
            "UPDATE tracks SET status=? WHERE track_id=?",
            (status, track_id),
        )
        con.commit()


def db_get_artist(artist_id: int) -> sqlite3.Row | None:
    with db() as con:
        return con.execute(
            "SELECT * FROM artists WHERE artist_id=?",
            (artist_id,),
        ).fetchone()


# -------------------- UI helpers --------------------
def kb_lang() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang:uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru"),
        ]]
    )


def kb_genres(prefix: str) -> InlineKeyboardMarkup:
    # callback_data like: f"{prefix}:Pop"
    rows = []
    row = []
    for i, g in enumerate(GENRES, start=1):
        row.append(InlineKeyboardButton(g, callback_data=f"{prefix}:{g}"))
        if i % 2 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("Cancel", callback_data=f"{prefix}:CANCEL")])
    return InlineKeyboardMarkup(rows)


def fmt_artist_profile(artist: sqlite3.Row) -> str:
    bio = artist["bio"] or "—"
    dg = artist["default_genre"] or "—"
    return (
        f"🎤 **{artist['display_name']}**\n"
        f"💳 Payment: {artist['payment_link']}\n"
        f"🎧 Default genre: {dg}\n"
        f"📝 Bio: {bio}"
    )


def kb_profile_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✏️ Edit name", callback_data="profile:edit:display_name")],
            [InlineKeyboardButton("💳 Edit payment link", callback_data="profile:edit:payment_link")],
            [InlineKeyboardButton("🎧 Edit default genre", callback_data="profile:edit:default_genre")],
            [InlineKeyboardButton("📝 Edit bio", callback_data="profile:edit:bio")],
        ]
    )


def kb_review(track_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("✅ Approve", callback_data=f"review:approve:{track_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"review:reject:{track_id}"),
        ]]
    )



# -------------------- Language handlers --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id

    # Check for deep link parameters (e.g., /start profile_123)
    if context.args and len(context.args) > 0:
        param = context.args[0]

        # Handle profile_<artist_id> deep link - show artist profile to visitor
        if param.startswith("profile_"):
            try:
                artist_id = int(param.replace("profile_", ""))
                artist = db_get_artist(artist_id)
                if artist:
                    # Show artist profile
                    tracks = db_list_artist_tracks(artist["artist_id"], limit=5)
                    tracks_text = "\n".join([f"• {t['title']} ({t['genre']})" for t in tracks if t['status'] == 'APPROVED']) or "No tracks yet"

                    profile_text = (
                        f"🎤 **{artist['display_name']}**\n"
                        f"🎧 Genre: {artist['default_genre'] or '—'}\n"
                        f"📝 {artist['bio'] or '—'}\n\n"
                        f"🎵 **Tracks:**\n{tracks_text}\n\n"
                        f"💳 Support this artist: {artist['payment_link']}"
                    )
                    await update.message.reply_text(profile_text, parse_mode="Markdown")
                    return
                else:
                    await update.message.reply_text("❌ Artist not found.")
                    return
            except ValueError:
                pass  # Invalid artist_id, continue to normal start

    # Normal /start flow
    lang = db_get_lang(user_id)
    if not lang:
        await update.message.reply_text(
            "Choose language / Tilni tanlang / Выберите язык:",
            reply_markup=kb_lang(),
        )
        return

    await update.message.reply_text("✅ Ready. Use /submit to upload or /profile to edit your artist profile.")


async def on_lang_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not q or not q.from_user:
        return
    await q.answer()
    data = q.data or ""
    if not data.startswith("lang:"):
        return
    lang = data.split(":", 1)[1]
    if lang not in ("uz", "ru"):
        return
    db_set_lang(q.from_user.id, lang)
    await q.edit_message_text("✅ Saved. Now use /submit to upload or /profile to manage your profile.")


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Returns the chat_id of the current chat. Useful for getting channel IDs."""
    if update.effective_chat:
        await update.message.reply_text(f"chat_id: {update.effective_chat.id}")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message with available commands"""
    if not update.message:
        return

    help_text = (
        "🎵 <b>Sado Music Bot - Help</b>\n\n"
        "<b>Available Commands:</b>\n\n"
        "/start - Start the bot and select your language\n"
        "/submit - Submit a new track for review\n"
        "/profile - View and edit your artist profile\n"
        "/help - Show this help message\n"
        "/chatid - Get the current chat ID (useful for admins)\n"
        "/cancel - Cancel any ongoing operation\n\n"
        "<b>How it works:</b>\n"
        "1️⃣ Use /submit to create your artist profile\n"
        "2️⃣ Upload your track for admin review\n"
        "3️⃣ Once approved, your track gets posted to channels\n"
        "4️⃣ Fans can support you via your payment link\n\n"
        "Need help? Contact the admin!"
    )

    await update.message.reply_text(help_text, parse_mode="HTML")


# -------------------- /profile --------------------
PROFILE_EDIT_FIELD = 2001  # conversation state


async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message or not update.effective_user:
        return ConversationHandler.END

    artist = db_get_artist_by_tg(update.effective_user.id)
    if not artist:
        await update.message.reply_text("You don't have an artist profile yet. Use /submit to create one.")
        return ConversationHandler.END

    tracks = db_list_artist_tracks(artist["artist_id"], limit=5)
    tracks_text = "\n".join([f"• {t['title']} ({t['genre']}) — {t['status']}" for t in tracks]) or "—"

    await update.message.reply_markdown(
        fmt_artist_profile(artist) + "\n\n🎵 Recent tracks:\n" + tracks_text,
        reply_markup=kb_profile_actions(),
    )
    return ConversationHandler.END


async def profile_edit_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    if not q or not q.from_user:
        return ConversationHandler.END
    await q.answer()

    artist = db_get_artist_by_tg(q.from_user.id)
    if not artist:
        await q.edit_message_text("No profile found. Use /submit first.")
        return ConversationHandler.END

    data = q.data or ""
    # profile:edit:<field>
    parts = data.split(":")
    if len(parts) != 3:
        return ConversationHandler.END

    field = parts[2]
    context.user_data["edit_artist_id"] = artist["artist_id"]
    context.user_data["edit_field"] = field

    if field == "default_genre":
        await q.edit_message_text("Choose your default genre:", reply_markup=kb_genres("profilegenre"))
        return PROFILE_EDIT_FIELD

    prompt = {
        "display_name": "Send your new artist name:",
        "payment_link": "Send your new payment link (Click/Payme URL):",
        "bio": "Send your new bio (1–2 lines), or '-' to clear:",
    }.get(field, "Send new value:")

    await q.edit_message_text(prompt)
    return PROFILE_EDIT_FIELD


async def profile_edit_genre_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    if not q or not q.from_user:
        return ConversationHandler.END
    await q.answer()

    data = q.data or ""
    # profilegenre:<GENRE>
    if not data.startswith("profilegenre:"):
        return ConversationHandler.END

    choice = data.split(":", 1)[1]
    if choice == "CANCEL":
        await q.edit_message_text("Cancelled.")
        return ConversationHandler.END

    artist_id = context.user_data.get("edit_artist_id")
    if not artist_id:
        await q.edit_message_text("Session expired. Run /profile again.")
        return ConversationHandler.END

    db_update_artist_field(int(artist_id), "default_genre", choice)
    await q.edit_message_text(f"✅ Default genre updated to: {choice}")
    return ConversationHandler.END


async def profile_edit_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message or not update.effective_user:
        return ConversationHandler.END

    artist_id = context.user_data.get("edit_artist_id")
    field = context.user_data.get("edit_field")
    if not artist_id or not field:
        await update.message.reply_text("Session expired. Run /profile again.")
        return ConversationHandler.END

    val = (update.message.text or "").strip()
    if field == "bio" and val == "-":
        val = ""

    db_update_artist_field(int(artist_id), field, val if val != "" else None)
    await update.message.reply_text("✅ Updated.")
    context.user_data.pop("edit_artist_id", None)
    context.user_data.pop("edit_field", None)
    return ConversationHandler.END


# -------------------- /submit --------------------
(
    SUB_ONBOARD_NAME,
    SUB_ONBOARD_PAYLINK,
    SUB_ONBOARD_GENRE,
    SUB_ONBOARD_BIO,
    SUB_UPLOAD_AUDIO,
    SUB_TITLE,
    SUB_GENRE,
    SUB_CAPTION,
) = range(8)


async def submit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message or not update.effective_user:
        return ConversationHandler.END

    artist = db_get_artist_by_tg(update.effective_user.id)
    if not artist:
        await update.message.reply_text("🎤 First time here. Let's create your artist profile.\n\nSend your artist name:")
        return SUB_ONBOARD_NAME

    # returning artist shortcut
    await update.message.reply_text(
        f"Uploading as: **{artist['display_name']}**\n\nSend your audio file (as Music/Audio, not voice note).",
        parse_mode="Markdown",
    )
    context.user_data["artist_id"] = artist["artist_id"]
    context.user_data["default_genre"] = artist["default_genre"]
    return SUB_UPLOAD_AUDIO


# --- onboarding ---
async def onboard_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = (update.message.text or "").strip()
    if len(name) < 2:
        await update.message.reply_text("Name too short. Send your artist name again:")
        return SUB_ONBOARD_NAME
    context.user_data["onb_name"] = name
    await update.message.reply_text("Send your payment link (Click/Payme URL):")
    return SUB_ONBOARD_PAYLINK


async def onboard_paylink(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    link = (update.message.text or "").strip()
    if not (link.startswith("http://") or link.startswith("https://")):
        await update.message.reply_text("Please send a valid URL starting with http(s)://")
        return SUB_ONBOARD_PAYLINK
    context.user_data["onb_paylink"] = link
    await update.message.reply_text("Choose your default genre:", reply_markup=kb_genres("onbgenre"))
    return SUB_ONBOARD_GENRE


async def onboard_genre_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    if not q or not q.from_user:
        return ConversationHandler.END
    await q.answer()

    choice = (q.data or "").split(":", 1)[1]
    if choice == "CANCEL":
        await q.edit_message_text("Cancelled.")
        return ConversationHandler.END

    context.user_data["onb_default_genre"] = choice
    await q.edit_message_text("Optional: send a short bio (1–2 lines), or type '-' to skip.")
    return SUB_ONBOARD_BIO


async def onboard_bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    bio = (update.message.text or "").strip()
    if bio == "-":
        bio = None

    name = context.user_data.get("onb_name")
    link = context.user_data.get("onb_paylink")
    dg = context.user_data.get("onb_default_genre")

    if not update.effective_user:
        return ConversationHandler.END

    artist_id = db_create_artist(
        tg_user_id=update.effective_user.id,
        display_name=name,
        payment_link=link,
        default_genre=dg,
        bio=bio,
    )

    # clear onboarding temp
    for k in ["onb_name", "onb_paylink", "onb_default_genre"]:
        context.user_data.pop(k, None)

    context.user_data["artist_id"] = artist_id
    context.user_data["default_genre"] = dg

    await update.message.reply_text("✅ Profile created. Now send your audio file (as Music/Audio).")
    return SUB_UPLOAD_AUDIO


# --- submission ---
async def sub_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message:
        return ConversationHandler.END

    audio = update.message.audio
    if not audio:
        await update.message.reply_text("Please send an audio file (Music/Audio). Voice notes aren't supported yet.")
        return SUB_UPLOAD_AUDIO

    context.user_data["file_id"] = audio.file_id
    await update.message.reply_text("Now send the track title:")
    return SUB_TITLE


async def sub_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    title = (update.message.text or "").strip()
    if len(title) < 2:
        await update.message.reply_text("Title too short. Send the track title again:")
        return SUB_TITLE
    context.user_data["title"] = title

    default_genre = context.user_data.get("default_genre")
    if default_genre:
        await update.message.reply_text(
            f"Choose genre (default: {default_genre}):",
            reply_markup=kb_genres("subgenre"),
        )
    else:
        await update.message.reply_text("Choose genre:", reply_markup=kb_genres("subgenre"))
    return SUB_GENRE


async def sub_genre_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    if not q:
        return ConversationHandler.END
    await q.answer()

    choice = (q.data or "").split(":", 1)[1]
    if choice == "CANCEL":
        await q.edit_message_text("Cancelled.")
        return ConversationHandler.END

    context.user_data["genre"] = choice
    await q.edit_message_text("Optional: send a short caption (one line), or type '-' to skip.")
    return SUB_CAPTION


async def sub_caption(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    caption = (update.message.text or "").strip()
    if caption == "-":
        caption = None

    artist_id = context.user_data.get("artist_id")
    file_id = context.user_data.get("file_id")
    title = context.user_data.get("title")
    genre = context.user_data.get("genre")

    if not all([artist_id, file_id, title, genre]):
        await update.message.reply_text("Something went wrong (missing data). Try /submit again.")
        return ConversationHandler.END

    track_id = db_add_track_pending(
        artist_id=int(artist_id),
        title=title,
        genre=genre,
        caption=caption,
        telegram_file_id=file_id,
    )

    # Get artist info for review card
    artist = db_get_artist(int(artist_id))
    artist_name = artist["display_name"] if artist else "Unknown"

    # Send review card to admin
    review_text = (
        f"🎵 **New Track Submission**\n\n"
        f"**Title:** {title}\n"
        f"**Artist:** {artist_name}\n"
        f"**Genre:** {genre}\n"
        f"**Caption:** {caption or '—'}\n"
        f"**Track ID:** #{track_id}"
    )

    try:
        await context.bot.send_audio(
            chat_id=ADMIN_ID,
            audio=file_id,
            caption=review_text,
            parse_mode="Markdown",
            reply_markup=kb_review(track_id),
        )
    except Exception as e:
        # Log error but don't fail the submission
        print(f"Failed to send review to admin: {e}")

    # clear submission temp (keep artist_id/default_genre)
    for k in ["file_id", "title", "genre"]:
        context.user_data.pop(k, None)

    await update.message.reply_text(
        f"✅ Submitted for review.\nSubmission ID: #{track_id}\n\n(Next step: admins approve it and it gets posted.)"
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message:
        await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


async def on_review_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle admin approve/reject actions on track submissions."""
    q = update.callback_query
    if not q or not q.from_user:
        return
    await q.answer()

    # Check if user is admin
    if q.from_user.id != ADMIN_ID:
        await q.answer("You are not authorized to review tracks.", show_alert=True)
        return

    data = q.data or ""
    # review:approve:123 or review:reject:123
    parts = data.split(":")
    if len(parts) != 3:
        return

    action = parts[1]
    try:
        track_id = int(parts[2])
    except ValueError:
        return

    track = db_get_track(track_id)
    if not track:
        await q.edit_message_caption("❌ Track not found.")
        return

    if track["status"] != "PENDING":
        await q.edit_message_caption(f"⚠️ Track already {track['status'].lower()}.")
        return

    artist = db_get_artist(track["artist_id"])
    artist_tg_id = artist["tg_user_id"] if artist else None
    artist_name = artist["display_name"] if artist else "Unknown"

    if action == "approve":
        # Update status
        db_update_track_status(track_id, "APPROVED")

        # Post to genre channel
        channel = GENRE_CHANNELS.get(track["genre"], "@sado_discovery")

        # Get bot username for deep links
        bot_me = await context.bot.get_me()
        bot_username = bot_me.username

        # Build caption with inline text links
        post_caption = (
            f"🎵 **{track['title']}**\n"
            f"🎤 {artist_name}\n"
        )
        if track["caption"]:
            post_caption += f"\n{track['caption']}\n"

        # Add artist profile link
        if bot_username:
            artist_profile_url = f"https://t.me/{bot_username}?start=profile_{track['artist_id']}"
            post_caption += f"\n👤 [Artist Profile]({artist_profile_url})"

        # Add donation link
        if artist and artist["payment_link"]:
            post_caption += f"\n💳 [Support this artist]({artist['payment_link']})"

        try:
            await context.bot.send_audio(
                chat_id=channel,
                audio=track["telegram_file_id"],
                caption=post_caption,
                parse_mode="Markdown",
            )
            await q.edit_message_caption(
                f"✅ Approved and posted to {channel}\n\n"
                f"Title: {track['title']}\n"
                f"Artist: {artist_name}"
            )
        except Exception as e:
            await q.edit_message_caption(f"✅ Approved but failed to post: {e}")

        # Notify artist
        if artist_tg_id:
            try:
                await context.bot.send_message(
                    chat_id=artist_tg_id,
                    text=f"🎉 Your track **{track['title']}** has been approved and posted to {channel}!",
                    parse_mode="Markdown",
                )
            except Exception:
                pass

    elif action == "reject":
        db_update_track_status(track_id, "REJECTED")
        await q.edit_message_caption(
            f"❌ Rejected\n\n"
            f"Title: {track['title']}\n"
            f"Artist: {artist_name}"
        )

        # Notify artist
        if artist_tg_id:
            try:
                await context.bot.send_message(
                    chat_id=artist_tg_id,
                    text=f"😔 Your track **{track['title']}** was not approved. Try submitting a different track!",
                    parse_mode="Markdown",
                )
            except Exception:
                pass



# -------------------- Command menu setup --------------------
async def setup_bot_commands(application: Application) -> None:
    """Set up the bot command menu visible in Telegram"""
    from telegram import BotCommand

    commands = [
        BotCommand("start", "Start the bot and select language"),
        BotCommand("submit", "Submit a new track for review"),
        BotCommand("profile", "View and edit your artist profile"),
        BotCommand("help", "Show help and available commands"),
        BotCommand("chatid", "Get the current chat ID"),
        BotCommand("cancel", "Cancel current operation"),
    ]

    await application.bot.set_my_commands(commands)
    print("✅ Bot command menu configured")


# -------------------- main --------------------
def main() -> None:
    init_db()  # <-- ensure Postgres tables and indexes before anything else
    if not TOKEN:
        raise RuntimeError("Set BOT_TOKEN environment variable first.")
    db_init()

    app = Application.builder().token(TOKEN).build()

    # Set up command menu
    app.post_init = setup_bot_commands

    # language
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_lang_choice, pattern=r"^lang:"))

    # utility
    app.add_handler(CommandHandler("chatid", chatid))
    app.add_handler(CommandHandler("help", help_cmd))

    # admin review
    app.add_handler(CallbackQueryHandler(on_review_action, pattern=r"^review:"))


    # profile (simple command + edit callbacks)
    app.add_handler(CommandHandler("profile", profile_cmd))
    app.add_handler(CallbackQueryHandler(profile_edit_router, pattern=r"^profile:edit:"))
    app.add_handler(CallbackQueryHandler(profile_edit_genre_choice, pattern=r"^profilegenre:"))

    # profile edit text conversation (only used after pressing profile edit buttons)
    profile_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(profile_edit_router, pattern=r"^profile:edit:")],
        states={
            PROFILE_EDIT_FIELD: [
                CallbackQueryHandler(profile_edit_genre_choice, pattern=r"^profilegenre:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, profile_edit_text),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    app.add_handler(profile_conv)

    # submit conversation
    submit_conv = ConversationHandler(
        entry_points=[CommandHandler("submit", submit_cmd)],
        states={
            SUB_ONBOARD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboard_name)],
            SUB_ONBOARD_PAYLINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboard_paylink)],
            SUB_ONBOARD_GENRE: [CallbackQueryHandler(onboard_genre_choice, pattern=r"^onbgenre:")],
            SUB_ONBOARD_BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboard_bio)],
            SUB_UPLOAD_AUDIO: [MessageHandler(filters.AUDIO, sub_audio), MessageHandler(filters.ALL, sub_audio)],
            SUB_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sub_title)],
            SUB_GENRE: [CallbackQueryHandler(sub_genre_choice, pattern=r"^subgenre:")],
            SUB_CAPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, sub_caption)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    app.add_handler(submit_conv)

    app.run_polling()


if __name__ == "__main__":
    main()
