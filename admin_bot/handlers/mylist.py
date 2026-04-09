"""
/mylist — yuklangan yozuvlar ro'yxati
"""
from aiogram import Router, F
from aiogram.types import Message

from shared.i18n import t
from shared.utils import require_perm

router = Router()


async def _lang(db, uid: int) -> str:
    return await db.get_user_lang(uid)


@router.message(F.text == "/mylist")
async def my_list(message: Message, db, settings):
    lang = await _lang(db, message.from_user.id)
    if not await require_perm(db, settings, message.from_user.id, "can_upload"):
        await message.answer(t("no_permission", lang))
        return

    rows = await db.get_all_videos_grouped()
    if not rows:
        await message.answer(t("mylist_empty", lang))
        return

    header = t("mylist_header", lang, total=len(rows))
    lines  = [header, ""]
    for i, r in enumerate(rows, 1):
        parts = r["parts_count"]
        lines.append(
            f"{i}. <b>{r['title']}</b>  |  "
            f"<code>{r['code']}</code>  |  "
            f"{parts} {t('mylist_parts', lang)}"
        )

    text = "\n".join(lines)
    if len(text) > 4000:
        text = text[:4000] + "\n..."
    await message.answer(text, parse_mode="HTML")
