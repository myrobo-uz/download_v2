from aiogram import Router
from aiogram.types import ChatJoinRequest

router = Router()

@router.chat_join_request()
async def on_join_request(update: ChatJoinRequest, db):
    await db.upsert_join_request(update.from_user.id, update.chat.id)
