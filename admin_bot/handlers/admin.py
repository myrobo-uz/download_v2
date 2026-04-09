"""
ADMIN BOT — upload, edit, mylist, broadcast, cooldown
"""
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)
from loguru import logger

from shared.i18n import t
from shared.utils.auth import is_root, require_perm
from shared.utils.text import normalize_code
from admin_bot.handlers.states import (
    UploadStates, EditStates, CooldownState, BroadcastState
)

router = Router()


async def _lang(db, uid): return await db.get_user_lang(uid)
async def _can(db, s, uid, p): return await require_perm(db, s, uid, p)

def _file(msg: Message):
    if msg.video:     return msg.video.file_id,      "video"
    if msg.photo:     return msg.photo[-1].file_id,  "photo"
    if msg.audio:     return msg.audio.file_id,      "audio"
    if msg.voice:     return msg.voice.file_id,      "voice"
    if msg.document:  return msg.document.file_id,   "document"
    if msg.animation: return msg.animation.file_id,  "animation"
    return None, None

def _cancel_kb(lang):
    lbl = {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "en": "❌ Cancel"}
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=lbl.get(lang, "❌ Bekor qilish"))]],
        resize_keyboard=True,
    )

async def _is_admin(db, settings, uid):
    """Admin botga faqat adminlar kirishi kerak."""
    if is_root(settings, uid): return True
    if await db.is_superadmin(uid): return True
    return await db.is_admin(uid)


# ── /start — admin botga kirish ───────────────────────────────────────────────

