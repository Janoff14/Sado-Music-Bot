# Sado Music Bot - Aiogram v3 entry point
import asyncio
import logging
import sys

from sado_music_bot.config import load_config, Config
from sado_music_bot.db import DB
from sado_music_bot.music.handlers import router as music_router
from sado_music_bot.donations.handlers import router as donations_router
from sado_music_bot.admin.handlers import router as admin_router
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot_output.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

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

    logger.info("=" * 50)
    logger.info(f"🎵 {cfg.app_name} Bot starting...")
    logger.info(f"   Bot username: @{bot_username}")
    logger.info(f"   Admin ID: {cfg.admin_id}")
    logger.info(f"   Database: {cfg.db_path}")
    logger.info(f"   Max donations/hour: {cfg.max_donations_per_hour}")
    logger.info("")
    logger.info("Channels configured:")
    logger.info(f"   Pop: {cfg.channel_pop or '(not set)'}")
    logger.info(f"   Rock: {cfg.channel_rock or '(not set)'}")
    logger.info(f"   Hip Hop: {cfg.channel_hiphop or '(not set)'}")
    logger.info(f"   Discovery: {cfg.channel_discovery or '(not set)'}")
    logger.info("")
    logger.info("Discussion groups:")
    logger.info(f"   Pop: {cfg.discussion_pop or '(not set)'}")
    logger.info(f"   Rock: {cfg.discussion_rock or '(not set)'}")
    logger.info(f"   Hip Hop: {cfg.discussion_hiphop or '(not set)'}")
    logger.info(f"   Discovery: {cfg.discussion_discovery or '(not set)'}")
    logger.info("=" * 50)

    await dp.start_polling(bot, cfg=cfg, db=db)

if __name__ == "__main__":
    asyncio.run(main())
