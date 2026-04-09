"""
Til tanlash: /start va /change_language
"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from shared.i18n import t
from shared.utils.subscription import is_allowed

router = Router()

LANG_KB = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
    InlineKeyboardButton(text="🇷🇺 Русский",   callback_data="lang:ru"),
    InlineKeyboardButton(text="🇬🇧 English",   callback_data="lang:en"),
]])


@router.message(F.text.in_({"/start", "/change_language", "/til"}))
async def cmd_language(message: Message, db, state: FSMContext):
    await state.clear()
    await message.answer(t("choose_language", "uz"), reply_markup=LANG_KB)


@router.callback_query(F.data.startswith("lang:"))
async def cb_set_lang(cb: CallbackQuery, db, bot):
    lang = cb.data.split(":")[1]
    if lang not in ("uz", "ru", "en"):
        await cb.answer()
        return

    await db.set_user_lang(cb.from_user.id, lang)
    await cb.message.edit_text(t("language_set", lang))
    await cb.answer()

    channels = await db.get_channels()
    ok = True
    if channels:
        ok = await is_allowed(bot, db, cb.from_user.id, channels)

    if ok:
        await cb.message.answer(t("welcome_subscribed", lang))
    else:
        buttons = [
            [InlineKeyboardButton(text=t("subscribe_btn", lang), url=ch["invite_link"])]
            for ch in channels if ch.get("invite_link")
        ]
        buttons.append([InlineKeyboardButton(
            text=t("check_sub_btn", lang), callback_data="check_sub"
        )])
        await cb.message.answer(
            t("subscribe_prompt", lang),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
