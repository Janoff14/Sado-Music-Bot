# sado_music_bot/i18n/__init__.py
# Internationalization module for the bot.

from __future__ import annotations

from typing import Dict, Optional

from .uz import UZ
from .ru import RU

# Supported languages
LANGUAGES: Dict[str, Dict[str, str]] = {
    "uz": UZ,
    "ru": RU,
}

DEFAULT_LANGUAGE = "uz"
CHANNEL_LANGUAGE = "uz"  # Always use Uzbek for channel posts


def t(key: str, lang: Optional[str] = None) -> str:
    """
    Get translated text for the given key and language.

    Args:
        key: The translation key
        lang: Language code ('uz' or 'ru'). Defaults to Uzbek.

    Returns:
        Translated string or the key itself if not found.
    """
    if lang is None:
        lang = DEFAULT_LANGUAGE

    if lang not in LANGUAGES:
        lang = DEFAULT_LANGUAGE

    return LANGUAGES[lang].get(key, key)


def t_channel(key: str) -> str:
    """
    Get translated text for channel posts (always Uzbek).
    """
    return LANGUAGES[CHANNEL_LANGUAGE].get(key, key)


def get_language_name(lang_code: str) -> str:
    """Get human-readable language name."""
    names = {
        "uz": "🇺🇿 O'zbekcha",
        "ru": "🇷🇺 Русский",
    }
    return names.get(lang_code, lang_code)


def get_available_languages() -> Dict[str, str]:
    """Get dict of available language codes to names."""
    return {
        "uz": "🇺🇿 O'zbekcha",
        "ru": "🇷🇺 Русский",
    }


__all__ = [
    "t",
    "t_channel",
    "LANGUAGES",
    "DEFAULT_LANGUAGE",
    "CHANNEL_LANGUAGE",
    "get_language_name",
    "get_available_languages",
]

