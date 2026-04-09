"""
/resettime — cooldown vaqtini o'zgartirish
"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from shared.i18n import t
from shared.utils import require_perm
from admin_bot.handlers.states import CooldownState

router = Router()


async def _lang(db, uid: int) -> str:
    return await db.get_user_lang(uid)


@router.message(F.text == "/resettime")
async def reset_time_start(message: Message, state: FSMContext, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not await require_perm(db, settings, message.from_user.id, "can_reset_time"):
        await message.answer(t("no_permission", lang))
        return
    await state.set_state(CooldownState.waiting_seconds)
    await message.answer(t("cooldown_prompt", lang))


@router.message(CooldownState.waiting_seconds, F.text)
async def set_cooldown(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    txt  = (message.text or "").strip()
    if not txt.isdigit() or int(txt) < 1:
        await message.answer(t("cooldown_invalid", lang))
        return
    seconds = int(txt)
    await db.set_cooldown_seconds(seconds)
    await state.clear()
    await message.answer(
        t("cooldown_set", lang, seconds=seconds),
        reply_markup=ReplyKeyboardRemove(),
    )
