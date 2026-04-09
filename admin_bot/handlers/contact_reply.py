"""
Admin guruhidan reply va edit:
- Admin guruhda MUROJAAT xabariga reply → foydalanuvchi botiga yetkaziladi
- Admin reply ni edit qilsa → userdagi xabar ham edit bo'ladi
"""
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from loguru import logger

from shared.i18n import t

router = Router()


async def _lang(db, uid: int) -> str:
    return await db.get_user_lang(uid)


def _extract_file(msg: Message):
    if msg.video:     return msg.video.file_id,      "video"
    if msg.photo:     return msg.photo[-1].file_id,  "photo"
    if msg.audio:     return msg.audio.file_id,      "audio"
    if msg.voice:     return msg.voice.file_id,      "voice"
    if msg.document:  return msg.document.file_id,   "document"
    if msg.animation: return msg.animation.file_id,  "animation"
    if msg.sticker:   return msg.sticker.file_id,    "sticker"
    return None, None


async def _send_to_user(bot: Bot, user_id: int, media_type: str | None,
                        file_id: str | None, text: str) -> Message | None:
    """User botiga media yoki matn yuboradi."""
    try:
        if file_id and media_type:
            if media_type == "video":
                return await bot.send_video(user_id, video=file_id, caption=text or None)
            elif media_type == "photo":
                return await bot.send_photo(user_id, photo=file_id, caption=text or None)
            elif media_type == "audio":
                return await bot.send_audio(user_id, audio=file_id, caption=text or None)
            elif media_type == "voice":
                return await bot.send_voice(user_id, voice=file_id)
            elif media_type == "document":
                return await bot.send_document(user_id, document=file_id, caption=text or None)
            elif media_type == "animation":
                return await bot.send_animation(user_id, animation=file_id, caption=text or None)
            elif media_type == "sticker":
                return await bot.send_sticker(user_id, sticker=file_id)
        if text:
            return await bot.send_message(user_id, text)
    except TelegramBadRequest as e:
        logger.warning(f"Userga yuborishda xatolik ({user_id}): {e}")
    return None


# ── Admin guruhda MUROJAAT xabariga reply ────────────────────────────────────

@router.message(F.reply_to_message & F.chat.type.in_({"group", "supergroup"}))
async def handle_admin_reply(message: Message, bot: Bot, db, settings):
    reply = message.reply_to_message
    if not reply:
        return

    # 1) DB dan admin_msg_id orqali topamiz
    req = await db.get_request_by_admin_msg(reply.message_id)

    # 2) Fallback — matn ichida "MUROJAAT #" bor-yo'qligini tekshirish
    if not req:
        original_text = reply.text or reply.caption or ""
        if "MUROJAAT #" not in original_text and "ОБРАЩЕНИЕ #" not in original_text and "REQUEST #" not in original_text:
            return
        try:
            req_id = int(original_text.split("#")[1].split("\n")[0].strip())
            req = await db.get_request(req_id)
        except (IndexError, ValueError):
            return

    if not req:
        return

    user_id = req["user_id"]
    lang    = await _lang(db, user_id)
    prefix  = t("admin_reply_prefix", lang)

    reply_text = message.text or message.caption or ""
    file_id, media_type = _extract_file(message)

    full_text = f"{prefix}\n\n{reply_text}" if reply_text else prefix

    user_msg = await _send_to_user(bot, user_id, media_type, file_id, full_text)

    if user_msg:
        await db.set_request_user_msg(req["id"], user_msg.message_id)
        await db.mark_request_answered(req["id"])

    await message.reply(t("admin_reply_sent", "uz"))


# ── Admin reply ni EDIT qilsa → userdagi xabar ham edit ─────────────────────

@router.edited_message(F.chat.type.in_({"group", "supergroup"}))
async def handle_admin_edit(message: Message, bot: Bot, db):
    req = await db.get_request_by_admin_msg(message.message_id)
    if not req:
        return

    user_id     = req["user_id"]
    user_msg_id = req.get("user_msg_id")
    if not user_msg_id:
        return

    lang     = await _lang(db, user_id)
    prefix   = t("admin_reply_prefix", lang)
    new_text = message.text or message.caption or ""
    edited   = f"{prefix}\n\n{new_text} ✏️" if new_text else f"{prefix} ✏️"

    try:
        if message.text:
            await bot.edit_message_text(
                chat_id=user_id,
                message_id=user_msg_id,
                text=edited,
            )
        elif message.caption is not None:
            await bot.edit_message_caption(
                chat_id=user_id,
                message_id=user_msg_id,
                caption=edited,
            )
    except TelegramBadRequest as e:
        logger.warning(f"User xabarini edit qilishda xatolik: {e}")
