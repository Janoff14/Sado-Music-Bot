# sado_music_bot/i18n/__init__.py
"""
Internationalization module - text strings only, no flow changes.
All texts use HTML formatting (not MarkdownV2).
"""

from typing import Dict, Optional

# Uzbek translations
UZ: Dict[str, str] = {
    # Start & Welcome
    "welcome_back": "✅ Xush kelibsiz!\n\n• /submit — yangi trek yuklash\n• /profile — profilingizni ko'rish/tahrirlash\n• /language — tilni o'zgartirish\n• /cancel — bekor qilish",
    "welcome_new": "🎵 <b>Sado Music</b>ga xush kelibsiz!\n\nMusiqangizni dunyo bilan baham ko'ring.\n\nTilni tanlang / Выберите язык:",
    "select_language": "🌐 Tilni tanlang / Выберите язык:",
    "language_saved": "✅ Til saqlandi!\n\nBirinchi trekingizni yuklash uchun /submit bosing.",

    # Errors
    "track_not_found": "❌ Trek topilmadi.",
    "artist_not_found": "❌ Ijrochi topilmadi.",
    "track_inactive": "❌ Trek endi faol emas.",
    "invalid_language": "Noto'g'ri til",

    # Profile
    "no_profile": "Profil topilmadi. Avval /submit bosing.",
    "profile_header": "🎤 <b>{name}</b>",
    "session_expired": "Sessiya tugadi. Qaytadan urinib ko'ring.",
    "updated": "✅ Yangilandi!",

    # Profile editing
    "edit_name_prompt": "Yangi ijrochi ismingizni yuboring:",
    "edit_payment_prompt": "Yangi to'lov havolasini yuboring (Click/Payme URL):",
    "edit_bio_prompt": "Yangi bio yuboring ('-' tozalash uchun):",
    "choose_genre": "Janrni tanlang:",

    # Onboarding
    "onboard_start": "🎤 <b>Profil yaratish</b>\n\nIjrochi/sahna ismingizni yuboring:",
    "name_too_short": "Ism juda qisqa. Qaytadan urinib ko'ring:",
    "payment_prompt": "To'lov havolasini yuboring (Click/Payme URL):\n\n<i>Muxlislar shu yerga pul yuboradi.</i>",
    "invalid_url": "Iltimos, http:// yoki https:// bilan boshlanadigan havola yuboring",
    "genre_prompt": "Standart janringizni tanlang:",
    "bio_prompt": "Ixtiyoriy: qisqa bio yuboring (1-2 qator), yoki '-' o'tkazib yuborish uchun.",
    "profile_created": "✅ Profil yaratildi!\n\nEndi audio faylingizni yuboring (Musiqa/Audio format).",

    # Submission
    "uploading_as": "Yuklanyapti: <b>{name}</b>\n\nAudio faylingizni yuboring (Musiqa/Audio format).",
    "send_title": "Trek nomini yuboring:",
    "title_too_short": "Nom juda qisqa. Qaytadan urinib ko'ring:",
    "choose_genre_default": "Janrni tanlang (standart: {genre}):",
    "caption_prompt": "Ixtiyoriy: qisqa tavsif yuboring, yoki '-' o'tkazib yuborish uchun.",
    "submission_received": "✅ <b>Trek qabul qilindi!</b>\n\n<b>{title}</b> trekingiz ko'rib chiqish uchun yuborildi.\nTasdiqlangach xabar beramiz.\n\nYuborish ID: <code>{id}</code>",
    "submission_failed": "❌ Yuborishda xatolik: {error}",
    "something_wrong": "Xatolik yuz berdi. /submit qaytadan bosing.",

    # Submitter notifications
    "submitter_approved": "✅ <b>{title}</b> trekingiz tasdiqlandi va joylandi!",
    "submitter_rejected": "❌ <b>{title}</b> trekingiz tasdiqlanmadi.\n\nIltimos, qoidalarga rioya qiling va qaytadan urinib ko'ring.",

    # Cancel & Help
    "cancelled": "Bekor qilindi.",
    "nothing_to_cancel": "Bekor qiladigan narsa yo'q.",
    "help_text": "🎵 <b>Sado Music Bot</b>\n\n<b>Buyruqlar:</b>\n• /start — Botni ishga tushirish\n• /submit — Yangi trek yuborish\n• /profile — Ijrochi profilini ko'rish/tahrirlash\n• /language — Tilni o'zgartirish\n• /cancel — Joriy amalni bekor qilish\n• /chatid — Joriy chat ID ni olish\n\n<i>Donation tugmalari hozircha Demo rejimida.</i>",
}

