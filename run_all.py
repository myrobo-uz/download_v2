"""
Ishga tushirish:
  python run_all.py           — ikkalasi birga (tavsiya)
  python run_all.py --user    — faqat user bot
  python run_all.py --admin   — faqat admin bot
"""
import asyncio
import sys
from pathlib import Path

# Loyiha ildizini sys.path ga qo'shamiz
sys.path.insert(0, str(Path(__file__).parent))

from shared.config import load_settings
from shared.db.sqlite import Database
from shared.utils.logging import setup_logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


async def run_user_bot(settings, db, logger):
    from user_bot.handlers.language     import router as lang_r
    from user_bot.handlers.contact      import router as contact_r
    from user_bot.handlers.join_request import router as jr_r
    from user_bot.handlers.user         import router as user_r

    bot = Bot(token=settings.user_bot_token)
    dp  = Dispatcher(storage=MemoryStorage())
    dp.include_router(lang_r)
    dp.include_router(contact_r)
    dp.include_router(jr_r)
    dp.include_router(user_r)
    dp["db"] = db
    dp["settings"] = settings
    dp["bot"] = bot

    me = await bot.get_me()
    logger.info(f"✅ USER BOT: @{me.username}")
    try:
        await dp.start_polling(bot, db=db, settings=settings)
    finally:
        await bot.session.close()
        logger.info("🛑 USER BOT to'xtatildi.")


async def run_admin_bot(settings, db, logger):
    from admin_bot.handlers.panel           import router as panel_r
    from admin_bot.handlers.upload          import router as upload_r
    from admin_bot.handlers.edit            import router as edit_r
    from admin_bot.handlers.mylist          import router as mylist_r
    from admin_bot.handlers.broadcast       import router as broadcast_r
    from admin_bot.handlers.cooldown        import router as cooldown_r
    from admin_bot.handlers.contact_reply   import router as reply_r
    from admin_bot.handlers.channel         import router as channel_r
    from admin_bot.handlers.admin_manage    import router as am_r

    bot = Bot(token=settings.admin_bot_token)
    dp  = Dispatcher(storage=MemoryStorage())
    dp.include_router(panel_r)
    dp.include_router(upload_r)
    dp.include_router(edit_r)
    dp.include_router(mylist_r)
    dp.include_router(broadcast_r)
    dp.include_router(cooldown_r)
    dp.include_router(reply_r)
    dp.include_router(channel_r)
    dp.include_router(am_r)
    dp["db"] = db
    dp["settings"] = settings
    dp["bot"] = bot

    me = await bot.get_me()
    logger.info(f"🔧 ADMIN BOT: @{me.username}")
    try:
        await dp.start_polling(bot, db=db, settings=settings)
    finally:
        await bot.session.close()
        logger.info("🛑 ADMIN BOT to'xtatildi.")


async def main():
    settings = load_settings()
    logger   = setup_logging()

    db = Database(settings.db_path)
    await db.connect()

    logger.info(f"🗄  DB: {settings.db_path}")
    logger.info(f"📺 Channel: {settings.private_channel_id}")
    logger.info(f"💬 Group:   {settings.private_group_id}")
    logger.info(f"👑 Roots:   {settings.root_admin_ids}")

    args = sys.argv[1:]
    try:
        if "--user" in args:
            await run_user_bot(settings, db, logger)
        elif "--admin" in args:
            await run_admin_bot(settings, db, logger)
        else:
            await asyncio.gather(
                run_user_bot(settings, db, logger),
                run_admin_bot(settings, db, logger),
            )
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
