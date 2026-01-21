# Sado Music Bot - Aiogram v3 entry point
import asyncio
from sado_music_bot.config import load_config, Config
from sado_music_bot.db import DB
from sado_music_bot.music.handlers import router as music_router
from sado_music_bot.donations.handlers import router as donations_router
from sado_music_bot.admin.handlers import router as admin_router
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

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
