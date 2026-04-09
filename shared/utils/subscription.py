from aiogram.exceptions import TelegramBadRequest


async def is_allowed(bot, db, user_id: int, channels: list[dict]) -> bool:
    for ch in channels:
        channel_id = ch["channel_id"]
        try:
            member = await bot.get_chat_member(channel_id, user_id)
            if member.status not in ("left", "kicked"):
                continue
        except TelegramBadRequest:
            pass
        if await db.has_join_request(user_id, channel_id):
            continue
        return False
    return True
