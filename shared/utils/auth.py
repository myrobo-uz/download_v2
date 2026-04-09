from __future__ import annotations


def is_root(settings, user_id: int) -> bool:
    return int(user_id) in set(getattr(settings, "root_admin_ids", []) or [])


async def require_admin(db, settings, user_id: int) -> bool:
    if is_root(settings, user_id):
        return True
    if await db.is_superadmin(user_id):
        return True
    return await db.is_admin(user_id)


async def require_perm(db, settings, user_id: int, perm: str) -> bool:
    if is_root(settings, user_id):
        return True
    if await db.is_superadmin(user_id):
        perms = await db.get_superadmin_perms(user_id)
        return bool(perms and perms.get(perm, False))
    perms = await db.get_admin_perms(user_id)
    return bool(perms and perms.get(perm, False))
