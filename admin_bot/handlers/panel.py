"""
/panel — inline tugmali admin panel
Kanallar, adminlar, superadminlar boshqaruvi
"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

from shared.i18n import t
from shared.utils import is_root, require_perm
from admin_bot.handlers.states import PanelManageState, ChannelPanelState

router = Router()


async def _lang(db, uid):
    return await db.get_user_lang(uid)


def kb_root(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("panel_btn_send",     lang), callback_data="P:SEND")],
        [InlineKeyboardButton(text=t("panel_btn_time",     lang), callback_data="P:TIME")],
        [InlineKeyboardButton(text=t("panel_btn_channels", lang), callback_data="P:CHAN")],
        [InlineKeyboardButton(text=t("panel_btn_upload",   lang), callback_data="P:UPLOAD")],
        [InlineKeyboardButton(text=t("panel_btn_list",     lang), callback_data="P:LIST")],
        [InlineKeyboardButton(text=t("panel_btn_edit",     lang), callback_data="P:EDIT")],
        [InlineKeyboardButton(text=t("panel_btn_admins",   lang), callback_data="P:ADMINS")],
        [InlineKeyboardButton(text=t("panel_btn_supers",   lang), callback_data="P:SUPERS")],
    ])


async def kb_by_perms(db, user_id, lang):
    if await db.is_superadmin(user_id):
        perms = await db.get_superadmin_perms(user_id) or {}
    else:
        perms = await db.get_admin_perms(user_id) or {}

    buttons = []
    if perms.get("can_send_broadcast"):
        buttons.append([InlineKeyboardButton(text=t("panel_btn_send",lang),callback_data="P:SEND")])
    if perms.get("can_reset_time"):
        buttons.append([InlineKeyboardButton(text=t("panel_btn_time",lang),callback_data="P:TIME")])
    if perms.get("can_add_channel"):
        buttons.append([InlineKeyboardButton(text=t("panel_btn_channels",lang),callback_data="P:CHAN")])
    if perms.get("can_upload"):
        buttons.append([InlineKeyboardButton(text=t("panel_btn_upload",lang),callback_data="P:UPLOAD")])
        buttons.append([InlineKeyboardButton(text=t("panel_btn_list",lang),callback_data="P:LIST")])
        buttons.append([InlineKeyboardButton(text=t("panel_btn_edit",lang),callback_data="P:EDIT")])
    if perms.get("can_manage_admins"):
        buttons.append([InlineKeyboardButton(text=t("panel_btn_admins",lang),callback_data="P:ADMINS")])
    if not buttons:
        buttons = [[InlineKeyboardButton(text=t("panel_no_perm",lang),callback_data="P:NONE")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def kb_channels(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("channels_list_btn",lang),callback_data="CHAN:LIST")],
        [InlineKeyboardButton(text=t("channels_add_btn",lang),callback_data="CHAN:ADD")],
        [InlineKeyboardButton(text=t("channels_remove_btn",lang),callback_data="CHAN:REMOVE")],
        [InlineKeyboardButton(text=t("panel_back",lang),callback_data="P:BACK")],
    ])

def kb_back(lang, to="P:BACK"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("panel_back",lang),callback_data=to)]
    ])

def kb_admins(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("admins_list_btn",lang),callback_data="P:ADMINS:LIST")],
        [InlineKeyboardButton(text=t("admins_add_btn",lang),callback_data="P:ADMINS:ADD")],
        [InlineKeyboardButton(text=t("admins_del_btn",lang),callback_data="P:ADMINS:DEL")],
        [InlineKeyboardButton(text=t("panel_back",lang),callback_data="P:BACK")],
    ])

def kb_supers(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("admins_list_btn",lang),callback_data="P:SUPERS:LIST")],
        [InlineKeyboardButton(text=t("admins_add_btn",lang),callback_data="P:SUPERS:ADD")],
        [InlineKeyboardButton(text=t("admins_del_btn",lang),callback_data="P:SUPERS:DEL")],
        [InlineKeyboardButton(text=t("panel_back",lang),callback_data="P:BACK")],
    ])


@router.message(F.text.in_({"❌ Bekor qilish","❌ Отмена","❌ Cancel","/cancel"}))
async def cancel_panel(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    await state.clear()
    await message.answer(t("cancel_done", lang))


@router.message(F.text == "/panel")
async def cmd_panel(message: Message, db, settings):
    uid = message.from_user.id
    lang = await _lang(db, uid)
    if is_root(settings, uid):
        await message.answer(t("panel_root_title", lang), reply_markup=kb_root(lang))
        return
    if not (await db.is_admin(uid) or await db.is_superadmin(uid)):
        await message.answer(t("not_admin", lang))
        return
    kb = await kb_by_perms(db, uid, lang)
    await message.answer(t("panel_admin_title", lang), reply_markup=kb)


@router.callback_query(F.data == "P:SEND")
async def p_send(cb, db): await cb.answer(); await cb.message.answer("📢 /send")

@router.callback_query(F.data == "P:TIME")
async def p_time(cb, db): await cb.answer(); await cb.message.answer("⏱ /resettime")

@router.callback_query(F.data == "P:UPLOAD")
async def p_upload(cb, db): await cb.answer(); await cb.message.answer("📤 /upload")

@router.callback_query(F.data == "P:LIST")
async def p_list(cb, db): await cb.answer(); await cb.message.answer("📋 /mylist")

@router.callback_query(F.data == "P:EDIT")
async def p_edit(cb, db): await cb.answer(); await cb.message.answer("✏️ /edit")

@router.callback_query(F.data == "P:NONE")
async def p_none(cb, db):
    lang = await _lang(db, cb.from_user.id)
    await cb.answer(t("no_permission", lang), show_alert=True)

@router.callback_query(F.data == "P:BACK")
async def p_back(cb: CallbackQuery, db, settings):
    uid = cb.from_user.id; lang = await _lang(db, uid)
    if is_root(settings, uid):
        await cb.message.edit_text(t("panel_root_title", lang), reply_markup=kb_root(lang))
    else:
        kb = await kb_by_perms(db, uid, lang)
        await cb.message.edit_text(t("panel_admin_title", lang), reply_markup=kb)
    await cb.answer()


# ── Channels ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "P:CHAN")
async def p_channels(cb, db):
    lang = await _lang(db, cb.from_user.id); await cb.answer()
    await cb.message.edit_text(t("channels_panel", lang), reply_markup=kb_channels(lang))

@router.callback_query(F.data == "CHAN:LIST")
async def ch_list(cb, db):
    lang = await _lang(db, cb.from_user.id)
    channels = await db.get_channels()
    if not channels:
        await cb.message.edit_text(t("channels_empty", lang), reply_markup=kb_channels(lang))
    else:
        txt = t("channels_list_header", lang) + "\n\n"
        for ch in channels:
            txt += f"• <code>{ch['channel_id']}</code>\n{ch.get('invite_link','')}\n\n"
        await cb.message.edit_text(txt, parse_mode="HTML", reply_markup=kb_channels(lang))
    await cb.answer()

@router.callback_query(F.data == "CHAN:ADD")
async def ch_add_ask(cb: CallbackQuery, state: FSMContext, db):
    lang = await _lang(db, cb.from_user.id)
    await state.set_state(ChannelPanelState.waiting_add); await cb.answer()
    await cb.message.edit_text(t("channels_add_prompt", lang), parse_mode="HTML")

@router.message(ChannelPanelState.waiting_add)
async def ch_add_save(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.answer(t("channels_add_bad_format", lang)); return
    try:
        channel_id = int(parts[0])
    except ValueError:
        await message.answer(t("channels_bad_id", lang)); return
    await db.add_channel(channel_id, parts[1])
    await state.clear(); await message.answer(t("channels_added", lang))

@router.callback_query(F.data == "CHAN:REMOVE")
async def ch_remove_ask(cb: CallbackQuery, state: FSMContext, db):
    lang = await _lang(db, cb.from_user.id)
    await state.set_state(ChannelPanelState.waiting_remove); await cb.answer()
    await cb.message.edit_text(t("channels_remove_prompt", lang), parse_mode="HTML")

@router.message(ChannelPanelState.waiting_remove)
async def ch_remove_do(message: Message, state: FSMContext, db):
    lang = await _lang(db, message.from_user.id)
    try:
        channel_id = int((message.text or "").strip())
    except ValueError:
        await message.answer(t("channels_bad_id", lang)); return
    await db.remove_channel(channel_id)
    await state.clear(); await message.answer(t("channels_removed", lang))


# ── Admins ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "P:ADMINS")
async def p_admins(cb: CallbackQuery, db, settings):
    lang = await _lang(db, cb.from_user.id)
    if not await require_perm(db, settings, cb.from_user.id, "can_manage_admins"):
        await cb.answer(t("no_permission", lang), show_alert=True); return
    await cb.answer()
    await cb.message.edit_text(t("admins_panel", lang), reply_markup=kb_admins(lang))

@router.callback_query(F.data == "P:ADMINS:LIST")
async def p_admins_list(cb: CallbackQuery, db, settings):
    lang = await _lang(db, cb.from_user.id)
    if not await require_perm(db, settings, cb.from_user.id, "can_manage_admins"):
        await cb.answer(t("no_permission", lang), show_alert=True); return
    admins = await db.list_admins()
    text = t("admins_empty", lang) if not admins else (
        t("admins_list_header", lang) + "\n" +
        "\n".join(f"• <code>{a['user_id']}</code> | @{a.get('username') or '─'} | {a.get('full_name') or '─'}" for a in admins)
    )
    await cb.message.edit_text(text, parse_mode="HTML", reply_markup=kb_back(lang, "P:ADMINS"))
    await cb.answer()

@router.callback_query(F.data == "P:ADMINS:ADD")
async def p_admins_add(cb: CallbackQuery, state: FSMContext, db, settings):
    lang = await _lang(db, cb.from_user.id)
    if not await require_perm(db, settings, cb.from_user.id, "can_manage_admins"):
        await cb.answer(t("no_permission", lang), show_alert=True); return
    await state.set_state(PanelManageState.waiting_add_admin_id)
    await cb.answer(); await cb.message.answer(t("admins_add_prompt", lang))

@router.callback_query(F.data == "P:ADMINS:DEL")
async def p_admins_del(cb: CallbackQuery, state: FSMContext, db, settings):
    lang = await _lang(db, cb.from_user.id)
    if not await require_perm(db, settings, cb.from_user.id, "can_manage_admins"):
        await cb.answer(t("no_permission", lang), show_alert=True); return
    await state.set_state(PanelManageState.waiting_del_admin_id)
    await cb.answer(); await cb.message.answer(t("admins_del_prompt", lang))

@router.message(PanelManageState.waiting_add_admin_id)
async def add_admin_msg(message: Message, state: FSMContext, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not await require_perm(db, settings, message.from_user.id, "can_manage_admins"):
        await message.answer(t("no_permission", lang)); await state.clear(); return
    txt = (message.text or "").strip()
    if not txt.isdigit(): await message.answer(t("id_invalid", lang)); return
    await db.add_admin(int(txt)); await state.clear()
    await message.answer(t("admins_added", lang, uid=int(txt)), parse_mode="HTML")

@router.message(PanelManageState.waiting_del_admin_id)
async def del_admin_msg(message: Message, state: FSMContext, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not await require_perm(db, settings, message.from_user.id, "can_manage_admins"):
        await message.answer(t("no_permission", lang)); await state.clear(); return
    txt = (message.text or "").strip()
    if not txt.isdigit(): await message.answer(t("id_invalid", lang)); return
    await db.remove_admin(int(txt)); await state.clear()
    await message.answer(t("admins_removed", lang, uid=int(txt)), parse_mode="HTML")


# ── SuperAdmins ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "P:SUPERS")
async def p_supers(cb: CallbackQuery, db, settings):
    lang = await _lang(db, cb.from_user.id)
    if not is_root(settings, cb.from_user.id):
        await cb.answer(t("only_root", lang), show_alert=True); return
    await cb.answer()
    await cb.message.edit_text(t("supers_panel", lang), reply_markup=kb_supers(lang))

@router.callback_query(F.data == "P:SUPERS:LIST")
async def p_supers_list(cb: CallbackQuery, db, settings):
    lang = await _lang(db, cb.from_user.id)
    if not is_root(settings, cb.from_user.id):
        await cb.answer(t("only_root", lang), show_alert=True); return
    supers = await db.list_superadmins()
    text = t("supers_empty", lang) if not supers else (
        t("supers_list_header", lang) + "\n" +
        "\n".join(f"• <code>{s['user_id']}</code> | @{s.get('username') or '─'} | {s.get('full_name') or '─'}" for s in supers)
    )
    await cb.message.edit_text(text, parse_mode="HTML", reply_markup=kb_back(lang, "P:SUPERS"))
    await cb.answer()

@router.callback_query(F.data == "P:SUPERS:ADD")
async def p_supers_add(cb: CallbackQuery, state: FSMContext, db, settings):
    lang = await _lang(db, cb.from_user.id)
    if not is_root(settings, cb.from_user.id):
        await cb.answer(t("only_root", lang), show_alert=True); return
    await state.set_state(PanelManageState.waiting_add_super_id)
    await cb.answer(); await cb.message.answer(t("supers_add_prompt", lang))

@router.callback_query(F.data == "P:SUPERS:DEL")
async def p_supers_del(cb: CallbackQuery, state: FSMContext, db, settings):
    lang = await _lang(db, cb.from_user.id)
    if not is_root(settings, cb.from_user.id):
        await cb.answer(t("only_root", lang), show_alert=True); return
    await state.set_state(PanelManageState.waiting_del_super_id)
    await cb.answer(); await cb.message.answer(t("supers_del_prompt", lang))

@router.message(PanelManageState.waiting_add_super_id)
async def add_super_msg(message: Message, state: FSMContext, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not is_root(settings, message.from_user.id):
        await message.answer(t("only_root", lang)); await state.clear(); return
    txt = (message.text or "").strip()
    if not txt.isdigit(): await message.answer(t("id_invalid", lang)); return
    await db.add_superadmin(int(txt)); await state.clear()
    await message.answer(t("supers_added", lang, uid=int(txt)), parse_mode="HTML")

@router.message(PanelManageState.waiting_del_super_id)
async def del_super_msg(message: Message, state: FSMContext, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not is_root(settings, message.from_user.id):
        await message.answer(t("only_root", lang)); await state.clear(); return
    txt = (message.text or "").strip()
    if not txt.isdigit(): await message.answer(t("id_invalid", lang)); return
    await db.remove_superadmin(int(txt)); await state.clear()
    await message.answer(t("supers_removed", lang, uid=int(txt)), parse_mode="HTML")
