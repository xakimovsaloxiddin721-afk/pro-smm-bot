from aiogram import Router, F
from aiogram.types import Message

from bot.database import db

router = Router(name="balance")


@router.message(F.text == "💰 Balans")
async def show_balance(message: Message):
    balance = await db.get_balance(message.from_user.id)
    await message.answer(f"💰 Sizning balansingiz: <b>{balance:,} so'm</b>".replace(",", " "))
