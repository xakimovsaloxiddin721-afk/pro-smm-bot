from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.database import db
from bot.keyboards.inline import gift_premium_menu_kb, gift_catalog_kb, premium_catalog_kb
from bot.keyboards.main_menu import main_menu_kb
from bot.states import GiftStates
from config import GIFT_CATALOG, PREMIUM_PLANS, ADMIN_IDS

router = Router(name="gift_premium")


@router.message(F.text == "🎁 Gift/Premium")
async def gift_premium_menu(message: Message):
    await message.answer("Nimani sotib olmoqchisiz?", reply_markup=gift_premium_menu_kb())


@router.callback_query(F.data == "menu_gift_premium")
async def back_gift_premium(callback: CallbackQuery):
    await callback.message.edit_text("Nimani sotib olmoqchisiz?", reply_markup=gift_premium_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "menu_back")
async def back_to_main(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Bosh menyu:", reply_markup=main_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "menu_gift")
async def show_gift_catalog(callback: CallbackQuery):
    await callback.message.edit_text("🎁 Gift tanlang:", reply_markup=gift_catalog_kb())
    await callback.answer()


@router.callback_query(F.data == "menu_premium")
async def show_premium_catalog(callback: CallbackQuery):
    await callback.message.edit_text("⭐ Premium tarifni tanlang:", reply_markup=premium_catalog_kb())
    await callback.answer()


async def _start_purchase(callback: CallbackQuery, state: FSMContext, item_key: str, item_title: str, price: int, order_type: str):
    balance = await db.get_balance(callback.from_user.id)
    if balance < price:
        await callback.message.edit_text(
            f"❗️<b>Balans yetarli emas</b>\n\n"
            f"Ushbu {item_title} uchun kerak: <b>{price:,} so'm</b>\n"
            f"Hozirgi balans: <b>{balance:,} so'm</b>\n"
            f"Yetishmayapti: <b>{price - balance:,} so'm</b>\n\n"
            f"Avval \"💳 Hisobni to'ldirish\" orqali balansni to'ldiring.".replace(",", " ")
        )
        await callback.answer()
        return

    await state.update_data(item_key=item_key, item_title=item_title, price=price, order_type=order_type)
    await state.set_state(GiftStates.waiting_username)
    await callback.message.edit_text(
        f"✅ {item_title} — {price:,} so'm\n\n"
        f"Qabul qiluvchi username'ini yuboring (masalan: @username)".replace(",", " ")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("gift_"))
async def choose_gift(callback: CallbackQuery, state: FSMContext):
    key = callback.data.removeprefix("gift_")
    item = GIFT_CATALOG[key]
    await _start_purchase(callback, state, key, item["title"], item["price"], "gift")


@router.callback_query(F.data.startswith("premium_"))
async def choose_premium(callback: CallbackQuery, state: FSMContext):
    key = callback.data.removeprefix("premium_")
    item = PREMIUM_PLANS[key]
    await _start_purchase(callback, state, key, item["title"], item["price"], "premium")


@router.message(GiftStates.waiting_username, F.text.startswith("@"))
async def receive_username(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    price = data["price"]
    item_title = data["item_title"]
    item_key = data["item_key"]
    order_type = data["order_type"]
    target = message.text.strip()

    balance = await db.get_balance(message.from_user.id)
    if balance < price:
        await message.answer("❗️Balans yetarli emas. Iltimos avval hisobni to'ldiring.")
        await state.clear()
        return

    await db.change_balance(message.from_user.id, -price)
    order_id = await db.create_order(message.from_user.id, order_type, item_key, price, target)
    await state.clear()

    await message.answer(
        f"✅ Buyurtma qabul qilindi!\n\n"
        f"🎁 {item_title}\n"
        f"👤 Qabul qiluvchi: {target}\n"
        f"💰 Narx: {price:,} so'm\n"
        f"🔢 Buyurtma raqami: #{order_id}\n\n"
        f"Tez orada yetkazib beriladi.".replace(",", " "),
        reply_markup=main_menu_kb(),
    )

    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"🆕 <b>Yangi {order_type} buyurtma</b>\n\n"
            f"🔢 #{order_id}\n"
            f"👤 Buyurtmachi: {message.from_user.full_name} (@{message.from_user.username})\n"
            f"🎁 {item_title}\n"
            f"➡️ Qabul qiluvchi: {target}\n"
            f"💰 {price:,} so'm".replace(",", " "),
        )


@router.message(GiftStates.waiting_username)
async def bad_username(message: Message):
    await message.answer("❗️Username @ belgisi bilan boshlanishi kerak. Masalan: @username")
