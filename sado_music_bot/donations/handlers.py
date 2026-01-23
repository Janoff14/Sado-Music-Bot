"""
Donation handlers - handles donation flow from channel buttons
"""
import logging
import re
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from sado_music_bot.config import Config, get_discussion_for_genre
from sado_music_bot.db import DB
from sado_music_bot.keyboards import (
    kb_donation_confirm, kb_donation_amounts, kb_donation_note_options,
    kb_donation_anonymity, kb_track_support
)
from sado_music_bot.texts import donation_dm_card, appreciation_public, creator_dm, donation_start_text
from sado_music_bot.i18n import t, t_channel
from .states import DonationNote

router = Router()
logger = logging.getLogger(__name__)


class DonationAmountState(StatesGroup):
    waiting_custom_amount = State()


def _clean_note(text: str) -> str | None:
    """Clean user note: remove links, limit length"""
    raw = (text or "").strip()
    raw = re.sub(r"https?://\S+", "", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    if not raw:
        return None
    return raw[:120]


# =====================
# New Donation Flow (from deep links)
# =====================

@router.callback_query(F.data.startswith("donamtsel:"))
async def on_donation_amount_selected(cb: CallbackQuery, db: DB, state: FSMContext):
    """Handle amount selection in donation flow"""
    if not cb.data or not cb.from_user:
        return

    parts = cb.data.split(":")
    if len(parts) < 3:
        await cb.answer("Invalid data", show_alert=True)
        return

    track_id = parts[1]
    amount_str = parts[2]

    # Handle custom amount
    if amount_str == "custom":
        await state.update_data(donation_track_id=track_id)
        await state.set_state(DonationAmountState.waiting_custom_amount)
        await cb.message.edit_text("✏️ Enter custom amount in so'm (e.g., 15000):")
        await cb.answer()
        return

    try:
        amount = int(amount_str)
    except ValueError:
        await cb.answer("Invalid amount", show_alert=True)
        return

    # Create donation and proceed to note step
    await _create_donation_and_ask_note(cb, db, track_id, amount)


@router.message(DonationAmountState.waiting_custom_amount, F.text)
async def on_custom_amount(m: Message, db: DB, state: FSMContext):
    """Handle custom amount input"""
    if m.text and m.text.startswith("/"):
        return

    try:
        amount = int(m.text.strip().replace(" ", "").replace(",", ""))
        if amount < 1000:
            await m.answer("❌ Minimum amount is 1 000 so'm")
            return
        if amount > 1000000:
            await m.answer("❌ Maximum amount is 1 000 000 so'm")
            return
    except ValueError:
        await m.answer("❌ Please enter a valid number")
        return

    data = await state.get_data()
    track_id = data.get("donation_track_id")

    if not track_id:
        await m.answer("Session expired. Please try again.")
        await state.clear()
        return

    # Create donation and proceed
    track = await db.get_track(track_id)
    if not track:
        await m.answer("❌ Track not found")
        await state.clear()
        return

    _, artist_id, track_title, _, _, _, _, _, status = track

    if status != "ACTIVE":
        await m.answer("❌ Track is no longer active")
        await state.clear()
        return

    artist = await db.get_artist(artist_id)
    if not artist:
        await m.answer("❌ Artist not found")
        await state.clear()
        return

    artist_name = artist[2]

    # Create donation
    donation_id = await db.create_donation(
        track_id=track_id,
        artist_id=artist_id,
        donor_user_id=m.from_user.id,
        donor_name=m.from_user.full_name,
        donor_username=m.from_user.username,
        amount=amount,
        is_anonymous=0
    )

    # Clear state after creating donation
    await state.clear()

    # Ask for note
    await m.answer(
        f"✅ Amount: <b>{amount:,} so'm</b>\n\n"
        f"🎵 {track_title}\n"
        f"🎤 {artist_name}\n\n"
        "Would you like to add a message for the artist?",
        reply_markup=kb_donation_note_options(donation_id)
    )


async def _create_donation_and_ask_note(cb: CallbackQuery, db: DB, track_id: str, amount: int):
    """Helper to create donation and ask for note"""
    if not cb.from_user:
        return

    track = await db.get_track(track_id)
    if not track:
        await cb.answer("Track not found", show_alert=True)
        return

    _, artist_id, track_title, _, _, _, _, _, status = track

    if status != "ACTIVE":
        await cb.answer("Track is no longer active", show_alert=True)
        return

    artist = await db.get_artist(artist_id)
    if not artist:
        await cb.answer("Artist not found", show_alert=True)
        return

    artist_name = artist[2]

    # Create donation
    donation_id = await db.create_donation(
        track_id=track_id,
        artist_id=artist_id,
        donor_user_id=cb.from_user.id,
        donor_name=cb.from_user.full_name,
        donor_username=cb.from_user.username,
        amount=amount,
        is_anonymous=0
    )

    # Ask for note
    await cb.message.edit_text(
        f"✅ Amount: <b>{amount:,} so'm</b>\n\n"
        f"🎵 {track_title}\n"
        f"🎤 {artist_name}\n\n"
        "Would you like to add a message for the artist?",
        reply_markup=kb_donation_note_options(donation_id)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("don_skip_note:"))
async def on_skip_note(cb: CallbackQuery, db: DB):
    """Skip adding a note and proceed to anonymity"""
    if not cb.data:
        return

    donation_id = cb.data.split(":")[1]
    donation = await db.get_donation(donation_id)

    if not donation:
        await cb.answer("Not found", show_alert=True)
        return

    # Ask anonymity preference
    await cb.message.edit_text(
        "Choose your donation visibility:",
        reply_markup=kb_donation_anonymity(donation_id)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("don_public:"))
async def on_donate_public(cb: CallbackQuery, db: DB):
    """User chose to donate publicly"""
    if not cb.data:
        return

    donation_id = cb.data.split(":")[1]

    # Set anonymous to 0
    donation = await db.get_donation(donation_id)
    if not donation:
        await cb.answer("Not found", show_alert=True)
        return

    if donation[8] != 0:  # is_anonymous
        await db.toggle_donation_anon(donation_id)

    # Show final confirmation
    await _show_final_confirmation(cb, db, donation_id)


@router.callback_query(F.data.startswith("don_anon_set:"))
async def on_donate_anonymous(cb: CallbackQuery, db: DB):
    """User chose to donate anonymously"""
    if not cb.data:
        return

    donation_id = cb.data.split(":")[1]

    # Set anonymous to 1
    donation = await db.get_donation(donation_id)
    if not donation:
        await cb.answer("Not found", show_alert=True)
        return

    if donation[8] == 0:  # is_anonymous
        await db.toggle_donation_anon(donation_id)

    # Show final confirmation
    await _show_final_confirmation(cb, db, donation_id)


async def _show_final_confirmation(cb: CallbackQuery, db: DB, donation_id: str):
    """Show final confirmation card"""
    donation = await db.get_donation(donation_id)
    if not donation:
        await cb.answer("Not found", show_alert=True)
        return

    _, track_id, artist_id, _, _, _, amount, note, is_anon, _ = donation

    track = await db.get_track(track_id)
    artist = await db.get_artist(artist_id)

    if not track or not artist:
        await cb.answer("Missing data", show_alert=True)
        return

    track_title = track[2]
    artist_name = artist[2]

    text = donation_dm_card(track_title, artist_name, amount, bool(is_anon), note)

    await cb.message.edit_text(
        text,
        reply_markup=kb_donation_confirm(donation_id, bool(is_anon), has_note=bool(note))
    )
    await cb.answer()


@router.callback_query(F.data == "doncancel")
async def on_donation_cancel(cb: CallbackQuery):
    """Cancel donation flow"""
    await cb.message.edit_text("❌ Donation canceled.")
    await cb.answer()


@router.callback_query(F.data.startswith("support_track:"))
async def on_support_track_from_profile(cb: CallbackQuery, db: DB):
    """Handle support button from artist profile track list"""
    if not cb.data or not cb.from_user:
        return

    track_id = cb.data.split(":")[1]
    track = await db.get_track(track_id)

    if not track:
        await cb.answer("Track not found", show_alert=True)
        return

    _, artist_id, track_title, _, _, _, _, _, status = track

    if status != "ACTIVE":
        await cb.answer("Track is no longer active", show_alert=True)
        return

    artist = await db.get_artist(artist_id)
    if not artist:
        await cb.answer("Artist not found", show_alert=True)
        return

    artist_name = artist[2]

    # Show donation amount selection
    await cb.message.answer(
        donation_start_text(track_title, artist_name),
        reply_markup=kb_donation_amounts(track_id)
    )
    await cb.answer()


# =====================
# Legacy handlers - REMOVED (duplicate flow)
# The old don_amt: flow has been removed to avoid having two separate donation processes.
# All donations now go through the deep link flow (donamtsel:)
# =====================


@router.callback_query(F.data.startswith("don_anon:"))
async def on_toggle_anon(cb: CallbackQuery, db: DB):
    """Toggle anonymous setting for a donation"""
    if not cb.data or not cb.from_user:
        return

    donation_id = cb.data.split(":")[1]
    donation = await db.get_donation(donation_id)
    if not donation:
        await cb.answer("Not found.", show_alert=True)
        return

    # Unpack: (donation_id, track_id, artist_id, donor_user_id, donor_name, donor_username, amount, note, is_anonymous, status)
    _, track_id, artist_id, _, _, _, amount, note, is_anon, status = donation

    if status != "CREATED":
        await cb.answer("Not editable.", show_alert=True)
        return

    # Toggle anonymity
    new_anon = await db.toggle_donation_anon(donation_id)
    # Save as user's default
    await db.set_anon_default(cb.from_user.id, new_anon)

    # Get track and artist for updated card
    track = await db.get_track(track_id)
    artist = await db.get_artist(artist_id)
    if not track or not artist:
        await cb.answer("Missing data.", show_alert=True)
        return

    track_title = track[2]  # title
    artist_name = artist[2]  # display_name

    # Update card
    text = donation_dm_card(track_title, artist_name, amount, bool(new_anon), note)
    try:
        await cb.message.edit_text(
            text,
            reply_markup=kb_donation_confirm(donation_id, bool(new_anon), has_note=bool(note))
        )
    except Exception as e:
        logger.warning(f"Failed to edit donation card {donation_id}: {e}")
    await cb.answer("Updated.")


@router.callback_query(F.data.startswith("don_note:"))
async def on_add_note(cb: CallbackQuery, state: FSMContext, db: DB):
    """Start note editing flow"""
    if not cb.data:
        return

    donation_id = cb.data.split(":")[1]
    donation = await db.get_donation(donation_id)
    if not donation:
        await cb.answer("Not found.", show_alert=True)
        return

    if donation[9] != "CREATED":  # status
        await cb.answer("Not editable.", show_alert=True)
        return

    await state.set_state(DonationNote.waiting_note)
    await state.update_data(donation_id=donation_id, card_message_id=cb.message.message_id)
    await cb.answer()
    await cb.message.reply("Send your note (max 120 chars). Links will be removed.")


@router.message(DonationNote.waiting_note, F.text)
async def on_note_text(m: Message, state: FSMContext, bot: Bot, db: DB):
    if m.text and m.text.startswith("/"):
        return
    data = await state.get_data()
    donation_id = data.get("donation_id")
    card_message_id = data.get("card_message_id")

    if not donation_id:
        await m.answer("Session expired.")
        await state.clear()
        return

    note = _clean_note(m.text or "")
    await db.set_donation_note(donation_id, note)

    # Get updated donation
    donation = await db.get_donation(donation_id)
    if not donation:
        await m.answer("Donation not found.")
        await state.clear()
        return

    _, track_id, artist_id, _, _, _, amount, new_note, is_anon, status = donation

    track = await db.get_track(track_id)
    artist = await db.get_artist(artist_id)
    if not track or not artist:
        await m.answer("Missing data.")
        await state.clear()
        return

    track_title = track[2]
    artist_name = artist[2]

    # Update the original confirmation card
    text = donation_dm_card(track_title, artist_name, amount, bool(is_anon), new_note)
    try:
        await bot.edit_message_text(
            chat_id=m.chat.id,
            message_id=card_message_id,
            text=text,
            reply_markup=kb_donation_confirm(donation_id, bool(is_anon), has_note=bool(new_note))
        )
    except Exception as e:
        logger.warning(f"Failed to edit donation card after note: {e}")

    await m.answer("✅ Note saved.")
    await state.clear()


@router.callback_query(F.data.startswith("don_cancel:"))
async def on_cancel_donation(cb: CallbackQuery, db: DB):
    """Cancel a pending donation"""
    if not cb.data:
        return

    donation_id = cb.data.split(":")[1]
    donation = await db.get_donation(donation_id)
    if not donation:
        await cb.answer("Not found.", show_alert=True)
        return

    if donation[9] != "CREATED":  # status
        await cb.answer("Already processed.", show_alert=True)
        return

    await db.set_donation_status(donation_id, "CANCELED")
    try:
        await cb.message.edit_text("❌ Donation canceled.")
    except Exception as e:
        logger.warning(f"Failed to edit message after cancel: {e}")
    await cb.answer("Canceled.")


@router.callback_query(F.data.startswith("don_ok:"))
async def on_confirm_donation(cb: CallbackQuery, bot: Bot, cfg: Config, db: DB):
    """Confirm a donation (demo mode)"""
    if not cb.data or not cb.from_user:
        return

    donation_id = cb.data.split(":")[1]
    donation = await db.get_donation(donation_id)
    if not donation:
        await cb.answer("Not found.", show_alert=True)
        return

    _, track_id, artist_id, donor_user_id, donor_name, donor_username, amount, note, is_anon, status = donation

    if status != "CREATED":
        await cb.answer("Already processed.", show_alert=True)
        return

    # Confirm in database
    await db.set_donation_status(donation_id, "CONFIRMED")

    # Get track and artist
    track = await db.get_track(track_id)
    artist = await db.get_artist(artist_id)
    if not track or not artist:
        await cb.answer("Missing data.", show_alert=True)
        return

    # Unpack track: (track_id, artist_id, title, genre, caption, file_id, channel_msg_id, disc_anchor_id, status)
    _, _, track_title, genre, _, _, _, disc_anchor_id, _ = track

    # Unpack artist: (artist_id, tg_user_id, display_name, payment_link, profile_url, default_genre, bio)
    _, artist_tg_id, artist_name, _, _, _, _ = artist

    # 1) Post appreciation message in discussion group
    donor_public = "Someone" if int(is_anon) == 1 else (donor_name or cb.from_user.full_name)
    appreciation = appreciation_public(donor_public, amount, artist_name, track_title, note)

    discussion_id = get_discussion_for_genre(cfg, genre)
    if discussion_id != 0 and disc_anchor_id != 0:
        try:
            await bot.send_message(
                chat_id=discussion_id,
                text=appreciation,
                reply_to_message_id=int(disc_anchor_id),
            )
            print(f"[INFO] Posted appreciation in discussion {discussion_id}")
        except Exception as e:
            print(f"[WARN] Failed to post appreciation: {e}")

    # 2) DM the artist
    msg_to_artist = creator_dm(bool(is_anon), donor_name, donor_username, amount, track_title, note)
    try:
        await bot.send_message(chat_id=int(artist_tg_id), text=msg_to_artist)
        print(f"[INFO] Notified artist {artist_tg_id}")
    except Exception as e:
        print(f"[WARN] Failed to DM artist: {e}")

    # 3) Update donor's confirmation card
    try:
        await cb.message.edit_text("✅ Donation confirmed (Demo). Thanks for supporting the artist!")
    except Exception as e:
        logger.warning(f"Failed to edit confirmation message: {e}")
    await cb.answer("Confirmed ✅")
    print(f"[INFO] Confirmed donation {donation_id}")


# Note: /cancel command is handled by music.handlers to avoid duplicate handlers
