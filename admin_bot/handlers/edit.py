"""
Mavjud yozuvni tahrirlash: kod, sarlavha, caption yoki fayl
"""
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from loguru import logger

from shared.i18n import t
from shared.utils import require_perm, normalize_code
from admin_bot.handlers.states import EditStates

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
    return None, None


async def _send_to_channel(bot, settings, incoming_file_id: str, kind: str, caption: str):
    try:
        if kind == "video":
            sent = await bot.send_video(settings.private_channel_id,
                video=incoming_file_id, caption=caption, protect_content=True)
            return sent.video.file_id, sent.message_id
        elif kind == "photo":
            sent = await bot.send_photo(settings.private_channel_id,
                photo=incoming_file_id, caption=caption, protect_content=True)
            return sent.photo[-1].file_id, sent.message_id
        elif kind == "audio":
            sent = await bot.send_audio(settings.private_channel_id,
                audio=incoming_file_id, caption=caption, protect_content=True)
            return sent.audio.file_id, sent.message_id
        elif kind == "voice":
            sent = await bot.send_voice(settings.private_channel_id,
                voice=incoming_file_id, protect_content=True)
            return sent.voice.file_id, sent.message_id
        elif kind == "document":
            sent = await bot.send_document(settings.private_channel_id,
                document=incoming_file_id, caption=caption, protect_content=True)
            return sent.document.file_id, sent.message_id
        elif kind == "animation":
            sent = await bot.send_animation(settings.private_channel_id,
                animation=incoming_file_id, caption=caption, protect_content=True)
            return sent.animation.file_id, sent.message_id
    except TelegramBadRequest as e:
        logger.warning(f"Edit: kanalga yuborishda xatolik: {e}")
    return incoming_file_id, None


# ── /edit ─────────────────────────────────────────────────────────────────────

@router.message(F.text == "/edit")
async def edit_start(message: Message, state: FSMContext, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not await require_perm(db, settings, message.from_user.id, "can_upload"):
        await message.answer(t("no_permission", lang))
        return
    await state.set_state(EditStates.waiting_code)
    await message.answer(t("edit_enter_code", lang))


@router.message(EditStates.waiting_code, F.text)
async def edit_get_code(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    code = normalize_code(message.text or "")
    if not code:
        await message.answer(t("upload_bad_code", lang))
        return

    records = await db.get_videos_by_code(code)
    if not records:
        await message.answer(t("edit_not_found", lang))
        return

    rec = records[0]
    await state.update_data(edit_id=rec["id"], edit_code=code)
    await state.set_state(EditStates.choosing_field)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("edit_btn_code",    lang), callback_data="edit:code")],
        [InlineKeyboardButton(text=t("edit_btn_title",   lang), callback_data="edit:title")],
        [InlineKeyboardButton(text=t("edit_btn_caption", lang), callback_data="edit:caption")],
        [InlineKeyboardButton(text=t("edit_btn_file",    lang), callback_data="edit:file")],
        [InlineKeyboardButton(text=t("edit_btn_cancel",  lang), callback_data="edit:cancel")],
    ])
    await message.answer(
        t("edit_choose_field", lang, code=code, title=rec.get("title") or "─"),
        reply_markup=kb,
    )


@router.callback_query(EditStates.choosing_field, F.data.startswith("edit:"))
async def edit_choose(cb: CallbackQuery, state: FSMContext, db):
    lang   = await _lang(db, cb.from_user.id)
    action = cb.data.split(":")[1]

    if action == "cancel":
        await state.clear()
        await cb.message.edit_text(t("cancel_done", lang))
        await cb.answer()
        return

    mapping = {
        "code":    (EditStates.waiting_new_code,    "edit_enter_new_code"),
        "title":   (EditStates.waiting_new_title,   "edit_enter_new_title"),
        "caption": (EditStates.waiting_new_caption, "edit_enter_new_caption"),
        "file":    (EditStates.waiting_new_file,    "edit_enter_new_file"),
    }
    state_cls, msg_key = mapping[action]
    await state.set_state(state_cls)
    await cb.message.answer(t(msg_key, lang))
    await cb.answer()


@router.message(EditStates.waiting_new_code, F.text)
async def edit_save_code(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    new_code = normalize_code(message.text or "")
    if not new_code:
        await message.answer(t("upload_bad_code", lang))
        return
    data     = await state.get_data()
    vid      = data["edit_id"]
    old_code = data.get("edit_code")
    if new_code != old_code and await db.code_exists(new_code, exclude_id=vid):
        await message.answer(t("edit_code_taken", lang))
        return
    await db.update_video_code(vid, new_code)
    await state.clear()
    await message.answer(t("edit_done", lang), reply_markup=ReplyKeyboardRemove())


@router.message(EditStates.waiting_new_title, F.text)
async def edit_save_title(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    data = await state.get_data()
    await db.update_video_title(data["edit_id"], message.text.strip())
    await state.clear()
    await message.answer(t("edit_done", lang), reply_markup=ReplyKeyboardRemove())


@router.message(EditStates.waiting_new_caption, F.text)
async def edit_save_caption(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    data = await state.get_data()
    await db.update_video_caption(data["edit_id"], message.text.strip())
    await state.clear()
    await message.answer(t("edit_done", lang), reply_markup=ReplyKeyboardRemove())


@router.message(EditStates.waiting_new_file)
async def edit_save_file(message: Message, state: FSMContext, db, settings, bot):
    lang = await _lang(db, message.from_user.id)
    incoming_file_id, kind = _extract_file(message)
    if not incoming_file_id:
        await message.answer(t("upload_send_media", lang))
        return

    data = await state.get_data()
    vid  = data["edit_id"]
    code = data.get("edit_code", "edit")

    channel_file_id, channel_message_id = await _send_to_channel(
        bot, settings, incoming_file_id, kind, f"#{code} [edited]"
    )
    await db.update_video_file(vid, channel_file_id, kind, channel_message_id)
    await state.clear()
    await message.answer(t("edit_done", lang), reply_markup=ReplyKeyboardRemove())
