"""
Configuration module for Sado Music Bot
Loads settings from environment variables / .env file
"""
import logging
import os
from dataclasses import dataclass
from typing import Union
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class Config:
    bot_token: str
    admin_id: int
    bot_username: str = ""
    app_name: str = "Sado Music"
    max_donations_per_hour: int = 5

    # Genre channels (where tracks get posted)
    channel_pop: str = ""
    channel_rock: str = ""
    channel_hiphop: str = ""
    channel_discovery: str = ""

    # Discussion groups (for comments/appreciation posts)
    discussion_pop: str = ""
    discussion_rock: str = ""
    discussion_hiphop: str = ""
    discussion_discovery: str = ""

    @property
    def db_path(self):
        # Use DATABASE_URL for Postgres
        return os.getenv("DATABASE_URL")


def _parse_chat_id(val: str) -> Union[int, str]:
    """Parse chat ID - return int if numeric, else string (for @usernames)"""
    val = val.strip()
    if not val:
        return 0
    try:
        return int(val)
    except ValueError:
        return val  # It's a @username


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is missing")

    admin_id = int(os.getenv("ADMIN_ID", "0"))
    if admin_id == 0:
        raise RuntimeError("ADMIN_ID is missing")

    bot_username = os.getenv("BOT_USERNAME", "").strip()
    if not bot_username:
        logger.warning("BOT_USERNAME not set in .env - deep links may not work until bot starts")

    return Config(
        bot_token=bot_token,
        admin_id=admin_id,
        bot_username=os.getenv("BOT_USERNAME", ""),
        app_name=os.getenv("APP_NAME", "Sado Music"),
        max_donations_per_hour=int(os.getenv("MAX_DONATIONS_PER_HOUR", "5")),
        # Genre channels
        channel_pop=os.getenv("CHANNEL_POP", ""),
        channel_rock=os.getenv("CHANNEL_ROCK", ""),
        channel_hiphop=os.getenv("CHANNEL_HIPHOP", ""),
        channel_discovery=os.getenv("CHANNEL_DISCOVERY", ""),
        # Discussion groups
        discussion_pop=os.getenv("DISCUSSION_POP", ""),
        discussion_rock=os.getenv("DISCUSSION_ROCK", ""),
        discussion_hiphop=os.getenv("DISCUSSION_HIPHOP", ""),
        discussion_discovery=os.getenv("DISCUSSION_DISCOVERY", ""),
    )


# Genre -> channel attribute mapping
GENRE_CHANNELS = {
    "Pop": "channel_pop",
    "Rock": "channel_rock",
    "Hip Hop": "channel_hiphop",
    "Rap": "channel_hiphop",
    "Indie": "channel_discovery",
    "Electronic": "channel_discovery",
    "Other": "channel_discovery",
}

GENRE_DISCUSSIONS = {
    "Pop": "discussion_pop",
    "Rock": "discussion_rock",
    "Hip Hop": "discussion_hiphop",
    "Rap": "discussion_hiphop",
    "Indie": "discussion_discovery",
    "Electronic": "discussion_discovery",
    "Other": "discussion_discovery",
}


def get_channel_for_genre(cfg: Config, genre: str) -> Union[int, str]:
    """Get channel ID/username for a genre. Returns 0 if not configured."""
    attr = GENRE_CHANNELS.get(genre, "channel_discovery")
    val = getattr(cfg, attr, "")
    return _parse_chat_id(val) if val else 0


def get_discussion_for_genre(cfg: Config, genre: str) -> Union[int, str]:
    """Get discussion group ID/username for a genre. Returns 0 if not configured."""
    attr = GENRE_DISCUSSIONS.get(genre, "discussion_discovery")
    val = getattr(cfg, attr, "")
    return _parse_chat_id(val) if val else 0
