"""
Murojaat tizimi: /boglanish
- User istalgan media yuboradi
- Admin guruhda reply → userga yetadi
- Admin reply EDIT qilsa → userdagi xabar ham yangilanadi
"""
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from shared.i18n import t
from user_bot.handlers.states import ContactState

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


async def _send_media(bot: Bot, chat_id: int, kind: str, file_id: str,
                      caption: str | None) -> Message | None:
    try:
        if kind == "video":
            return await bot.send_video(chat_id, video=file_id, caption=caption)
        elif kind == "photo":
            return await bot.send_photo(chat_id, photo=file_id, caption=caption)
        elif kind == "audio":
            return await bot.send_audio(chat_id, audio=file_id, caption=caption)
        elif kind == "voice":
            return await bot.send_voice(chat_id, voice=file_id)
        elif kind == "document":
            return await bot.send_document(chat_id, document=file_id, caption=caption)
        elif kind == "animation":
            return await bot.send_animation(chat_id, animation=file_id, caption=caption)
        elif kind == "sticker":
            return await bot.send_sticker(chat_id, sticker=file_id)
        else:
            return await bot.send_message(chat_id, caption or "")
    except TelegramBadRequest as e:
        logger.warning(f"Media yuborishda xatolik {chat_id}: {e}")
        return None


# ── /boglanish ────────────────────────────────────────────────────────────────

@router.message(F.text == "/boglanish")
async def cmd_contact(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    await state.set_state(ContactState.waiting_message)
    await message.answer(t("contact_prompt", lang))


@router.message(ContactState.waiting_message)
async def handle_contact(message: Message, state: FSMContext, db, bot: Bot, settings):
    lang = await _lang(db, message.from_user.id)
    text = message.text or message.caption or ""
    file_id, media_type = _extract_file(message)

    req_id = await db.add_request(
        user_id=message.from_user.id,
        text=text or None,
        media_type=media_type,
        file_id=file_id,
    )

    full_name = message.from_user.full_name or str(message.from_user.id)
    header = t("admin_notify_header", "uz",
               id=req_id, name=full_name, uid=message.from_user.id)

    group_id = settings.private_group_id
    admin_msg = None
    if group_id:
        try:
            if file_id:
                cap = f"{header}\n{text}" if text else header
                admin_msg = await _send_media(bot, group_id, media_type, file_id, cap)
            else:
                admin_msg = await bot.send_message(group_id, f"{header}\n{text}")
        except TelegramBadRequest as e:
            logger.warning(f"Guruhga yuborishda xatolik: {e}")

    if admin_msg:
        await db.set_request_admin_msg(req_id, admin_msg.message_id)

    await message.answer(t("contact_sent", lang))
    await state.clear()


# ── Admin guruhdan reply → userga ────────────────────────────────────────────

@router.message(F.reply_to_message & F.chat.type.in_({"group", "supergroup"}))
async def handle_admin_reply(message: Message, bot: Bot, db):
    reply = message.reply_to_message
    if not reply:
        return

    req = await db.get_request_by_admin_msg(reply.message_id)
    if not req:
        original = reply.text or reply.caption or ""
        if "MUROJAAT #" not in original:
            return
        try:
            req_id = int(original.split("#")[1].split("\n")[0].strip())
            req = await db.get_request(req_id)
        except (IndexError, ValueError):
            return
    if not req:
        return

    user_id = req["user_id"]
    lang = await _lang(db, user_id)
    prefix = t("admin_reply_prefix", lang)
    reply_text = message.text or message.caption or ""
    file_id, media_type = _extract_file(message)

    user_msg = None
    try:
        if file_id:
            cap = f"{prefix}\n\n{reply_text}" if reply_text else prefix
            user_msg = await _send_media(bot, user_id, media_type, file_id, cap)
        else:
            user_msg = await bot.send_message(user_id, f"{prefix}\n\n{reply_text}")
    except TelegramBadRequest as e:
        logger.warning(f"Userga javob yuborishda xatolik: {e}")
        await message.reply("⚠️ Userga yuborishda xatolik.")
        return

    if user_msg:
        await db.set_request_user_msg(req["id"], user_msg.message_id)
        await db.mark_request_answered(req["id"])

    await message.reply(t("admin_reply_sent", "uz"))


# ── Admin reply EDIT → userdagi xabar ham edit ───────────────────────────────

@router.edited_message(F.chat.type.in_({"group", "supergroup"}))
async def handle_admin_edit(message: Message, bot: Bot, db):
    req = await db.get_request_by_admin_msg(message.message_id)
    if not req:
        return

    user_id     = req["user_id"]
    user_msg_id = req.get("user_msg_id")
    if not user_msg_id:
        return

    lang      = await _lang(db, user_id)
    prefix    = t("admin_reply_prefix", lang)
    new_text  = message.text or message.caption or ""

    try:
        if message.text:
            await bot.edit_message_text(
                chat_id=user_id, message_id=user_msg_id,
                text=f"{prefix}\n\n{new_text} ✏️",
            )
        elif message.caption is not None:
            await bot.edit_message_caption(
                chat_id=user_id, message_id=user_msg_id,
                caption=f"{prefix}\n\n{new_text} ✏️" if new_text else f"{prefix} ✏️",
            )
    except TelegramBadRequest as e:
        logger.warning(f"User xabarini edit qilishda xatolik: {e}")
