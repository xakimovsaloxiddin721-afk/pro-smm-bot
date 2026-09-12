from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.states import SupportStates
from config import ADMIN_IDS

router = Router(name="support")


@router.message(F.text == "☎️ Qo'llab-quvvatlash")
async def support_menu(message: Message, state: FSMContext):
    await state.set_state(SupportStates.waiting_message)
    await message.answer("✍️ Savolingizni yozing, admin tez orada javob beradi.")


@router.message(SupportStates.waiting_message)
async def forward_to_admin(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await message.answer("✅ Xabaringiz yuborildi. Admin tez orada bog'lanadi.")
    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"📩 <b>Yangi murojaat</b>\n\n"
            f"👤 {message.from_user.full_name} (@{message.from_user.username})\n"
            f"🆔 <code>{message.from_user.id}</code>\n\n"
            f"{message.text}",
        )
