# sado_music_bot/i18n/uz.py
# Uzbek (uz) user-visible strings for bot UI, admin UI, and channel/discussion posts.
# Keep these short, conventional, and consistent across the bot.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class UzTexts:
    # Generic
    unauthorized: str = "Sizda ruxsat yo'q\\."
    unknown_error: str = "Xatolik yuz berdi\\. Qayta urinib ko'ring\\."
    not_found: str = "Topilmadi\\."
    cancelled: str = "Bekor qilindi\\."
    done: str = "Tayyor\\."

    # Language selection
    select_language: str = "Tilni tanlang / Выберите язык:"
    language_changed: str = "✅ Til o'zgartirildi\\: O'zbekcha"

    # Start / welcome
    welcome: str = "Salom\\! Men SadoMusicBot\\. Musiqa yuklash yoki boshqa amallarni bajarishingiz mumkin\\."
    help_text: str = "Buyruqlar ro'yxati:\\n/start \\- Botni ishga tushirish\\n/help \\- Yordam\\n/language \\- Tilni o'zgartirish\\n/submit \\- Trek yuborish\\n/donate \\- Xayriya qilish"

    # Submissions / moderation (admin callbacks)
    submission_not_found: str = "Yuborilgan trek topilmadi\\."
    invalid_callback: str = "Noto'g'ri so'rov\\."
    already_processed_prefix: str = "Bu yuborish allaqachon qayta ishlangan\\:"
    approved_and_posted: str = "✅ Tasdiqlandi va kanalga joylandi\\!"
    rejected: str = "❌ Rad etildi\\."
    channel_not_configured: str = "Bu janr uchun kanal sozlanmagan\\."

    # Messages to submitter
    submitter_approved: str = "✅ Trek tasdiqlandi va kanalga joylandi\\!"
    submitter_rejected: str = "❌ Trek tasdiqlanmadi \\(rad etildi\\)\\."

    # Music submission flow
    submit_start: str = "Trek yuborish jarayonini boshlash uchun davom eting\\."
    send_audio: str = "Iltimos, audio faylni yuboring \\(MP3, OGG, va h\\.k\\.\\)\\:"
    send_title: str = "Trek nomini kiriting\\:"
    send_artist: str = "Ijrochi ismini kiriting\\:"
    select_genre: str = "Janrni tanlang\\:"
    send_payment_info: str = "To'lov ma'lumotlarini kiriting \\(ixtiyoriy, o'tkazish uchun /skip\\)\\:"
    send_profile_link: str = "Profil havolasini kiriting \\(ixtiyoriy, o'tkazish uchun /skip\\)\\:"
    submission_preview: str = "Sizning yuborishingiz\\:"
    confirm_submission: str = "Yuborishni tasdiqlaysizmi?"
    submission_sent: str = "✅ Trek moderatsiyaga yuborildi\\! Natija haqida xabar beramiz\\."
    submission_cancelled: str = "❌ Yuborish bekor qilindi\\."

    # Donations flow
    donate_start: str = "Xayriya qilish uchun davom eting\\."
    donate_amount: str = "Summani kiriting \\(so'mda\\)\\:"
    donate_payment_method: str = "To'lov usulini tanlang\\:"
    donate_instructions: str = "To'lov quyidagi rekvizitlarga amalga oshiriladi\\:"
    donate_confirm_payment: str = "To'lovni amalga oshirdingizmi?"
    donate_thanks: str = "✅ Rahmat\\! Sizning xayriyangiz qabul qilindi\\."
    donate_cancelled: str = "❌ Xayriya bekor qilindi\\."

    # Channel post formatting (caption templates)
    # NOTE: Use format_map or f-strings with these keys:
    # {title}, {artist}, {genre}, {pay}, {profile}
    channel_caption_header: str = "🎵 {title}"
    channel_caption_artist_line: str = "👤 Ijrochi: {artist}"
    channel_caption_genre_line: str = "🎧 Janr: {genre}"
    channel_caption_support_line: str = "💳 Qo'llab\\-quvvatlash: {pay}"
    channel_caption_profile_line: str = "🔗 Profil: {profile}"
    channel_caption_footer: str = "Fikr qoldirish uchun muhokamaga o'ting\\."

    # Discussion / anchor message
    # {channel_post_url} or {post_id} depending on implementation
    discussion_anchor: str = "💬 Muhokama shu yerda\\:"

    # Admin message captions / status tags
    admin_status_pending: str = "⏳ Kutilmoqda"
    admin_status_approved: str = "✅ TASDIQLANDI"
    admin_status_rejected: str = "❌ RAD ETILDI"

    # Admin action buttons (if used)
    btn_approve: str = "✅ Tasdiqlash"
    btn_reject: str = "❌ Rad etish"
    btn_confirm: str = "✅ Tasdiqlash"
    btn_cancel: str = "❌ Bekor qilish"
    btn_skip: str = "⏭ O'tkazish"
    btn_back: str = "⬅️ Orqaga"


