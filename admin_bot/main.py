import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from shared.config import load_settings
from shared.utils import setup_logging
from shared.db import Database

from admin_bot.handlers.panel            import router as panel_router
from admin_bot.handlers.upload           import router as upload_router
from admin_bot.handlers.edit             import router as edit_router
from admin_bot.handlers.mylist           import router as mylist_router
from admin_bot.handlers.broadcast        import router as broadcast_router
from admin_bot.handlers.cooldown         import router as cooldown_router
from admin_bot.handlers.contact_reply    import router as contact_reply_router
from admin_bot.handlers.channel_listener import router as channel_router


async def main():
    settings = load_settings()
    logger   = setup_logging()

    bot = Bot(token=settings.admin_bot_token)
    dp  = Dispatcher(storage=MemoryStorage())

    db = Database(settings.db_path)
    await db.connect()

    dp.include_router(panel_router)
    dp.include_router(upload_router)
    dp.include_router(edit_router)
    dp.include_router(mylist_router)
    dp.include_router(broadcast_router)
    dp.include_router(cooldown_router)
    dp.include_router(contact_reply_router)
    dp.include_router(channel_router)

    dp["db"]       = db
    dp["settings"] = settings
    dp["bot"]      = bot

    async def on_startup():
        me = await bot.get_me()
        logger.info(f"ADMIN BOT: @{me.username}")
        logger.info(f"Private channel: {settings.private_channel_id}")
        logger.info(f"Root IDs: {settings.root_admin_ids}")

    async def on_shutdown():
        logger.info("Admin bot to'xtatilmoqda...")
        await db.close()
        await bot.session.close()

    try:
        await on_startup()
        await dp.start_polling(bot, db=db, settings=settings)
    finally:
        await on_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
