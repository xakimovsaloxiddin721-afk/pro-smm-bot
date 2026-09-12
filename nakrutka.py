from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.database import db
from bot.keyboards.inline import nakrutka_catalog_kb
from bot.keyboards.main_menu import main_menu_kb
from bot.states import NakrutkaStates
from config import NAKRUTKA_SERVICES, ADMIN_IDS

router = Router(name="nakrutka")


@router.message(F.text == "🚀 Nakrutka avto")
async def nakrutka_menu(message: Message):
    await message.answer("🚀 Xizmatni tanlang:", reply_markup=nakrutka_catalog_kb())


@router.callback_query(F.data.startswith("nakrutka_"))
async def choose_service(callback: CallbackQuery, state: FSMContext):
    key = callback.data.removeprefix("nakrutka_")
    item = NAKRUTKA_SERVICES[key]
    await state.update_data(service_key=key, service_title=item["title"], price_per_100=item["price_per_100"])
    await state.set_state(NakrutkaStates.waiting_link)
    await callback.message.edit_text(
        f"✅ {item['title']}\n\n"
        f"Havola yoki username yuboring (masalan: kanal/post linki yoki @username)"
    )
    await callback.answer()


@router.message(NakrutkaStates.waiting_link)
async def receive_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text.strip())
    await state.set_state(NakrutkaStates.waiting_quantity)
    await message.answer("🔢 Nechta miqdorda buyurtma berasiz? (masalan: 100)")


@router.message(NakrutkaStates.waiting_quantity, F.text.regexp(r"^\d+$"))
async def receive_quantity(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    quantity = int(message.text)
    price_per_100 = data["price_per_100"]
    total_price = round(price_per_100 * quantity / 100)
    service_title = data["service_title"]
    service_key = data["service_key"]
    link = data["link"]

    balance = await db.get_balance(message.from_user.id)
    if balance < total_price:
        await state.clear()
        await message.answer(
            f"❗️<b>Balans yetarli emas</b>\n\n"
            f"Kerak: {total_price:,} so'm\n"
            f"Balans: {balance:,} so'm\n\n"
            f"Avval hisobni to'ldiring.".replace(",", " "),
            reply_markup=main_menu_kb(),
        )
        return

    await db.change_balance(message.from_user.id, -total_price)
    order_id = await db.create_order(message.from_user.id, "nakrutka", service_key, total_price, link, quantity)
    await state.clear()

    await message.answer(
        f"✅ Buyurtma qabul qilindi!\n\n"
        f"🚀 {service_title}\n"
        f"🔗 {link}\n"
        f"🔢 Miqdor: {quantity}\n"
        f"💰 Narx: {total_price:,} so'm\n"
        f"📄 Buyurtma raqami: #{order_id}".replace(",", " "),
        reply_markup=main_menu_kb(),
    )

    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"🆕 <b>Yangi nakrutka buyurtma</b>\n\n"
            f"🔢 #{order_id}\n"
            f"👤 {message.from_user.full_name} (@{message.from_user.username})\n"
            f"🚀 {service_title}\n"
            f"🔗 {link}\n"
            f"🔢 Miqdor: {quantity}\n"
            f"💰 {total_price:,} so'm".replace(",", " "),
        )


@router.message(NakrutkaStates.waiting_quantity)
async def bad_quantity(message: Message):
    await message.answer("❗️Faqat raqam kiriting, masalan: 100")
