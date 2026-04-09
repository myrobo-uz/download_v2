"""
Private kanalga yuborilgan postlarni tinglash:
caption ichida kod → avtomatik DBga yozish
"""
from aiogram import Router
from aiogram.types import Message
from loguru import logger

from shared.utils import normalize_code, strip_code_from_caption

router = Router()


def _extract_file(msg: Message):
    if msg.video:     return msg.video.file_id,      "video"
    if msg.audio:     return msg.audio.file_id,      "audio"
    if msg.document:  return msg.document.file_id,   "document"
    if msg.voice:     return msg.voice.file_id,      "voice"
    if msg.animation: return msg.animation.file_id,  "animation"
    if msg.photo:     return msg.photo[-1].file_id,  "photo"
    return None, None


@router.channel_post()
async def on_channel_post(message: Message, db, settings):
    if message.chat.id != settings.private_channel_id:
        return

    file_id, kind = _extract_file(message)
    if not file_id:
        return

    raw_caption = message.caption or ""
    code = normalize_code(raw_caption)
    if not code:
        logger.info("Kanal posti: caption ichida kod topilmadi, o'tkazildi.")
        return

    user_caption = strip_code_from_caption(raw_caption, code)

    await db.save_video(
        code=code,
        title=code,
        file_id=file_id,
        kind=kind,
        caption=user_caption,
        channel_message_id=message.message_id,
    )
    logger.success(f"Kanal posti saqlandi | code={code} | kind={kind}")
