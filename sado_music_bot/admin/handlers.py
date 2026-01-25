"""
Admin handlers - approval/rejection of track submissions and channel management
"""
import uuid
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sado_music_bot.config import Config, get_channel_for_genre, get_discussion_for_genre
from sado_music_bot.db import DB
from sado_music_bot.keyboards import kb_track_post
from sado_music_bot.texts import track_caption_with_payment
from sado_music_bot.i18n import t, t_channel

router = Router()


class AdminChannelStates(StatesGroup):
    waiting_channel_id = State()
    waiting_channel_username = State()
    waiting_channel_name = State()
    waiting_channel_description = State()
    waiting_channel_genre = State()


# =====================
# Admin Channel Management
# =====================
@router.message(Command("addchannel"))
async def cmd_add_channel(m: Message, cfg: Config, state: FSMContext):
    """Admin command to add a channel to the bot"""
    if not m.from_user or m.from_user.id != cfg.admin_id:
        return

    await m.answer(
        "📺 <b>Add Channel</b>\n\n"
        "Send the channel ID or @username:"
    )
    await state.set_state(AdminChannelStates.waiting_channel_id)


@router.message(AdminChannelStates.waiting_channel_id, F.text)
async def on_channel_id(m: Message, cfg: Config, state: FSMContext):
    if not m.from_user or m.from_user.id != cfg.admin_id or not m.text:
        return

    channel_id = m.text.strip()
    await state.update_data(channel_id=channel_id)

    # If it looks like a username, skip asking for username
    if channel_id.startswith("@"):
        await state.update_data(channel_username=channel_id[1:])
        await m.answer("Send the channel name (display name):")
        await state.set_state(AdminChannelStates.waiting_channel_name)
    else:
        await m.answer("Send the channel @username (without @), or '-' to skip:")
        await state.set_state(AdminChannelStates.waiting_channel_username)


@router.message(AdminChannelStates.waiting_channel_username, F.text)
async def on_channel_username(m: Message, cfg: Config, state: FSMContext):
    if not m.from_user or m.from_user.id != cfg.admin_id or not m.text:
        return

    username = m.text.strip()
    if username == "-":
        username = None
    elif username.startswith("@"):
        username = username[1:]

    await state.update_data(channel_username=username)
    await m.answer("Send the channel name (display name):")
    await state.set_state(AdminChannelStates.waiting_channel_name)


@router.message(AdminChannelStates.waiting_channel_name, F.text)
async def on_channel_name(m: Message, cfg: Config, state: FSMContext):
    if not m.from_user or m.from_user.id != cfg.admin_id or not m.text:
        return

    name = m.text.strip()
    await state.update_data(channel_name=name)
    await m.answer("Send a short description for the channel, or '-' to skip:")
    await state.set_state(AdminChannelStates.waiting_channel_description)


@router.message(AdminChannelStates.waiting_channel_description, F.text)
async def on_channel_description(m: Message, cfg: Config, state: FSMContext):
    if not m.from_user or m.from_user.id != cfg.admin_id or not m.text:
        return

    description = m.text.strip()
    if description == "-":
        description = None

    await state.update_data(channel_description=description)
    await m.answer("Send the genre for this channel (Pop, Rock, Hip Hop, etc.), or '-' to skip:")
    await state.set_state(AdminChannelStates.waiting_channel_genre)


@router.message(AdminChannelStates.waiting_channel_genre, F.text)
async def on_channel_genre(m: Message, cfg: Config, db: DB, state: FSMContext):
    if not m.from_user or m.from_user.id != cfg.admin_id or not m.text:
        return

    genre = m.text.strip()
    if genre == "-":
        genre = None

    data = await state.get_data()
    channel_id = data.get("channel_id")
    channel_username = data.get("channel_username")
    channel_name = data.get("channel_name")
    channel_description = data.get("channel_description")

    await db.add_channel(channel_id, channel_username, channel_name, channel_description, genre)

    await m.answer(
        f"✅ <b>Channel added!</b>\n\n"
        f"ID: <code>{channel_id}</code>\n"
        f"Username: @{channel_username or '—'}\n"
        f"Name: {channel_name}\n"
        f"Description: {channel_description or '—'}\n"
        f"Genre: {genre or '—'}"
    )
    await state.clear()


@router.message(Command("removechannel"))
async def cmd_remove_channel(m: Message, cfg: Config, db: DB):
    """Admin command to remove a channel from the bot"""
    if not m.from_user or m.from_user.id != cfg.admin_id:
        return

    if not m.text or len(m.text.split()) < 2:
        await m.answer("Usage: /removechannel <channel_id>")
        return

    channel_id = m.text.split()[1].strip()
    await db.remove_channel(channel_id)
    await m.answer(f"✅ Channel {channel_id} removed!")


@router.message(Command("listchannels"))
async def cmd_list_channels(m: Message, cfg: Config, db: DB):
    """Admin command to list all channels"""
    if not m.from_user or m.from_user.id != cfg.admin_id:
        return

    channels = await db.get_all_channels()

    if not channels:
        await m.answer("No channels configured.")
        return

    text = "📺 <b>Configured Channels:</b>\n\n"
    for channel in channels:
        channel_id, channel_username, channel_name, description, genre = channel
        text += f"• <b>{channel_name}</b>\n"
        text += f"  ID: <code>{channel_id}</code>\n"
        if channel_username:
            text += f"  Username: @{channel_username}\n"
        if description:
            text += f"  Description: {description}\n"
        if genre:
            text += f"  Genre: {genre}\n"
        text += "\n"

    await m.answer(text)


