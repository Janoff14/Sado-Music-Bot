# sado_music_bot/i18n/ru.py
# Russian (ru) user-visible strings for bot UI, admin UI, and channel/discussion posts.
# Keep these short, conventional, and consistent across the bot.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class RuTexts:
    # Generic
    unauthorized: str = "У вас нет доступа\\."
    unknown_error: str = "Произошла ошибка\\. Попробуйте ещё раз\\."
    not_found: str = "Не найдено\\."
    cancelled: str = "Отменено\\."
    done: str = "Готово\\."

    # Language selection
    select_language: str = "Tilni tanlang / Выберите язык:"
    language_changed: str = "✅ Язык изменён\\: Русский"

    # Start / welcome
    welcome: str = "Привет\\! Я SadoMusicBot\\. Вы можете загрузить музыку или выполнить другие действия\\."
    help_text: str = "Список команд:\\n/start \\- Запустить бота\\n/help \\- Помощь\\n/language \\- Изменить язык\\n/submit \\- Отправить трек\\n/donate \\- Пожертвовать"

    # Submissions / moderation (admin callbacks)
    submission_not_found: str = "Отправленный трек не найден\\."
    invalid_callback: str = "Некорректный запрос\\."
    already_processed_prefix: str = "Эта отправка уже обработана\\:"
    approved_and_posted: str = "✅ Одобрено и опубликовано в канале\\!"
    rejected: str = "❌ Отклонено\\."
    channel_not_configured: str = "Для этого жанра канал не настроен\\."

    # Messages to submitter
    submitter_approved: str = "✅ Трек одобрен и опубликован в канале\\!"
    submitter_rejected: str = "❌ Трек не одобрен \\(отклонён\\)\\."

    # Music submission flow
    submit_start: str = "Начнём процесс отправки трека\\."
    send_audio: str = "Пожалуйста, отправьте аудиофайл \\(MP3, OGG и т\\.д\\.\\)\\:"
    send_title: str = "Введите название трека\\:"
    send_artist: str = "Введите имя исполнителя\\:"
    select_genre: str = "Выберите жанр\\:"
    send_payment_info: str = "Введите платёжные данные \\(необязательно, /skip чтобы пропустить\\)\\:"
    send_profile_link: str = "Введите ссылку на профиль \\(необязательно, /skip чтобы пропустить\\)\\:"
    submission_preview: str = "Ваша отправка\\:"
    confirm_submission: str = "Подтвердить отправку?"
    submission_sent: str = "✅ Трек отправлен на модерацию\\! Мы сообщим о результате\\."
    submission_cancelled: str = "❌ Отправка отменена\\."

    # Donations flow
    donate_start: str = "Начнём процесс пожертвования\\."
    donate_amount: str = "Введите сумму \\(в сумах\\)\\:"
    donate_payment_method: str = "Выберите способ оплаты\\:"
    donate_instructions: str = "Оплата производится по следующим реквизитам\\:"
    donate_confirm_payment: str = "Вы произвели оплату?"
    donate_thanks: str = "✅ Спасибо\\! Ваше пожертвование принято\\."
    donate_cancelled: str = "❌ Пожертвование отменено\\."

    # Channel post formatting (caption templates)
    # NOTE: Use format_map or f-strings with these keys:
    # {title}, {artist}, {genre}, {pay}, {profile}
    channel_caption_header: str = "🎵 {title}"
    channel_caption_artist_line: str = "👤 Исполнитель: {artist}"
    channel_caption_genre_line: str = "🎧 Жанр: {genre}"
    channel_caption_support_line: str = "💳 Поддержать: {pay}"
    channel_caption_profile_line: str = "🔗 Профиль: {profile}"
    channel_caption_footer: str = "Чтобы оставить комментарий, перейдите в обсуждение\\."

    # Discussion / anchor message
    # {channel_post_url} or {post_id} depending on implementation
    discussion_anchor: str = "💬 Обсуждение здесь\\:"

    # Admin message captions / status tags
    admin_status_pending: str = "⏳ Ожидает"
    admin_status_approved: str = "✅ ОДОБРЕНО"
    admin_status_rejected: str = "❌ ОТКЛОНЕНО"

    # Admin action buttons (if used)
    btn_approve: str = "✅ Одобрить"
    btn_reject: str = "❌ Отклонить"
    btn_confirm: str = "✅ Подтвердить"
    btn_cancel: str = "❌ Отмена"
    btn_skip: str = "⏭ Пропустить"
    btn_back: str = "⬅️ Назад"


