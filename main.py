import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from bot.database.db import init_db
from bot.handlers import start, balance, topup, gift_premium, nakrutka, support, admin

logging.basicConfig(level=logging.INFO)


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi. .env faylini tekshiring.")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Admin router birinchi bo'lishi kerak — callback'lar to'g'ri ishlashi uchun
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(balance.router)
    dp.include_router(topup.router)
    dp.include_router(gift_premium.router)
    dp.include_router(nakrutka.router)
    dp.include_router(support.router)

    await init_db()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