@router.callback_query(F.data.startswith("admin_approve:"))
async def on_admin_approve(cb: CallbackQuery, bot: Bot, cfg: Config, db: DB):
    """Admin approved a submission - post to channel"""
    if not cb.from_user or cb.from_user.id != cfg.admin_id:
        await cb.answer("You're not authorized.", show_alert=True)
        return

    if not cb.data:
        return

    submission_id = cb.data.split(":")[1]
    submission = await db.get_submission(submission_id)

    if not submission:
        await cb.answer("Submission not found.", show_alert=True)
        return

    sub_id, artist_id, submitter_id, title, genre, caption, file_id, status, admin_msg_id = submission

    if status != "PENDING":
        await cb.answer(f"Already {status}.", show_alert=True)
        return

    artist = await db.get_artist(artist_id)
    if not artist:
        await cb.answer("Artist not found.", show_alert=True)
        return

    _, artist_tg_id, artist_name, payment_link, profile_url, _, _ = artist
    track_id = "trk_" + uuid.uuid4().hex[:10]

    # Get channel for this genre
    channel_id = get_channel_for_genre(cfg, genre)
    discussion_id = get_discussion_for_genre(cfg, genre)

    if channel_id == 0:
        try:
            await cb.message.edit_caption(
                caption=(cb.message.caption or "") + f"\n\n❌ No channel configured for genre: {genre}"
            )
        except:
            pass
        await cb.answer("Channel not configured for this genre.", show_alert=True)
        return

    # Build caption for channel post (with links instead of buttons for comments to work)
    post_caption = track_caption_with_payment(
        title=title,
        artist_name=artist_name,
        payment_link=payment_link,
        caption=caption,
        bot_username=cfg.bot_username,
        track_id=track_id,
        artist_id=artist_id,
        profile_url=profile_url
    )

    try:
        # 1) Post track to genre channel (no reply_markup so comments can appear)
        ch_msg = await bot.send_audio(
            chat_id=channel_id,
            audio=file_id,
            caption=post_caption
        )
        print(f"[INFO] Posted track {track_id} to channel {channel_id}")

        # 2) Create anchor message in discussion group (for donation comments)
        disc_msg_id = 0
        if discussion_id != 0:
            try:
                disc_msg = await bot.send_message(
                    chat_id=discussion_id,
                    text=f"🧵 Comments for:\n{post_caption}",
                    disable_web_page_preview=True,
                )
                disc_msg_id = disc_msg.message_id
                print(f"[INFO] Created discussion anchor {disc_msg_id} in {discussion_id}")
            except Exception as e:
                print(f"[WARN] Failed to create discussion anchor: {e}")

        # 3) Save track to database
        await db.insert_track(
            track_id=track_id,
            artist_id=artist_id,
            title=title,
            genre=genre,
            caption=caption,
            telegram_file_id=file_id,
            channel_msg_id=ch_msg.message_id,
            discussion_anchor_id=disc_msg_id
        )

        # 4) Update submission status
        await db.set_submission_status(submission_id, "APPROVED")

        # 5) Update admin message
        try:
            await cb.message.edit_caption(
                caption=(cb.message.caption or "") + f"\n\n✅ <b>APPROVED</b>\nTrack ID: <code>{track_id}</code>"
            )
        except:
            pass

        # 6) Notify the submitter in their preferred language
        try:
            submitter_lang = await db.get_lang(submitter_id)
            await bot.send_message(
                chat_id=submitter_id,
                text=t("submitter_approved", submitter_lang, title=title)
            )
        except Exception as e:
            print(f"[WARN] Failed to notify submitter: {e}")

        await cb.answer("✅ Approved and posted!")
        print(f"[INFO] Approved submission {submission_id} -> track {track_id}")

    except Exception as e:
        print(f"[ERROR] Failed to post approved track: {e}")
        try:
            await cb.message.edit_caption(
                caption=(cb.message.caption or "") + f"\n\n❌ Failed to post: {e}"
            )
        except:
            pass
        await cb.answer(f"Failed: {e}", show_alert=True)


@router.callback_query(F.data.startswith("admin_reject:"))
async def on_admin_reject(cb: CallbackQuery, bot: Bot, cfg: Config, db: DB):
    """Admin rejected a submission"""
    if not cb.from_user or cb.from_user.id != cfg.admin_id:
        await cb.answer("You're not authorized.", show_alert=True)
        return

    if not cb.data:
        return

    submission_id = cb.data.split(":")[1]
    submission = await db.get_submission(submission_id)

    if not submission:
        await cb.answer("Submission not found.", show_alert=True)
        return

    sub_id, artist_id, submitter_id, title, genre, caption, file_id, status, admin_msg_id = submission

    if status != "PENDING":
        await cb.answer(f"Already {status}.", show_alert=True)
        return

    # Update submission status
    await db.set_submission_status(submission_id, "REJECTED")

    # Update admin message
    try:
        await cb.message.edit_caption(
            caption=(cb.message.caption or "") + "\n\n❌ <b>REJECTED</b>"
        )
    except:
        pass

    # Notify the submitter in their preferred language
    try:
        submitter_lang = await db.get_lang(submitter_id)
        await bot.send_message(
            chat_id=submitter_id,
            text=t("submitter_rejected", submitter_lang, title=title)
        )
    except Exception as e:
        print(f"[WARN] Failed to notify submitter: {e}")

    await cb.answer("❌ Rejected")
    print(f"[INFO] Rejected submission {submission_id}")

