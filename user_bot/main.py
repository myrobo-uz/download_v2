"""
USER BOT — foydalanuvchilar boti
Ishga tushirish: python user_bot/main.py
"""
import asyncio
import sys
from pathlib import Path

# shared/ papkasini import yo'liga qo'shamiz
sys.path.insert(0, str(Path(__file__).parent.parent))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from shared.config import load_settings
from shared.db.sqlite import Database
from shared.utils.logging import setup_logging

from user_bot.handlers.language import router as language_router
from user_bot.handlers.contact import router as contact_router
from user_bot.handlers.join_request import router as join_request_router
from user_bot.handlers.user import router as user_router


async def main():
    settings = load_settings()
    logger = setup_logging()

    bot = Bot(token=settings.user_bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    db = Database(settings.db_path)
    await db.connect()

    # Tartib muhim — language avval, user eng oxirida (fallback)
    dp.include_router(language_router)
    dp.include_router(contact_router)
    dp.include_router(join_request_router)
    dp.include_router(user_router)

    dp["db"] = db
    dp["settings"] = settings
    dp["bot"] = bot

    logger.info("✅ USER BOT ishga tushdi.")
    logger.info(f"📺 Private channel: {settings.private_channel_id}")

    try:
        await dp.start_polling(bot, db=db, settings=settings)
    finally:
        logger.info("🛑 USER BOT to'xtatildi.")
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
