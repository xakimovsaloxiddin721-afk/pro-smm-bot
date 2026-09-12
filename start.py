from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.database import db
from bot.keyboards.main_menu import main_menu_kb

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await db.get_or_create_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or "",
    )
    await message.answer(
        "👋 <b>Xush kelibsiz!</b>\n\n"
        "Bu yerda siz:\n"
        "🚀 Nakrutka (obunachi, layk, ko'rish)\n"
        "🎁 Gift va Premium\n"
        "buyurtma qilishingiz mumkin.\n\n"
        "Quyidagi menyudan tanlang 👇",
        reply_markup=main_menu_kb(),
    )


@router.message(F.text == "⬅️ Bosh menyu")
async def back_to_main(message: Message):
    await message.answer("Bosh menyu:", reply_markup=main_menu_kb())
