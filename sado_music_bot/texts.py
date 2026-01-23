"""
Text templates for Sado Music Bot
"""


def track_caption(title: str, artist_name: str) -> str:
    """Simple track caption for channel posts"""
    return (
        f"🎧 <b>{title}</b>\n"
        f"👤 <b>{artist_name}</b>\n\n"
        f"<i>💡 Support donations are in Demo mode (coming soon!)</i>"
    )


def track_caption_with_payment(title: str, artist_name: str, payment_link: str | None, caption: str | None) -> str:
    """Full track caption with optional payment link and description"""
    text = f"🎵 <b>{title}</b>\n🎤 {artist_name}\n"
    if caption:
        text += f"\n{caption}\n"
    if payment_link:
        text += f"\n💳 Support: {payment_link}"
    return text


def donation_dm_card(track_title: str, artist_name: str, amount: int, anon: bool, note: str | None) -> str:
    """Donation confirmation card shown in DM"""
    amount_str = f"{amount:,}".replace(",", " ")
    note_str = note if note else "(none)"
    anon_str = "ON" if anon else "OFF"
    return (
        f"💸 <b>Donation Confirmation</b> — <i>Demo Mode</i>\n\n"
        f"Amount: <b>{amount_str} so'm</b>\n"
        f"To: <b>{artist_name}</b>\n"
        f"Track: <i>{track_title}</i>\n"
        f"Anonymous: <b>{anon_str}</b>\n"
        f"Note: <i>{note_str}</i>\n\n"
        f"⚠️ <i>Payment integration coming soon. No real payment will be processed.</i>"
    )


def appreciation_public(donor_public: str, amount: int, artist_name: str, track_title: str, note: str | None) -> str:
    """Public appreciation message for discussion group"""
    amount_str = f"{amount:,}".replace(",", " ")
    msg = (
        f"❤️ <b>{donor_public}</b> donated <b>{amount_str} so'm</b> to <b>{artist_name}</b> (Demo)\n"
        f"🎵 <i>{track_title}</i>"
    )
    if note:
        msg += f'\n💬 "{note}"'
    return msg


def creator_dm(is_anon: bool, donor_name: str | None, donor_username: str | None,
               amount: int, track_title: str, note: str | None) -> str:
    """Private notification to artist about donation"""
    amount_str = f"{amount:,}".replace(",", " ")
    if is_anon:
        msg = (
            f"You received an anonymous donation 💸 (Demo)\n"
            f"Amount: <b>{amount_str} so'm</b>\n"
            f"Track: <i>{track_title}</i>"
        )
    else:
        uname = f" (@{donor_username})" if donor_username else ""
        msg = (
            f"You received a donation 💸 (Demo)\n"
            f"Amount: <b>{amount_str} so'm</b>\n"
            f"From: <b>{donor_name or 'Unknown'}</b>{uname}\n"
            f"Track: <i>{track_title}</i>"
        )
    if note:
        msg += f'\nNote: "{note}"'
    return msg


def artist_profile_text(artist_name: str, bio: str | None, total_tracks: int, tracks_list: list) -> str:
    """Artist profile view with track list"""
    text = f"🎤 <b>{artist_name}</b>\n\n"
    if bio:
        text += f"📝 {bio}\n\n"
    text += f"🎵 <b>Total tracks:</b> {total_tracks}\n\n"

    if tracks_list:
        text += "<b>Recent tracks:</b>\n"
        for title, genre, track_id in tracks_list:
            text += f"\n🎵 <b>{title}</b>\n"
            text += f"   Genre: {genre}\n"
    else:
        text += "<i>No tracks yet</i>"

    return text


def donation_start_text(track_title: str, artist_name: str) -> str:
    """Initial donation flow message"""
    return (
        f"❤️ <b>Support Artist</b> — <i>Demo Mode, Coming Soon</i>\n\n"
        f"🎵 Track: <i>{track_title}</i>\n"
        f"🎤 Artist: <b>{artist_name}</b>\n\n"
        f"⚠️ <i>Payment integration coming soon. This is a demo.</i>\n\n"
        f"Choose donation amount:"
    )