# Russian translations
RU: Dict[str, str] = {
    # Start & Welcome
    "welcome_back": "✅ С возвращением!\n\n• /submit — загрузить новый трек\n• /profile — просмотр/редактирование профиля\n• /language — сменить язык\n• /cancel — отмена",
    "welcome_new": "🎵 Добро пожаловать в <b>Sado Music</b>!\n\nДелитесь своей музыкой с миром.\n\nTilni tanlang / Выберите язык:",
    "select_language": "🌐 Tilni tanlang / Выберите язык:",
    "language_saved": "✅ Язык сохранён!\n\nНажмите /submit чтобы загрузить первый трек.",

    # Errors
    "track_not_found": "❌ Трек не найден.",
    "artist_not_found": "❌ Артист не найден.",
    "track_inactive": "❌ Трек больше не активен.",
    "invalid_language": "Неверный язык",

    # Profile
    "no_profile": "Профиль не найден. Сначала нажмите /submit.",
    "profile_header": "🎤 <b>{name}</b>",
    "session_expired": "Сессия истекла. Попробуйте снова.",
    "updated": "✅ Обновлено!",

    # Profile editing
    "edit_name_prompt": "Отправьте новое имя артиста:",
    "edit_payment_prompt": "Отправьте новую ссылку для оплаты (Click/Payme URL):",
    "edit_bio_prompt": "Отправьте новое био ('-' чтобы очистить):",
    "choose_genre": "Выберите жанр:",

    # Onboarding
    "onboard_start": "🎤 <b>Создание профиля</b>\n\nОтправьте ваше сценическое имя:",
    "name_too_short": "Имя слишком короткое. Попробуйте ещё:",
    "payment_prompt": "Отправьте ссылку для оплаты (Click/Payme URL):\n\n<i>Сюда фанаты будут отправлять донаты.</i>",
    "invalid_url": "Пожалуйста, отправьте ссылку начинающуюся с http:// или https://",
    "genre_prompt": "Выберите жанр по умолчанию:",
    "bio_prompt": "Опционально: отправьте короткое био (1-2 строки), или '-' чтобы пропустить.",
    "profile_created": "✅ Профиль создан!\n\nТеперь отправьте аудиофайл (формат Музыка/Аудио).",

    # Submission
    "uploading_as": "Загрузка от: <b>{name}</b>\n\nОтправьте аудиофайл (формат Музыка/Аудио).",
    "send_title": "Отправьте название трека:",
    "title_too_short": "Название слишком короткое. Ещё раз:",
    "choose_genre_default": "Выберите жанр (по умолчанию: {genre}):",
    "caption_prompt": "Опционально: отправьте короткое описание, или '-' чтобы пропустить.",
    "submission_received": "✅ <b>Трек получен!</b>\n\nВаш трек <b>{title}</b> отправлен на модерацию.\nВы получите уведомление после одобрения.\n\nID отправки: <code>{id}</code>",
    "submission_failed": "❌ Ошибка отправки: {error}",
    "something_wrong": "Что-то пошло не так. Нажмите /submit снова.",

    # Submitter notifications
    "submitter_approved": "✅ Ваш трек <b>{title}</b> одобрен и опубликован!",
    "submitter_rejected": "❌ Ваш трек <b>{title}</b> не был одобрен.\n\nПожалуйста, убедитесь что отправка соответствует правилам и попробуйте снова.",

    # Cancel & Help
    "cancelled": "Отменено.",
    "nothing_to_cancel": "Нечего отменять.",
    "help_text": "🎵 <b>Sado Music Bot</b>\n\n<b>Команды:</b>\n• /start — Запустить бота\n• /submit — Загрузить новый трек\n• /profile — Просмотр/редактирование профиля\n• /language — Сменить язык\n• /cancel — Отменить текущую операцию\n• /chatid — Получить ID чата\n\n<i>Кнопки донатов пока в демо-режиме.</i>",
}

# All languages
LANGUAGES: Dict[str, Dict[str, str]] = {
    "uz": UZ,
    "ru": RU,
}

DEFAULT_LANGUAGE = "uz"
CHANNEL_LANGUAGE = "uz"  # Always Uzbek for channel posts


def t(key: str, lang: Optional[str] = None, **kwargs) -> str:
    """
    Get translated text for the given key and language.

    Args:
        key: The translation key
        lang: Language code ('uz' or 'ru'). Defaults to Uzbek.
        **kwargs: Format arguments for the string

    Returns:
        Translated string or the key itself if not found.
    """
    if lang is None or lang not in LANGUAGES:
        lang = DEFAULT_LANGUAGE

    text = LANGUAGES[lang].get(key)
    if text is None:
        # Fallback to default language
        text = LANGUAGES[DEFAULT_LANGUAGE].get(key, key)

    # Apply format arguments if provided
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text


def t_channel(key: str, **kwargs) -> str:
    """Get text for channel posts (always Uzbek)."""
    return t(key, CHANNEL_LANGUAGE, **kwargs)


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

