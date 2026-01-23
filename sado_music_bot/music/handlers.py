"""
Music handlers - user-facing commands for artist profiles and track submissions
"""
import logging
import uuid
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sado_music_bot.config import Config
from sado_music_bot.db import DB
from sado_music_bot.keyboards import kb_lang, kb_genres, kb_profile_actions, kb_admin_review
from sado_music_bot.texts import track_caption_with_payment
from sado_music_bot.i18n import t

router = Router()
logger = logging.getLogger(__name__)


# =====================
# FSM States
# =====================
class OnboardingStates(StatesGroup):
    waiting_name = State()
    waiting_payment_link = State()
    waiting_genre = State()
    waiting_bio = State()


class SubmitStates(StatesGroup):
    waiting_audio = State()
    waiting_title = State()
    waiting_genre = State()
    waiting_caption = State()


class ProfileEditStates(StatesGroup):
    waiting_value = State()


# =====================
# /start
# =====================
@router.message(Command("start"))
async def cmd_start(m: Message, db: DB, cfg: Config):
    if not m.from_user:
        return

    user_id = m.from_user.id
    lang = await db.get_lang(user_id)

    # Check for deep link parameters
    if m.text and len(m.text.split()) > 1:
        param = m.text.split()[1]

        # Handle donate_<track_id>
        if param.startswith("donate_"):
            track_id = param.replace("donate_", "")
            track = await db.get_track(track_id)
            if not track:
                await m.answer(t("track_not_found", lang))
                return

            # Unpack track info
            _, artist_id, track_title, genre, _, _, _, _, status = track

            if status != "ACTIVE":
                await m.answer(t("track_inactive", lang))
                return

            # Get artist info
            artist = await db.get_artist(artist_id)
            if not artist:
                await m.answer(t("artist_not_found", lang))
                return

            artist_name = artist[2]

            # Import keyboard and text functions
            from sado_music_bot.keyboards import kb_donation_amounts
            from sado_music_bot.texts import donation_start_text

            # Show donation amount selection
            await m.answer(
                donation_start_text(track_title, artist_name),
                reply_markup=kb_donation_amounts(track_id)
            )
            return

        # Handle artist_<artist_id>
        elif param.startswith("artist_"):
            artist_id = param.replace("artist_", "")
            artist = await db.get_artist(artist_id)
            if not artist:
                await m.answer(t("artist_not_found", lang))
                return

            # Unpack artist info
            _, _, artist_name, _, _, _, bio = artist

            # Get tracks
            total_tracks = await db.count_artist_tracks(artist_id)
            tracks = await db.list_artist_tracks_with_file(artist_id, limit=10)

            from sado_music_bot.keyboards import kb_track_support
            from sado_music_bot.texts import artist_profile_text

            # Show artist profile
            tracks_list = [(tr[1], tr[2], tr[0]) for tr in tracks]  # (title, genre, track_id)
            profile_text = artist_profile_text(artist_name, bio, total_tracks, tracks_list)

            await m.answer(profile_text)

            # Send each track with support button
            for track in tracks[:5]:  # Limit to 5 tracks to avoid spam
                track_id, title, genre, file_id, _ = track
                if file_id:
                    try:
                        await m.answer_audio(
                            audio=file_id,
                            caption=f"🎵 <b>{title}</b>\n🎧 {genre}",
                            reply_markup=kb_track_support(track_id)
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send track audio {track_id}: {e}")

            return

    # Default /start behavior
    artist = await db.get_artist_by_tg(user_id)

    if artist:
        await m.answer(t("welcome_back", lang))
    else:
        await m.answer(t("welcome_new", lang), reply_markup=kb_lang())


@router.callback_query(F.data.startswith("lang:"))
async def on_lang_choice(cb: CallbackQuery, db: DB):
    if not cb.from_user or not cb.data:
        return

    lang = cb.data.split(":")[1]
    if lang not in ("uz", "ru"):
        await cb.answer(t("invalid_language", "uz"))
        return

    await db.set_lang(cb.from_user.id, lang)
    await cb.message.edit_text(t("language_saved", lang))
    await cb.answer()


# =====================
# /chatid (utility)
# =====================
@router.message(Command("chatid"))
async def cmd_chatid(m: Message):
    """Get chat ID - useful for configuring channels"""
    if m.chat:
        await m.answer(f"Chat ID: <code>{m.chat.id}</code>")


# =====================
# /language
# =====================
@router.message(Command("language"))
async def cmd_language(m: Message, db: DB):
    """Change language preference"""
    if not m.from_user:
        return
    lang = await db.get_lang(m.from_user.id)
    await m.answer(t("select_language", lang), reply_markup=kb_lang())


# =====================
# /profile
# =====================
@router.message(Command("profile"))
async def cmd_profile(m: Message, db: DB):
    if not m.from_user:
        return

    lang = await db.get_lang(m.from_user.id)
    artist = await db.get_artist_by_tg(m.from_user.id)
    if not artist:
        await m.answer(t("no_profile", lang))
        return

    artist_id, tg_user_id, display_name, payment_link, profile_url, default_genre, bio = artist
    tracks = await db.list_artist_tracks(artist_id, limit=5)
    tracks_text = "\n".join([f"• {tr[1]} ({tr[2]})" for tr in tracks]) or "No tracks yet"

    profile_text = (
        f"🎤 <b>{display_name}</b>\n"
        f"💳 Payment: {payment_link or '—'}\n"
        f"🎧 Default genre: {default_genre or '—'}\n"
        f"📝 Bio: {bio or '—'}\n\n"
        f"🎵 <b>Recent tracks:</b>\n{tracks_text}"
    )

    await m.answer(profile_text, reply_markup=kb_profile_actions())


@router.callback_query(F.data.startswith("profile:edit:"))
async def on_profile_edit(cb: CallbackQuery, db: DB, state: FSMContext):
    if not cb.from_user or not cb.data:
        return

    lang = await db.get_lang(cb.from_user.id)
    artist = await db.get_artist_by_tg(cb.from_user.id)
    if not artist:
        await cb.message.edit_text(t("no_profile", lang))
        await cb.answer()
        return

    field = cb.data.split(":")[2]
    await state.update_data(edit_artist_id=artist[0], edit_field=field)

    if field == "default_genre":
        await cb.message.edit_text(t("choose_genre", lang), reply_markup=kb_genres("profilegenre"))
        await state.set_state(ProfileEditStates.waiting_value)
    else:
        prompts = {
            "display_name": t("edit_name_prompt", lang),
            "payment_link": t("edit_payment_prompt", lang),
            "bio": t("edit_bio_prompt", lang),
        }
        await cb.message.edit_text(prompts.get(field, "Send new value:"))
        await state.set_state(ProfileEditStates.waiting_value)

    await cb.answer()


@router.callback_query(F.data.startswith("profilegenre:"))
async def on_profile_genre_choice(cb: CallbackQuery, db: DB, state: FSMContext):
    if not cb.data:
        return

    lang = await db.get_lang(cb.from_user.id) if cb.from_user else "uz"
    choice = cb.data.split(":")[1]
    if choice == "CANCEL":
        await cb.message.edit_text(t("cancelled", lang))
        await state.clear()
        await cb.answer()
        return

    data = await state.get_data()
    artist_id = data.get("edit_artist_id")
    if not artist_id:
        await cb.message.edit_text(t("session_expired", lang))
        await state.clear()
        await cb.answer()
        return

    await db.update_artist_field(artist_id, "default_genre", choice)
    await cb.message.edit_text(f"✅ Default genre updated to: {choice}")
    await state.clear()
    await cb.answer()


@router.message(ProfileEditStates.waiting_value, F.text)
async def on_profile_edit_text(m: Message, db: DB, state: FSMContext):
    if m.text and m.text.startswith("/"):
        return

    lang = await db.get_lang(m.from_user.id) if m.from_user else "uz"
    data = await state.get_data()
    artist_id = data.get("edit_artist_id")
    field = data.get("edit_field")
    if not artist_id or not field:
        await m.answer(t("session_expired", lang))
        await state.clear()
        return
    val = m.text.strip()
    if field == "bio" and val == "-":
        val = None
    await db.update_artist_field(artist_id, field, val if val else None)
    await m.answer(t("updated", lang))
    await state.clear()


# =====================
# /submit
# =====================
@router.message(Command("submit"))
async def cmd_submit(m: Message, db: DB, state: FSMContext):
    if not m.from_user:
        return

    lang = await db.get_lang(m.from_user.id)
    artist = await db.get_artist_by_tg(m.from_user.id)
    if not artist:
        # Start onboarding for new artists
        await m.answer(t("onboard_start", lang))
        await state.set_state(OnboardingStates.waiting_name)
        return

    # Existing artist - go straight to audio upload
    artist_id, _, display_name, _, _, default_genre, _ = artist
    await m.answer(t("uploading_as", lang, name=display_name))
    await state.update_data(artist_id=artist_id, default_genre=default_genre)
    await state.set_state(SubmitStates.waiting_audio)


# =====================
# Onboarding flow
# =====================
@router.message(OnboardingStates.waiting_name)
async def onboard_name(m: Message, db: DB, state: FSMContext):
    if not m.text:
        return
    if m.text.startswith("/"):
        return

    lang = await db.get_lang(m.from_user.id) if m.from_user else "uz"
    name = m.text.strip()
    if len(name) < 2:
        await m.answer(t("name_too_short", lang))
        return
    await state.update_data(onb_name=name)
    await m.answer(t("payment_prompt", lang))
    await state.set_state(OnboardingStates.waiting_payment_link)


@router.message(OnboardingStates.waiting_payment_link)
async def onboard_paylink(m: Message, db: DB, state: FSMContext):
    if not m.text:
        return
    if m.text.startswith("/"):
        return

    lang = await db.get_lang(m.from_user.id) if m.from_user else "uz"
    link = m.text.strip()
    if not (link.startswith("http://") or link.startswith("https://")):
        await m.answer(t("invalid_url", lang))
        return
    await state.update_data(onb_paylink=link)
    await m.answer(t("genre_prompt", lang), reply_markup=kb_genres("onbgenre"))
    await state.set_state(OnboardingStates.waiting_genre)


@router.callback_query(F.data.startswith("onbgenre:"))
async def onboard_genre_choice(cb: CallbackQuery, db: DB, state: FSMContext):
    if not cb.data:
        return

    lang = await db.get_lang(cb.from_user.id) if cb.from_user else "uz"
    choice = cb.data.split(":")[1]
    if choice == "CANCEL":
        await cb.message.edit_text(t("cancelled", lang))
        await state.clear()
        await cb.answer()
        return

    await state.update_data(onb_default_genre=choice)
    await cb.message.edit_text(t("bio_prompt", lang))
    await state.set_state(OnboardingStates.waiting_bio)
    await cb.answer()


@router.message(OnboardingStates.waiting_bio)
async def onboard_bio(m: Message, db: DB, state: FSMContext):
    if not m.text:
        return
    if m.text.startswith("/"):
        return
    if not m.from_user:
        return

    lang = await db.get_lang(m.from_user.id)
    bio = m.text.strip()
    if bio == "-":
        bio = None
    data = await state.get_data()
    name = data.get("onb_name")
    link = data.get("onb_paylink")
    default_genre = data.get("onb_default_genre")
    artist_id = "art_" + uuid.uuid4().hex[:10]
    await db.upsert_artist(
        artist_id=artist_id,
        tg_user_id=m.from_user.id,
        display_name=name,
        payment_link=link,
        profile_url=None,
        default_genre=default_genre,
        bio=bio
    )
    await state.clear()
    await state.update_data(artist_id=artist_id, default_genre=default_genre)
    await m.answer(t("profile_created", lang))
    await state.set_state(SubmitStates.waiting_audio)


# =====================
# Track submission flow
# =====================
@router.message(SubmitStates.waiting_audio, F.audio)
async def sub_audio(m: Message, db: DB, state: FSMContext):
    lang = await db.get_lang(m.from_user.id) if m.from_user else "uz"
    await state.update_data(file_id=m.audio.file_id)
    await m.answer(t("send_title", lang))
    await state.set_state(SubmitStates.waiting_title)


@router.message(SubmitStates.waiting_title, F.text)
async def sub_title(m: Message, db: DB, state: FSMContext):
    if m.text and m.text.startswith("/"):
        return

    lang = await db.get_lang(m.from_user.id) if m.from_user else "uz"
    title = m.text.strip()
    if len(title) < 2:
        await m.answer(t("title_too_short", lang))
        return

    await state.update_data(title=title)
    data = await state.get_data()
    default_genre = data.get("default_genre")

    if default_genre:
        await m.answer(t("choose_genre_default", lang, genre=default_genre), reply_markup=kb_genres("subgenre"))
    else:
        await m.answer(t("choose_genre", lang), reply_markup=kb_genres("subgenre"))

    await state.set_state(SubmitStates.waiting_genre)


@router.callback_query(F.data.startswith("subgenre:"))
async def sub_genre_choice(cb: CallbackQuery, db: DB, state: FSMContext):
    if not cb.data:
        return

    lang = await db.get_lang(cb.from_user.id) if cb.from_user else "uz"
    choice = cb.data.split(":")[1]
    if choice == "CANCEL":
        await cb.message.edit_text(t("cancelled", lang))
        await state.clear()
        await cb.answer()
        return

    await state.update_data(genre=choice)
    await cb.message.edit_text(t("caption_prompt", lang))
    await state.set_state(SubmitStates.waiting_caption)
    await cb.answer()


@router.message(SubmitStates.waiting_caption, F.text)
async def sub_caption(m: Message, bot: Bot, cfg: Config, db: DB, state: FSMContext):
    if m.text and m.text.startswith("/"):
        return
    if not m.from_user:
        return

    lang = await db.get_lang(m.from_user.id)
    caption = m.text.strip()
    if caption == "-":
        caption = None

    data = await state.get_data()
    artist_id = data.get("artist_id")
    file_id = data.get("file_id")
    title = data.get("title")
    genre = data.get("genre")

    if not all([artist_id, file_id, title, genre]):
        await m.answer(t("something_wrong", lang))
        await state.clear()
        return

    artist = await db.get_artist(artist_id)
    if not artist:
        await m.answer(t("something_wrong", lang))
        await state.clear()
        return

    _, _, artist_name, payment_link, _, _, _ = artist

    # Create submission for admin review
    submission_id = "sub_" + uuid.uuid4().hex[:10]

    try:
        await db.create_submission(
            submission_id=submission_id,
            artist_id=artist_id,
            submitter_user_id=m.from_user.id,
            title=title,
            genre=genre,
            caption=caption,
            telegram_file_id=file_id
        )

        # Send to admin for review
        review_caption = (
            f"🎵 <b>New Submission</b>\n\n"
            f"<b>Title:</b> {title}\n"
            f"<b>Artist:</b> {artist_name}\n"
            f"<b>Genre:</b> {genre}\n"
        )
        if caption:
            review_caption += f"<b>Caption:</b> {caption}\n"
        if payment_link:
            review_caption += f"<b>Payment:</b> {payment_link}\n"
        review_caption += f"\n<code>ID: {submission_id}</code>"

        try:
            admin_msg = await bot.send_audio(
                chat_id=cfg.admin_id,
                audio=file_id,
                caption=review_caption,
                reply_markup=kb_admin_review(submission_id)
            )
            await db.set_submission_admin_message(submission_id, admin_msg.message_id)
            print(f"[INFO] Sent submission {submission_id} to admin")
        except Exception as e:
            print(f"[ERROR] Failed to send to admin: {e}")

        await m.answer(t("submission_received", lang, title=title, id=submission_id))

    except Exception as e:
        print(f"[ERROR] Failed to create submission: {e}")
        await m.answer(t("submission_failed", lang, error=str(e)))

    await state.clear()


# =====================
# /cancel
# =====================
@router.message(Command("cancel"))
async def cmd_cancel(m: Message, db: DB, state: FSMContext):
    if not m.from_user:
        return
    lang = await db.get_lang(m.from_user.id)
    current = await state.get_state()
    await state.clear()
    if current:
        await m.answer(t("cancelled", lang))
    else:
        await m.answer(t("nothing_to_cancel", lang))
    return


# =====================
# Help/fallback
# =====================
@router.message(Command("help"))
async def cmd_help(m: Message, db: DB):
    if not m.from_user:
        return
    lang = await db.get_lang(m.from_user.id)
    await m.answer(t("help_text", lang))

