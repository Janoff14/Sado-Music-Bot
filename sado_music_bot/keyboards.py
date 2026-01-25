"""
Keyboard layouts for Sado Music Bot
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PRESET_AMOUNTS = [5000, 10000, 25000]
GENRES = ["Pop", "Rock", "Indie", "Hip Hop", "Rap", "Electronic", "Other"]


def kb_lang() -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        ]
    ])


def kb_genres(prefix: str) -> InlineKeyboardMarkup:
    """Genre selection keyboard with custom callback prefix"""
    rows = []
    row = []
    for i, g in enumerate(GENRES, start=1):
        row.append(InlineKeyboardButton(text=g, callback_data=f"{prefix}:{g}"))
        if i % 2 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="❌ Cancel", callback_data=f"{prefix}:CANCEL")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_track_post(track_id: str, artist_id: str, bot_username: str) -> InlineKeyboardMarkup:
    """Inline keyboard for channel posts - opens bot for donation & artist profile"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="❤️ Support Artist (Demo)",
            url=f"https://t.me/{bot_username}?start=donate_{track_id}"
        )],
        [InlineKeyboardButton(
            text="👤 Artist Profile",
            url=f"https://t.me/{bot_username}?start=artist_{artist_id}"
        )]
    ])


def kb_admin_review(submission_id: str) -> InlineKeyboardMarkup:
    """Admin approve/reject keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"admin_approve:{submission_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"admin_reject:{submission_id}"),
        ]
    ])


def kb_donation_confirm(donation_id: str, anon_on: bool, has_note: bool) -> InlineKeyboardMarkup:
    """Donation confirmation keyboard in DM"""
    anon_text = "🎭 Anonymous: ON" if anon_on else "🎭 Anonymous: OFF"
    note_text = "💬 Edit note" if has_note else "💬 Add note"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm (Demo)", callback_data=f"don_ok:{donation_id}")],
        [
            InlineKeyboardButton(text=anon_text, callback_data=f"don_anon:{donation_id}"),
            InlineKeyboardButton(text=note_text, callback_data=f"don_note:{donation_id}"),
        ],
        [InlineKeyboardButton(text="❌ Cancel", callback_data=f"don_cancel:{donation_id}")],
    ])


def kb_profile_actions() -> InlineKeyboardMarkup:
    """Profile edit actions keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Edit name", callback_data="profile:edit:display_name")],
        [InlineKeyboardButton(text="💳 Edit payment link", callback_data="profile:edit:payment_link")],
        [InlineKeyboardButton(text="🎧 Edit default genre", callback_data="profile:edit:default_genre")],
        [InlineKeyboardButton(text="📝 Edit bio", callback_data="profile:edit:bio")],
    ])


def kb_donation_amounts(track_id: str) -> InlineKeyboardMarkup:
    """Amount selection for donation flow (Demo mode)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 5 000 so'm (Demo)", callback_data=f"donamtsel:{track_id}:5000")],
        [InlineKeyboardButton(text="💸 10 000 so'm (Demo)", callback_data=f"donamtsel:{track_id}:10000")],
        [InlineKeyboardButton(text="💸 25 000 so'm (Demo)", callback_data=f"donamtsel:{track_id}:25000")],
        [InlineKeyboardButton(text="✏️ Custom amount (Demo)", callback_data=f"donamtsel:{track_id}:custom")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="doncancel")]
    ])


def kb_donation_note_options(donation_id: str) -> InlineKeyboardMarkup:
    """Ask if user wants to add a note"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Add message", callback_data=f"don_note:{donation_id}")],
        [InlineKeyboardButton(text="➡️ Skip", callback_data=f"don_skip_note:{donation_id}")],
    ])


def kb_donation_anonymity(donation_id: str) -> InlineKeyboardMarkup:
    """Ask anonymity preference"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌟 Donate publicly", callback_data=f"don_public:{donation_id}")],
        [InlineKeyboardButton(text="🎭 Donate anonymously", callback_data=f"don_anon_set:{donation_id}")],
    ])


def kb_track_support(track_id: str) -> InlineKeyboardMarkup:
    """Support button for individual tracks in artist profile (Demo mode)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❤️ Support (Demo)", callback_data=f"support_track:{track_id}")]
    ])


def kb_user_type(lang: str = "uz") -> InlineKeyboardMarkup:
    """User type selection keyboard (artist or listener)"""
    if lang == "ru":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎤 Артист", callback_data="usertype:artist")],
            [InlineKeyboardButton(text="🎧 Слушатель", callback_data="usertype:listener")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎤 Ijrochi", callback_data="usertype:artist")],
            [InlineKeyboardButton(text="🎧 Tinglovchi", callback_data="usertype:listener")],
        ])


def kb_search_result_artist(artist_id: str, bot_username: str, lang: str = "uz") -> InlineKeyboardMarkup:
    """Button to view artist profile from search results"""
    text = "👤 Профиль" if lang == "ru" else "👤 Profil"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=text,
            url=f"https://t.me/{bot_username}?start=artist_{artist_id}"
        )]
    ])


def kb_search_result_track(track_id: str, artist_id: str, bot_username: str, channel_username: str = None,
                           channel_msg_id: int = None, lang: str = "uz") -> InlineKeyboardMarkup:
    """Buttons for track search results - donate and view artist"""
    donate_text = "❤️ Донат" if lang == "ru" else "❤️ Donat"
    profile_text = "👤 Профиль" if lang == "ru" else "👤 Profil"
    listen_text = "🎧 Слушать" if lang == "ru" else "🎧 Tinglash"

    buttons = []

    # If we have channel info, add listen button
    if channel_username and channel_msg_id:
        buttons.append([InlineKeyboardButton(
            text=listen_text,
            url=f"https://t.me/{channel_username}/{channel_msg_id}"
        )])

    # Donate and profile buttons
    buttons.append([
        InlineKeyboardButton(
            text=donate_text,
            url=f"https://t.me/{bot_username}?start=donate_{track_id}"
        ),
        InlineKeyboardButton(
            text=profile_text,
            url=f"https://t.me/{bot_username}?start=artist_{artist_id}"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