UZ: Dict[str, str] = {
    # Generic
    "unauthorized": UzTexts.unauthorized,
    "unknown_error": UzTexts.unknown_error,
    "not_found": UzTexts.not_found,
    "cancelled": UzTexts.cancelled,
    "done": UzTexts.done,

    # Language
    "select_language": UzTexts.select_language,
    "language_changed": UzTexts.language_changed,

    # Start / welcome
    "welcome": UzTexts.welcome,
    "help_text": UzTexts.help_text,

    # Submissions / moderation
    "submission_not_found": UzTexts.submission_not_found,
    "invalid_callback": UzTexts.invalid_callback,
    "already_processed_prefix": UzTexts.already_processed_prefix,
    "approved_and_posted": UzTexts.approved_and_posted,
    "rejected": UzTexts.rejected,
    "channel_not_configured": UzTexts.channel_not_configured,

    # Submitter notifications
    "submitter_approved": UzTexts.submitter_approved,
    "submitter_rejected": UzTexts.submitter_rejected,

    # Music submission flow
    "submit_start": UzTexts.submit_start,
    "send_audio": UzTexts.send_audio,
    "send_title": UzTexts.send_title,
    "send_artist": UzTexts.send_artist,
    "select_genre": UzTexts.select_genre,
    "send_payment_info": UzTexts.send_payment_info,
    "send_profile_link": UzTexts.send_profile_link,
    "submission_preview": UzTexts.submission_preview,
    "confirm_submission": UzTexts.confirm_submission,
    "submission_sent": UzTexts.submission_sent,
    "submission_cancelled": UzTexts.submission_cancelled,

    # Donations flow
    "donate_start": UzTexts.donate_start,
    "donate_amount": UzTexts.donate_amount,
    "donate_payment_method": UzTexts.donate_payment_method,
    "donate_instructions": UzTexts.donate_instructions,
    "donate_confirm_payment": UzTexts.donate_confirm_payment,
    "donate_thanks": UzTexts.donate_thanks,
    "donate_cancelled": UzTexts.donate_cancelled,

    # Channel formatting templates
    "channel_caption_header": UzTexts.channel_caption_header,
    "channel_caption_artist_line": UzTexts.channel_caption_artist_line,
    "channel_caption_genre_line": UzTexts.channel_caption_genre_line,
    "channel_caption_support_line": UzTexts.channel_caption_support_line,
    "channel_caption_profile_line": UzTexts.channel_caption_profile_line,
    "channel_caption_footer": UzTexts.channel_caption_footer,

    # Discussion
    "discussion_anchor": UzTexts.discussion_anchor,

    # Admin statuses
    "admin_status_pending": UzTexts.admin_status_pending,
    "admin_status_approved": UzTexts.admin_status_approved,
    "admin_status_rejected": UzTexts.admin_status_rejected,

    # Buttons
    "btn_approve": UzTexts.btn_approve,
    "btn_reject": UzTexts.btn_reject,
    "btn_confirm": UzTexts.btn_confirm,
    "btn_cancel": UzTexts.btn_cancel,
    "btn_skip": UzTexts.btn_skip,
    "btn_back": UzTexts.btn_back,
}


def t(key: str) -> str:
    """
    Simple accessor for Uzbek texts.
    Usage: t("unauthorized")
    """
    return UZ.get(key, key)