@router.message(F.text.in_({"/start"}))
async def cmd_start(message: Message, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not await _is_admin(db, settings, message.from_user.id):
        await message.answer("❌ Bu bot faqat adminlar uchun.")
        return
    await message.answer(
        f"👋 Xush kelibsiz, admin!\n\n"
        f"/panel — boshqaruv paneli\n"
        f"/upload — fayl yuklash\n"
        f"/mylist — yozuvlar ro'yxati\n"
        f"/edit — yozuvni tahrirlash\n"
        f"/send — broadcast\n"
        f"/resettime — cooldown sozlash"
    )


# ── /cancel ───────────────────────────────────────────────────────────────────

@router.message(F.text.in_({"❌ Bekor qilish", "❌ Отмена", "❌ Cancel", "/cancel"}))
async def cancel_any(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    await state.clear()
    await message.answer(t("cancel_done", lang), reply_markup=ReplyKeyboardRemove())


# ════════════════════════════════════════════════════════════════════════
#  UPLOAD  →  sarlavha → kod → caption → media (bir nechta yuborish mumkin)
# ════════════════════════════════════════════════════════════════════════

@router.message(F.text == "/upload")
async def upload_start(message: Message, state: FSMContext, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not await _can(db, settings, message.from_user.id, "can_upload"):
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
    lang = await _lang(db, message.from_user.id)
    caption = (message.text or "").strip()
    if caption == ".":
        caption = ""
    await state.update_data(caption=caption)
    await state.set_state(UploadStates.waiting_file)
    await message.answer(t("upload_send_file", lang), reply_markup=ReplyKeyboardRemove())


@router.message(UploadStates.waiting_file)
async def upload_file(message: Message, state: FSMContext, db, settings, bot):
    lang = await _lang(db, message.from_user.id)
    incoming_fid, kind = _file(message)
    if not incoming_fid:
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

    # ── Kanalga yuborib, qaytgan file_id ni saqlaymiz ──
    channel_fid = incoming_fid
    channel_mid = None
    ch_cap = f"<b>{title}</b>\nCode: <code>{code}</code>\nKind: {kind}\nCaption: {caption}"

    try:
        if kind == "video":
            s = await bot.send_video(settings.private_channel_id,
                video=incoming_fid, caption=ch_cap, protect_content=True)
            channel_fid = s.video.file_id
        elif kind == "photo":
            s = await bot.send_photo(settings.private_channel_id,
                photo=incoming_fid, caption=ch_cap, protect_content=True)
            channel_fid = s.photo[-1].file_id
        elif kind == "audio":
            s = await bot.send_audio(settings.private_channel_id,
                audio=incoming_fid, caption=ch_cap, protect_content=True)
            channel_fid = s.audio.file_id
        elif kind == "voice":
            s = await bot.send_voice(settings.private_channel_id,
                voice=incoming_fid, protect_content=True)
            channel_fid = s.voice.file_id
        elif kind == "document":
            s = await bot.send_document(settings.private_channel_id,
                document=incoming_fid, caption=ch_cap, protect_content=True)
            channel_fid = s.document.file_id
        elif kind == "animation":
            s = await bot.send_animation(settings.private_channel_id,
                animation=incoming_fid, caption=ch_cap, protect_content=True)
            channel_fid = s.animation.file_id
        channel_mid = s.message_id
    except TelegramBadRequest as e:
        logger.warning(f"Kanalga yuborishda xatolik: {e}")

    await db.save_video(
        code=code, title=title, file_id=channel_fid,
        kind=kind, caption=caption, channel_message_id=channel_mid,
    )

    # Holatni waiting_file da qoldiramiz — yana media yuborsa shu kod bilan davom etadi
    await message.answer(t("upload_more", lang, code=code, title=title),
                         reply_markup=_cancel_kb(lang))


# ════════════════════════════════════════════════════════════════════════
#  /mylist — yozuvlar ro'yxati
# ════════════════════════════════════════════════════════════════════════

@router.message(F.text == "/mylist")
async def my_list(message: Message, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not await _can(db, settings, message.from_user.id, "can_upload"):
        await message.answer(t("no_permission", lang))
        return
    rows = await db.get_all_videos_grouped()
    if not rows:
        await message.answer(t("mylist_empty", lang))
        return
    header = t("mylist_header", lang, total=len(rows))
    lines = [header, ""]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"{i}. <b>{r['title']}</b>  |  "
            f"<code>{r['code']}</code>  |  "
            f"{r['parts_count']} {t('mylist_parts', lang)}"
        )
    text = "\n".join(lines)
    if len(text) > 4000:
        text = text[:4000] + "\n..."
    await message.answer(text, parse_mode="HTML")


# ════════════════════════════════════════════════════════════════════════
#  EDIT
# ════════════════════════════════════════════════════════════════════════

@router.message(F.text == "/edit")
async def edit_start(message: Message, state: FSMContext, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not await _can(db, settings, message.from_user.id, "can_upload"):
        await message.answer(t("no_permission", lang))
        return
    await state.set_state(EditStates.waiting_code)
    await message.answer(t("edit_enter_code", lang), reply_markup=_cancel_kb(lang))


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
    st, key = mapping[action]
    await state.set_state(st)
    await cb.message.answer(t(key, lang), reply_markup=_cancel_kb(lang))
    await cb.answer()


@router.message(EditStates.waiting_new_code, F.text)
async def edit_code(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    new_code = normalize_code(message.text or "")
    if not new_code:
        await message.answer(t("upload_bad_code", lang)); return
    data = await state.get_data()
    vid, old = data["edit_id"], data.get("edit_code")
    if new_code != old and await db.code_exists(new_code, exclude_id=vid):
        await message.answer(t("edit_code_taken", lang)); return
    await db.update_video_code(vid, new_code)
    await state.clear()
    await message.answer(t("edit_done", lang), reply_markup=ReplyKeyboardRemove())


@router.message(EditStates.waiting_new_title, F.text)
async def edit_title(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    data = await state.get_data()
    await db.update_video_title(data["edit_id"], message.text.strip())
    await state.clear()
    await message.answer(t("edit_done", lang), reply_markup=ReplyKeyboardRemove())


@router.message(EditStates.waiting_new_caption, F.text)
async def edit_caption(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    data = await state.get_data()
    await db.update_video_caption(data["edit_id"], message.text.strip())
    await state.clear()
    await message.answer(t("edit_done", lang), reply_markup=ReplyKeyboardRemove())


@router.message(EditStates.waiting_new_file)
async def edit_file(message: Message, state: FSMContext, db, settings, bot):
    lang = await _lang(db, message.from_user.id)
    incoming_fid, kind = _file(message)
    if not incoming_fid:
        await message.answer(t("upload_send_media", lang)); return
    data = await state.get_data()
    vid, code = data["edit_id"], data.get("edit_code", "edit")
    channel_fid, channel_mid = incoming_fid, None
    try:
        if kind == "video":
            s = await bot.send_video(settings.private_channel_id,
                video=incoming_fid, caption=f"#{code} [edited]", protect_content=True)
            channel_fid = s.video.file_id
        elif kind == "photo":
            s = await bot.send_photo(settings.private_channel_id,
                photo=incoming_fid, caption=f"#{code} [edited]", protect_content=True)
            channel_fid = s.photo[-1].file_id
        elif kind == "audio":
            s = await bot.send_audio(settings.private_channel_id,
                audio=incoming_fid, caption=f"#{code} [edited]", protect_content=True)
            channel_fid = s.audio.file_id
        elif kind == "voice":
            s = await bot.send_voice(settings.private_channel_id,
                voice=incoming_fid, protect_content=True)
            channel_fid = s.voice.file_id
        elif kind == "document":
            s = await bot.send_document(settings.private_channel_id,
                document=incoming_fid, caption=f"#{code} [edited]", protect_content=True)
            channel_fid = s.document.file_id
        elif kind == "animation":
            s = await bot.send_animation(settings.private_channel_id,
                animation=incoming_fid, caption=f"#{code} [edited]", protect_content=True)
            channel_fid = s.animation.file_id
        channel_mid = s.message_id
    except TelegramBadRequest as e:
        logger.warning(f"Kanalga yuborishda xatolik: {e}")
    await db.update_video_file(vid, channel_fid, kind, channel_mid)
    await state.clear()
    await message.answer(t("edit_done", lang), reply_markup=ReplyKeyboardRemove())


# ════════════════════════════════════════════════════════════════════════
#  COOLDOWN
# ════════════════════════════════════════════════════════════════════════

@router.message(F.text == "/resettime")
async def cooldown_start(message: Message, state: FSMContext, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not await _can(db, settings, message.from_user.id, "can_reset_time"):
        await message.answer(t("no_permission", lang)); return
    await state.set_state(CooldownState.waiting_seconds)
    await message.answer(t("cooldown_prompt", lang), reply_markup=_cancel_kb(lang))


@router.message(CooldownState.waiting_seconds, F.text)
async def cooldown_set(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    txt = (message.text or "").strip()
    if not txt.isdigit() or int(txt) < 1:
        await message.answer(t("cooldown_invalid", lang)); return
    await db.set_cooldown_seconds(int(txt))
    await state.clear()
    await message.answer(t("cooldown_set", lang, seconds=int(txt)),
                         reply_markup=ReplyKeyboardRemove())


# ════════════════════════════════════════════════════════════════════════
#  BROADCAST
# ════════════════════════════════════════════════════════════════════════

@router.message(F.text == "/send")
async def broadcast_start(message: Message, state: FSMContext, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not await _can(db, settings, message.from_user.id, "can_send_broadcast"):
        await message.answer(t("no_permission", lang)); return
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
async def broadcast_other(cb: CallbackQuery):
    await cb.answer("Avval tanlov qiling yoki /cancel", show_alert=True)


@router.message(BroadcastState.waiting_content)
async def broadcast_do(message: Message, state: FSMContext, db, bot):
    lang   = await _lang(db, message.from_user.id)
    target = (await state.get_data()).get("target", "bs:all")
    users  = await db.get_all_users()

    if target == "bs:subscribed":
        users = [u for u in users if u["is_subscribed"]]
    elif target == "bs:unsubscribed":
        users = [u for u in users if not u["is_subscribed"]]

    sent = failed = 0
    fid, kind = _file(message)
    for u in users:
        cid = u["chat_id"]
        try:
            cap = message.caption or None
            if fid:
                if kind == "video":       await bot.send_video(cid, video=fid, caption=cap)
                elif kind == "photo":     await bot.send_photo(cid, photo=fid, caption=cap)
                elif kind == "audio":     await bot.send_audio(cid, audio=fid, caption=cap)
                elif kind == "voice":     await bot.send_voice(cid, voice=fid)
                elif kind == "document":  await bot.send_document(cid, document=fid, caption=cap)
                elif kind == "animation": await bot.send_animation(cid, animation=fid, caption=cap)
            elif message.text:
                await bot.send_message(cid, message.text)
            sent += 1
        except Exception:
            failed += 1

    await state.clear()
    await message.answer(t("broadcast_done", lang, sent=sent, failed=failed))
