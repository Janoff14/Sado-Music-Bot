"""
Database module for Sado Music Bot
Uses aiosqlite for async SQLite operations
"""
import time
import uuid
from typing import Optional, Tuple, List

import aiosqlite


class DB:
    def __init__(self, path: str):
        self.path = path

    async def init(self) -> None:
        """Initialize database tables"""
        async with aiosqlite.connect(self.path) as db:
            # User settings (language, anonymous default)
            await db.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                lang TEXT DEFAULT 'uz',
                anonymous_default INTEGER NOT NULL DEFAULT 0
            )
            """)

            # Artists (creators who submit music)
            await db.execute("""
            CREATE TABLE IF NOT EXISTS artists (
                artist_id TEXT PRIMARY KEY,
                tg_user_id INTEGER NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                payment_link TEXT,
                profile_url TEXT,
                default_genre TEXT,
                bio TEXT,
                created_at INTEGER NOT NULL
            )
            """)

            # Submissions (pending admin review)
            await db.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                submission_id TEXT PRIMARY KEY,
                artist_id TEXT NOT NULL,
                submitter_user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                genre TEXT NOT NULL,
                caption TEXT,
                telegram_file_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                admin_message_id INTEGER,
                created_at INTEGER NOT NULL,
                reviewed_at INTEGER
            )
            """)

            # Tracks (approved and posted)
            await db.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                track_id TEXT PRIMARY KEY,
                artist_id TEXT NOT NULL,
                title TEXT NOT NULL,
                genre TEXT NOT NULL,
                caption TEXT,
                telegram_file_id TEXT,
                channel_message_id INTEGER NOT NULL,
                discussion_anchor_message_id INTEGER DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at INTEGER NOT NULL
            )
            """)

            # Donations
            await db.execute("""
            CREATE TABLE IF NOT EXISTS donation_events (
                donation_id TEXT PRIMARY KEY,
                track_id TEXT NOT NULL,
                artist_id TEXT NOT NULL,
                donor_user_id INTEGER,
                donor_name TEXT,
                donor_username TEXT,
                amount INTEGER NOT NULL,
                note TEXT,
                is_anonymous INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                confirmed_at INTEGER
            )
            """)

            await db.commit()
            print("[DB] Tables initialized")

    # =====================
    # User Settings
    # =====================
    async def get_lang(self, user_id: int) -> str:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("SELECT lang FROM user_settings WHERE user_id=?", (user_id,))
            row = await cur.fetchone()
            return row[0] if row else "uz"

    async def set_lang(self, user_id: int, lang: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
            INSERT INTO user_settings(user_id, lang, anonymous_default)
            VALUES(?, ?, 0)
            ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang
            """, (user_id, lang))
            await db.commit()

    async def get_anon_default(self, user_id: int) -> int:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("SELECT anonymous_default FROM user_settings WHERE user_id=?", (user_id,))
            row = await cur.fetchone()
            return int(row[0]) if row else 0

    async def set_anon_default(self, user_id: int, val: int) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
            INSERT INTO user_settings(user_id, lang, anonymous_default)
            VALUES(?, 'uz', ?)
            ON CONFLICT(user_id) DO UPDATE SET anonymous_default=excluded.anonymous_default
            """, (user_id, int(val)))
            await db.commit()

    # =====================
    # Artists
    # =====================
    async def upsert_artist(
        self,
        artist_id: str,
        tg_user_id: int,
        display_name: str,
        payment_link: Optional[str] = None,
        profile_url: Optional[str] = None,
        default_genre: Optional[str] = None,
        bio: Optional[str] = None
    ) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
            INSERT INTO artists(artist_id, tg_user_id, display_name, payment_link, profile_url, default_genre, bio, created_at)
            VALUES(?,?,?,?,?,?,?,?)
            ON CONFLICT(artist_id) DO UPDATE SET
                tg_user_id=excluded.tg_user_id,
                display_name=excluded.display_name,
                payment_link=excluded.payment_link,
                profile_url=excluded.profile_url,
                default_genre=excluded.default_genre,
                bio=excluded.bio
            """, (artist_id, tg_user_id, display_name, payment_link, profile_url, default_genre, bio, int(time.time())))
            await db.commit()

    async def get_artist(self, artist_id: str) -> Optional[Tuple]:
        """Returns: (artist_id, tg_user_id, display_name, payment_link, profile_url, default_genre, bio)"""
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("""
            SELECT artist_id, tg_user_id, display_name, payment_link, profile_url, default_genre, bio
            FROM artists WHERE artist_id=?
            """, (artist_id,))
            return await cur.fetchone()

    async def get_artist_by_tg(self, tg_user_id: int) -> Optional[Tuple]:
        """Returns: (artist_id, tg_user_id, display_name, payment_link, profile_url, default_genre, bio)"""
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("""
            SELECT artist_id, tg_user_id, display_name, payment_link, profile_url, default_genre, bio
            FROM artists WHERE tg_user_id=?
            """, (tg_user_id,))
            return await cur.fetchone()

    async def update_artist_field(self, artist_id: str, field: str, value: Optional[str]) -> None:
        allowed = {"display_name", "payment_link", "profile_url", "default_genre", "bio"}
        if field not in allowed:
            raise ValueError(f"Invalid field: {field}")
        async with aiosqlite.connect(self.path) as db:
            await db.execute(f"UPDATE artists SET {field}=? WHERE artist_id=?", (value, artist_id))
            await db.commit()

    # =====================
    # Submissions
    # =====================
    async def create_submission(
        self,
        submission_id: str,
        artist_id: str,
        submitter_user_id: int,
        title: str,
        genre: str,
        caption: Optional[str],
        telegram_file_id: str
    ) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
            INSERT INTO submissions(submission_id, artist_id, submitter_user_id, title, genre, 
                                   caption, telegram_file_id, status, created_at)
            VALUES(?,?,?,?,?,?,?,?,?)
            """, (submission_id, artist_id, submitter_user_id, title, genre,
                  caption, telegram_file_id, "PENDING", int(time.time())))
            await db.commit()

    async def get_submission(self, submission_id: str) -> Optional[Tuple]:
        """Returns: (submission_id, artist_id, submitter_user_id, title, genre, caption,
                     telegram_file_id, status, admin_message_id)"""
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("""
            SELECT submission_id, artist_id, submitter_user_id, title, genre, caption, 
                   telegram_file_id, status, admin_message_id
            FROM submissions WHERE submission_id=?
            """, (submission_id,))
            return await cur.fetchone()

    async def set_submission_admin_message(self, submission_id: str, admin_msg_id: int) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("UPDATE submissions SET admin_message_id=? WHERE submission_id=?",
                           (admin_msg_id, submission_id))
            await db.commit()

    async def set_submission_status(self, submission_id: str, status: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
            UPDATE submissions SET status=?, reviewed_at=? WHERE submission_id=?
            """, (status, int(time.time()), submission_id))
            await db.commit()

    # =====================
    # Tracks
    # =====================
    async def insert_track(
        self,
        track_id: str,
        artist_id: str,
        title: str,
        genre: str,
        caption: Optional[str],
        telegram_file_id: Optional[str],
        channel_msg_id: int,
        discussion_anchor_id: int = 0
    ) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
            INSERT INTO tracks(track_id, artist_id, title, genre, caption, telegram_file_id, 
                               channel_message_id, discussion_anchor_message_id, status, created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """, (track_id, artist_id, title, genre, caption, telegram_file_id,
                  channel_msg_id, discussion_anchor_id, "ACTIVE", int(time.time())))
            await db.commit()

    async def get_track(self, track_id: str) -> Optional[Tuple]:
        """Returns: (track_id, artist_id, title, genre, caption, telegram_file_id,
                     channel_message_id, discussion_anchor_message_id, status)"""
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("""
            SELECT track_id, artist_id, title, genre, caption, telegram_file_id,
                   channel_message_id, discussion_anchor_message_id, status
            FROM tracks WHERE track_id=?
            """, (track_id,))
            return await cur.fetchone()

    async def list_artist_tracks(self, artist_id: str, limit: int = 10) -> List[Tuple]:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("""
            SELECT track_id, title, genre, status, created_at
            FROM tracks
            WHERE artist_id=?
            ORDER BY created_at DESC
            LIMIT ?
            """, (artist_id, limit))
            return await cur.fetchall()

    async def list_artist_tracks_with_file(self, artist_id: str, limit: int = 10) -> List[Tuple]:
        """Returns tracks with file_id for sending audio"""
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("""
            SELECT track_id, title, genre, telegram_file_id, status
            FROM tracks
            WHERE artist_id=? AND status='ACTIVE'
            ORDER BY created_at DESC
            LIMIT ?
            """, (artist_id, limit))
            return await cur.fetchall()

    async def count_artist_tracks(self, artist_id: str) -> int:
        """Count total active tracks for artist"""
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("""
            SELECT COUNT(*) FROM tracks WHERE artist_id=? AND status='ACTIVE'
            """, (artist_id,))
            row = await cur.fetchone()
            return int(row[0] or 0)

    # =====================
    # Donations
    # =====================
    async def create_donation(
        self,
        track_id: str,
        artist_id: str,
        donor_user_id: int,
        donor_name: str,
        donor_username: Optional[str],
        amount: int,
        is_anonymous: int = 0
    ) -> str:
        donation_id = "don_" + uuid.uuid4().hex[:12]
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
            INSERT INTO donation_events(
                donation_id, track_id, artist_id,
                donor_user_id, donor_name, donor_username,
                amount, note, is_anonymous, status, created_at
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """, (
                donation_id, track_id, artist_id,
                donor_user_id, donor_name, donor_username,
                amount, None, int(is_anonymous), "CREATED", int(time.time())
            ))
            await db.commit()
        return donation_id

    async def get_donation(self, donation_id: str) -> Optional[Tuple]:
        """Returns: (donation_id, track_id, artist_id, donor_user_id, donor_name, donor_username,
                     amount, note, is_anonymous, status)"""
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("""
            SELECT donation_id, track_id, artist_id,
                   donor_user_id, donor_name, donor_username,
                   amount, note, is_anonymous, status
            FROM donation_events WHERE donation_id=?
            """, (donation_id,))
            return await cur.fetchone()

    async def set_donation_note(self, donation_id: str, note: Optional[str]) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("UPDATE donation_events SET note=? WHERE donation_id=?", (note, donation_id))
            await db.commit()

    async def toggle_donation_anon(self, donation_id: str) -> int:
        d = await self.get_donation(donation_id)
        if not d:
            raise ValueError("Donation not found")
        current = int(d[8])  # is_anonymous index
        new_val = 0 if current == 1 else 1
        async with aiosqlite.connect(self.path) as db:
            await db.execute("UPDATE donation_events SET is_anonymous=? WHERE donation_id=?", (new_val, donation_id))
            await db.commit()
        return new_val

    async def set_donation_status(self, donation_id: str, status: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            if status == "CONFIRMED":
                await db.execute("""
                UPDATE donation_events SET status=?, confirmed_at=? WHERE donation_id=?
                """, (status, int(time.time()), donation_id))
            else:
                await db.execute("UPDATE donation_events SET status=? WHERE donation_id=?", (status, donation_id))
            await db.commit()

    async def count_recent_confirmed(self, donor_user_id: int, track_id: str, window_seconds: int = 3600) -> int:
        cutoff = int(time.time()) - window_seconds
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("""
            SELECT COUNT(*) FROM donation_events
            WHERE donor_user_id=? AND track_id=? AND status='CONFIRMED' 
              AND confirmed_at IS NOT NULL AND confirmed_at>=?
            """, (donor_user_id, track_id, cutoff))
            row = await cur.fetchone()
            return int(row[0] or 0)

