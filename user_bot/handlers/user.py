"""
Foydalanuvchi: check_sub, kod → fayl yuborish
"""
from datetime import datetime, timezone

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

from shared.i18n import t
from shared.utils.subscription import is_allowed
from shared.utils.text import normalize_code

router = Router()


def _parse_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


async def _lang(db, uid: int) -> str:
    return await db.get_user_lang(uid)


@router.callback_query(F.data == "check_sub")
async def cb_check_sub(cb: CallbackQuery, db, bot):
    lang = await _lang(db, cb.from_user.id)
    channels = await db.get_channels()
    ok = await is_allowed(bot, db, cb.from_user.id, channels)
    full_name = f"{cb.from_user.first_name or ''} {cb.from_user.last_name or ''}".strip()
    await db.upsert_user(
        chat_id=cb.from_user.id, full_name=full_name,
        username=cb.from_user.username, is_subscribed=ok, lang=lang,
    )
    if ok:
        await cb.message.edit_text(t("welcome_subscribed", lang))
    else:
        await cb.answer(t("not_subscribed", lang), show_alert=True)
    await cb.answer()


@router.message(F.text)
async def get_by_code(message: Message, db, settings, bot):
    lang = await _lang(db, message.from_user.id)
    code = normalize_code(message.text or "")
    if not code:
        await message.answer(t("send_code_hint", lang))
        return

    # Cooldown
    cooldown = await db.get_cooldown_seconds()
    last = await db.get_last_used_at(message.from_user.id)
    if last:
        diff = (datetime.now(timezone.utc) - _parse_dt(last)).total_seconds()
        if diff < cooldown:
            left = int(cooldown - diff)
            await message.answer(t("cooldown_msg", lang, seconds=cooldown, left=left))
            return

    # Obuna tekshirish
    channels = await db.get_channels()
    if channels:
        ok = await is_allowed(bot, db, message.from_user.id, channels)
        if not ok:
            buttons = [
                [InlineKeyboardButton(text=t("subscribe_btn", lang), url=ch["invite_link"])]
                for ch in channels if ch.get("invite_link")
            ]
            buttons.append([InlineKeyboardButton(
                text=t("check_sub_btn", lang), callback_data="check_sub"
            )])
            await message.answer(
                t("subscribe_prompt", lang),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )
            return

    records = await db.get_videos_by_code(code)
    if not records:
        await message.answer(t("code_not_found", lang))
        return

    try:
        for idx, rec in enumerate(records, 1):
            kind    = rec.get("kind", "video")
            caption = rec.get("caption") or ""
            part_n  = rec.get("part_number")

            if part_n is not None:
                final_cap = f"{caption}\n\n{t('part_label', lang, n=part_n)}".strip()
            elif len(records) > 1:
                final_cap = f"{caption}\n\n{t('order_label', lang, n=idx)}".strip()
            else:
                final_cap = caption or None
            file_id = rec.get("file_id")

            if not file_id or not isinstance(file_id, str):
                logger.warning(f"INVALID FILE_ID: {file_id}")
                continue
            kw = dict(chat_id=message.chat.id, caption=final_cap or None, protect_content=True)
            try:
                if kind == "video":
                    await bot.send_video(video=rec["file_id"], **kw)
                elif kind == "photo":
                    await bot.send_photo(photo=rec["file_id"], **kw)
                elif kind == "audio":
                    await bot.send_audio(audio=rec["file_id"], **kw)
                elif kind == "voice":
                    await bot.send_voice(chat_id=message.chat.id,
                                        voice=rec["file_id"], protect_content=True)
                elif kind == "animation":
                    await bot.send_animation(animation=rec["file_id"], **kw)
                else:
                    await bot.send_document(document=rec["file_id"], **kw)
            except TelegramBadRequest as e:
                logger.error(f"FAILED FILE: {file_id} | ERROR: {e}")
        await db.set_last_used_now(message.from_user.id)

    except TelegramBadRequest as e:
        logger.warning(f"send xatolik: {e}")
        await message.answer(t("send_error", lang))
