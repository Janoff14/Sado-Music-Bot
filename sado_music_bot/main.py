# Sado Music Bot - Aiogram v3 entry point
import asyncio
from sado_music_bot.config import load_config, Config
from sado_music_bot.db import DB
from sado_music_bot.music.handlers import router as music_router
from sado_music_bot.donations.handlers import router as donations_router
from sado_music_bot.admin.handlers import router as admin_router
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
import os
import psycopg2
import traceback

SCHEMA_SQL = """
BEGIN;
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
COMMIT;
"""

def init_db():
    print("INIT_DB: starting")
    db_url = os.environ["DATABASE_URL"]
    print("INIT_DB: got DATABASE_URL (len=%d)" % len(db_url))
    try:
        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cur:
                print("INIT_DB: executing schema")
                cur.execute(SCHEMA_SQL)
            conn.commit()
        print("INIT_DB: done OK")
    except Exception as e:
        print("INIT_DB: FAILED:", repr(e))
        traceback.print_exc()

async def main():
    cfg: Config = load_config()
    db = DB(cfg.db_path)
    await db.init()
    bot = Bot(token=cfg.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    if not cfg.bot_username:
        me = await bot.get_me()
        bot_username = me.username or "bot"
        from dataclasses import replace
        cfg = replace(cfg, bot_username=bot_username)
    else:
        bot_username = cfg.bot_username
    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(donations_router)
    dp.include_router(music_router)
    print("=" * 50)
    print(f"🎵 {cfg.app_name} Bot starting...")
    print(f"   Bot username: @{bot_username}")
    print(f"   Admin ID: {cfg.admin_id}")
    print(f"   Database: {cfg.db_path}")
    print(f"   Max donations/hour: {cfg.max_donations_per_hour}")
    print()
    print("Channels configured:")
    print(f"   Pop: {cfg.channel_pop or '(not set)'}")
    print(f"   Rock: {cfg.channel_rock or '(not set)'}")
    print(f"   Hip Hop: {cfg.channel_hiphop or '(not set)'}")
    print(f"   Discovery: {cfg.channel_discovery or '(not set)'}")
    print()
    print("Discussion groups:")
    print(f"   Pop: {cfg.discussion_pop or '(not set)'}")
    print(f"   Rock: {cfg.discussion_rock or '(not set)'}")
    print(f"   Hip Hop: {cfg.discussion_hiphop or '(not set)'}")
    print(f"   Discovery: {cfg.discussion_discovery or '(not set)'}")
    print("=" * 50)
    await dp.start_polling(bot, cfg=cfg, db=db)

if __name__ == "__main__":
    asyncio.run(main())
