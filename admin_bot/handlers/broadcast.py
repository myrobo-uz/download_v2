"""
/send — broadcast xabari
"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

from shared.i18n import t
from shared.utils import require_perm
from admin_bot.handlers.states import BroadcastState

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


@router.message(F.text == "/send")
async def broadcast_start(message: Message, state: FSMContext, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not await require_perm(db, settings, message.from_user.id, "can_send_broadcast"):
        await message.answer(t("no_permission", lang))
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("broadcast_subscribed",   lang), callback_data="bs:subscribed")],
        [InlineKeyboardButton(text=t("broadcast_unsubscribed", lang), callback_data="bs:unsubscribed")],
        [InlineKeyboardButton(text=t("broadcast_all",          lang), callback_data="bs:all")],
    ])
    await state.set_state(BroadcastState.waiting_target)
    await message.answer(t("broadcast_who", lang), reply_markup=kb)


@router.callback_query(BroadcastState.waiting_target,
                       F.data.in_({"bs:subscribed", "bs:unsubscribed", "bs:all"}))
async def broadcast_target(cb: CallbackQuery, state: FSMContext, db):
    lang = await _lang(db, cb.from_user.id)
    await state.update_data(target=cb.data)
    await state.set_state(BroadcastState.waiting_content)
    await cb.message.edit_text(t("broadcast_send_content", lang))
    await cb.answer()


@router.callback_query(BroadcastState.waiting_target)
async def broadcast_target_other(cb: CallbackQuery):
    await cb.answer("Avval tanlov qiling yoki /cancel", show_alert=True)


@router.message(BroadcastState.waiting_content)
async def broadcast_send(message: Message, state: FSMContext, db, bot):
    lang   = await _lang(db, message.from_user.id)
    data   = await state.get_data()
    target = data.get("target", "bs:all")

    all_users = await db.get_all_users()
    if target == "bs:subscribed":
        users = [u for u in all_users if u["is_subscribed"]]
    elif target == "bs:unsubscribed":
        users = [u for u in all_users if not u["is_subscribed"]]
    else:
        users = all_users

    sent = failed = 0
    file_id, kind = _extract_file(message)

    for u in users:
        cid = u["chat_id"]
        try:
            cap = message.caption or None
            if file_id:
                if kind == "video":
                    await bot.send_video(cid, video=file_id, caption=cap)
                elif kind == "photo":
                    await bot.send_photo(cid, photo=file_id, caption=cap)
                elif kind == "audio":
                    await bot.send_audio(cid, audio=file_id, caption=cap)
                elif kind == "voice":
                    await bot.send_voice(cid, voice=file_id)
                elif kind == "document":
                    await bot.send_document(cid, document=file_id, caption=cap)
                elif kind == "animation":
                    await bot.send_animation(cid, animation=file_id, caption=cap)
            elif message.text:
                await bot.send_message(cid, message.text)
            sent += 1
        except Exception:
            failed += 1

    await state.clear()
    await message.answer(t("broadcast_done", lang, sent=sent, failed=failed))
