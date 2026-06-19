"""
Fayl yuklash:  nom → kod → caption → media (bir nechta)
Kanalga yuborib, qaytgan file_id ni DBga yozadi.
"""
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest, TelegramMigrateToChat
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)
from loguru import logger

from shared.i18n import t
from shared.utils import require_perm, normalize_code
from admin_bot.handlers.states import UploadStates

router = Router()


async def _lang(db, uid: int) -> str:
    return await db.get_user_lang(uid)


def _cancel_kb(lang: str) -> ReplyKeyboardMarkup:
    labels = {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "en": "❌ Cancel"}
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=labels.get(lang, "❌ Bekor qilish"))]],
        resize_keyboard=True,
    )


def _extract_file(msg: Message):
    if msg.video:     return msg.video.file_id,      "video"
    if msg.photo:     return msg.photo[-1].file_id,  "photo"
    if msg.audio:     return msg.audio.file_id,      "audio"
    if msg.voice:     return msg.voice.file_id,      "voice"
    if msg.document:  return msg.document.file_id,   "document"
    if msg.animation: return msg.animation.file_id,  "animation"
    return None, None


async def _send_to_channel(bot, settings, incoming_file_id: str,
                           kind: str, channel_caption: str):
    """Faylni kanalga yuboradi va kanaldan qaytgan file_id + message_id qaytaradi."""
    chat_id = settings.private_channel_id
    for _ in range(2):
        try:
            if kind == "video":
                sent = await bot.send_video(
                    chat_id, video=incoming_file_id,
                    caption=channel_caption, protect_content=True)
                return sent.video.file_id, sent.message_id
            elif kind == "photo":
                sent = await bot.send_photo(
                    chat_id, photo=incoming_file_id,
                    caption=channel_caption, protect_content=True)
                return sent.photo[-1].file_id, sent.message_id
            elif kind == "audio":
                sent = await bot.send_audio(
                    chat_id, audio=incoming_file_id,
                    caption=channel_caption, protect_content=True)
                return sent.audio.file_id, sent.message_id
            elif kind == "voice":
                sent = await bot.send_voice(
                    chat_id, voice=incoming_file_id,
                    protect_content=True)
                return sent.voice.file_id, sent.message_id
            elif kind == "document":
                sent = await bot.send_document(
                    chat_id, document=incoming_file_id,
                    caption=channel_caption, protect_content=True)
                return sent.document.file_id, sent.message_id
            elif kind == "animation":
                sent = await bot.send_animation(
                    chat_id, animation=incoming_file_id,
                    caption=channel_caption, protect_content=True)
                return sent.animation.file_id, sent.message_id
        except TelegramMigrateToChat as e:
            logger.warning(
                f"Guruh supergroup ga o'tgan! Yangi ID: {e.migrate_to_chat_id}. "
                f".env da PRIVATE_CHANNEL_ID={e.migrate_to_chat_id} ga yangilang."
            )
            chat_id = e.migrate_to_chat_id
        except TelegramBadRequest as e:
            logger.warning(f"Kanalga yuborishda xatolik: {e}")
            break
    return incoming_file_id, None


# ── /cancel ───────────────────────────────────────────────────────────────────

@router.message(F.text.in_({"❌ Bekor qilish", "❌ Отмена", "❌ Cancel", "/cancel"}))
async def cancel_upload(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    await state.clear()
    await message.answer(t("cancel_done", lang), reply_markup=ReplyKeyboardRemove())


# ── /upload ───────────────────────────────────────────────────────────────────

@router.message(F.text == "/upload")
async def upload_start(message: Message, state: FSMContext, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not await require_perm(db, settings, message.from_user.id, "can_upload"):
        await message.answer(t("no_permission", lang))
        return
    await state.set_state(UploadStates.waiting_title)
    await message.answer(t("upload_send_title", lang), reply_markup=_cancel_kb(lang))


@router.message(UploadStates.waiting_title, F.text)
async def upload_title(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    title = (message.text or "").strip()
    if not title:
        await message.answer(t("upload_send_title", lang))
        return
    await state.update_data(title=title)
    await state.set_state(UploadStates.waiting_code)
    await message.answer(t("upload_enter_code", lang))


@router.message(UploadStates.waiting_code, F.text)
async def upload_code(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    code = normalize_code(message.text or "")
    if not code:
        await message.answer(t("upload_bad_code", lang))
        return
    await state.update_data(code=code)
    await state.set_state(UploadStates.waiting_caption)
    await message.answer(t("upload_send_caption", lang))


@router.message(UploadStates.waiting_caption, F.text)
async def upload_caption(message: Message, state: FSMContext, db):
    caption = (message.text or "").strip()
    if caption == ".":
        caption = ""
    await state.update_data(caption=caption)
    await state.set_state(UploadStates.waiting_file)
    lang = await _lang(db, message.from_user.id)
    await message.answer(t("upload_send_file", lang), reply_markup=ReplyKeyboardRemove())


@router.message(UploadStates.waiting_file)
async def upload_file(message: Message, state: FSMContext, db, settings, bot):
    lang = await _lang(db, message.from_user.id)
    incoming_file_id, kind = _extract_file(message)
    if not incoming_file_id:
        await message.answer(t("upload_send_media", lang))
        return

    data    = await state.get_data()
    code    = data.get("code", "")
    title   = data.get("title", "")
    caption = data.get("caption", "")

    if not code:
        await message.answer(t("upload_no_code", lang))
        await state.clear()
        return

    channel_caption = (
        f"<b>{title}</b>\n"
        f"Code: <code>{code}</code>\n"
        f"Kind: {kind}"
        + (f"\n{caption}" if caption else "")
    )

    # Kanalga yuborib, qaytgan file_id ni olamiz
    channel_file_id, channel_message_id = await _send_to_channel(
        bot, settings, incoming_file_id, kind, channel_caption
    )

    await db.save_video(
        code=code,
        title=title,
        file_id=channel_file_id,
        kind=kind,
        caption=caption,
        channel_message_id=channel_message_id,
    )

    # Holat waiting_file da qoladi — yana media yuborish mumkin
    await message.answer(
        t("upload_more", lang, code=code, title=title),
        reply_markup=_cancel_kb(lang),
    )