RU: Dict[str, str] = {
    # Generic
    "unauthorized": RuTexts.unauthorized,
    "unknown_error": RuTexts.unknown_error,
    "not_found": RuTexts.not_found,
    "cancelled": RuTexts.cancelled,
    "done": RuTexts.done,

    # Language
    "select_language": RuTexts.select_language,
    "language_changed": RuTexts.language_changed,

    # Start / welcome
    "welcome": RuTexts.welcome,
    "help_text": RuTexts.help_text,

    # Submissions / moderation
    "submission_not_found": RuTexts.submission_not_found,
    "invalid_callback": RuTexts.invalid_callback,
    "already_processed_prefix": RuTexts.already_processed_prefix,
    "approved_and_posted": RuTexts.approved_and_posted,
    "rejected": RuTexts.rejected,
    "channel_not_configured": RuTexts.channel_not_configured,

    # Submitter notifications
    "submitter_approved": RuTexts.submitter_approved,
    "submitter_rejected": RuTexts.submitter_rejected,

    # Music submission flow
    "submit_start": RuTexts.submit_start,
    "send_audio": RuTexts.send_audio,
    "send_title": RuTexts.send_title,
    "send_artist": RuTexts.send_artist,
    "select_genre": RuTexts.select_genre,
    "send_payment_info": RuTexts.send_payment_info,
    "send_profile_link": RuTexts.send_profile_link,
    "submission_preview": RuTexts.submission_preview,
    "confirm_submission": RuTexts.confirm_submission,
    "submission_sent": RuTexts.submission_sent,
    "submission_cancelled": RuTexts.submission_cancelled,

    # Donations flow
    "donate_start": RuTexts.donate_start,
    "donate_amount": RuTexts.donate_amount,
    "donate_payment_method": RuTexts.donate_payment_method,
    "donate_instructions": RuTexts.donate_instructions,
    "donate_confirm_payment": RuTexts.donate_confirm_payment,
    "donate_thanks": RuTexts.donate_thanks,
    "donate_cancelled": RuTexts.donate_cancelled,

    # Channel formatting templates
    "channel_caption_header": RuTexts.channel_caption_header,
    "channel_caption_artist_line": RuTexts.channel_caption_artist_line,
    "channel_caption_genre_line": RuTexts.channel_caption_genre_line,
    "channel_caption_support_line": RuTexts.channel_caption_support_line,
    "channel_caption_profile_line": RuTexts.channel_caption_profile_line,
    "channel_caption_footer": RuTexts.channel_caption_footer,

    # Discussion
    "discussion_anchor": RuTexts.discussion_anchor,

    # Admin statuses
    "admin_status_pending": RuTexts.admin_status_pending,
    "admin_status_approved": RuTexts.admin_status_approved,
    "admin_status_rejected": RuTexts.admin_status_rejected,

    # Buttons
    "btn_approve": RuTexts.btn_approve,
    "btn_reject": RuTexts.btn_reject,
    "btn_confirm": RuTexts.btn_confirm,
    "btn_cancel": RuTexts.btn_cancel,
    "btn_skip": RuTexts.btn_skip,
    "btn_back": RuTexts.btn_back,
}


def t(key: str) -> str:
    """
    Simple accessor for Russian texts.
    Usage: t("unauthorized")
    """
    return RU.get(key, key)

