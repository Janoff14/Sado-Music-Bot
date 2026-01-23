"""
Admin handlers - approval/rejection of track submissions
"""
import uuid
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from sado_music_bot.config import Config, get_channel_for_genre, get_discussion_for_genre
from sado_music_bot.db import DB
from sado_music_bot.keyboards import kb_track_post
from sado_music_bot.texts import track_caption_with_payment
from sado_music_bot.i18n import t, t_channel

router = Router()


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

    # Build caption for channel post
    post_caption = track_caption_with_payment(title, artist_name, payment_link, caption)

    try:
        # 1) Post track to genre channel
        ch_msg = await bot.send_audio(
            chat_id=channel_id,
            audio=file_id,
            caption=post_caption,
            reply_markup=kb_track_post(track_id, artist_id, cfg.bot_username)
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
                text=t("submitter_approved", submitter_lang),
                parse_mode="MarkdownV2"
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
            text=t("submitter_rejected", submitter_lang),
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        print(f"[WARN] Failed to notify submitter: {e}")

    await cb.answer("❌ Rejected")
    print(f"[INFO] Rejected submission {submission_id}")

