"""
/add_admin /remove_admin /set_perm /admins — buyruq orqali boshqaruv
"""
from aiogram import Router, F
from aiogram.types import Message

from shared.i18n import t
from shared.utils.auth import is_root

router = Router()

async def _lang(db, uid): return await db.get_user_lang(uid)


@router.message(F.text.startswith("/add_admin"))
async def add_admin(message: Message, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not is_root(settings, message.from_user.id):
        await message.answer(t("only_root", lang)); return
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer("Format: /add_admin 123456789"); return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer(t("id_invalid", lang)); return
    await db.add_admin(uid)
    await message.answer(t("admins_added", lang, uid=uid), parse_mode="HTML")


@router.message(F.text.startswith("/remove_admin"))
async def remove_admin(message: Message, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not is_root(settings, message.from_user.id):
        await message.answer(t("only_root", lang)); return
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer("Format: /remove_admin 123456789"); return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer(t("id_invalid", lang)); return
    await db.remove_admin(uid)
    await message.answer(t("admins_removed", lang, uid=uid), parse_mode="HTML")


@router.message(F.text.startswith("/set_perm"))
async def set_perm(message: Message, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not is_root(settings, message.from_user.id):
        await message.answer(t("only_root", lang)); return
    parts = (message.text or "").split()
    if len(parts) != 4:
        await message.answer(
            "Format:\n/set_perm 123456789 broadcast 1\n"
            "perm: add_channel | broadcast | upload | reset_time | manage_admins"
        ); return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer(t("id_invalid", lang)); return
    perm_map = {
        "add_channel":   "can_add_channel",
        "broadcast":     "can_send_broadcast",
        "upload":        "can_upload",
        "reset_time":    "can_reset_time",
        "manage_admins": "can_manage_admins",
    }
    perm = perm_map.get(parts[2])
    if not perm:
        await message.answer("perm noto'g'ri: add_channel | broadcast | upload | reset_time | manage_admins")
        return
    if parts[3] not in ("0", "1"):
        await message.answer("Qiymat 0 yoki 1 bo'lsin."); return
    await db.set_admin_perms(uid, **{perm: int(parts[3])})
    await message.answer("✅ Ruxsat yangilandi.")


@router.message(F.text == "/admins")
async def list_admins(message: Message, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not is_root(settings, message.from_user.id):
        await message.answer(t("only_root", lang)); return
    admins = await db.list_admins()
    if not admins:
        await message.answer(t("admins_empty", lang)); return
    lines = []
    for a in admins:
        p = a.get("perms", {})
        lines.append(
            f"<code>{a['user_id']}</code> | @{a.get('username') or '─'} | {a.get('full_name') or '─'}\n"
            f"  upload={int(p.get('can_upload',0))}  "
            f"broadcast={int(p.get('can_send_broadcast',0))}  "
            f"channels={int(p.get('can_add_channel',0))}  "
            f"time={int(p.get('can_reset_time',0))}  "
            f"admins={int(p.get('can_manage_admins',0))}"
        )
    await message.answer("\n\n".join(lines), parse_mode="HTML")
