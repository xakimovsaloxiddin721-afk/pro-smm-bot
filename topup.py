from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery

from bot.database import db
from bot.keyboards.inline import topup_methods_kb, admin_topup_decision_kb
from bot.states import TopupStates
from config import ADMIN_IDS, CARD_HUMO_NUMBER, CARD_UZCARD_NUMBER, CARD_OWNER_NAME

router = Router(name="topup")


@router.message(F.text == "💳 Hisobni to'ldirish")
async def topup_menu(message: Message):
    await message.answer("To'lov usulini tanlang 👇", reply_markup=topup_methods_kb())


@router.callback_query(F.data.in_({"topup_humo", "topup_uzcard"}))
async def choose_card(callback: CallbackQuery, state: FSMContext):
    method = "HUMO" if callback.data == "topup_humo" else "UZCARD"
    card_number = CARD_HUMO_NUMBER if method == "HUMO" else CARD_UZCARD_NUMBER
    await state.update_data(method=method)
    await state.set_state(TopupStates.waiting_amount)
    await callback.message.edit_text(
        f"💳 <b>{method}</b> orqali to'lov\n\n"
        f"Karta raqami: <code>{card_number}</code>\n"
        f"Karta egasi: {CARD_OWNER_NAME}\n\n"
        f"Qancha summa to'ldirmoqchisiz? (so'mda, faqat raqam yuboring)"
    )
    await callback.answer()


@router.message(TopupStates.waiting_amount, F.text.regexp(r"^\d+$"))
async def get_amount(message: Message, state: FSMContext):
    amount = int(message.text)
    await state.update_data(amount=amount)
    await state.set_state(TopupStates.waiting_receipt)
    await message.answer(
        f"✅ Summa: <b>{amount:,} so'm</b>\n\n"
        f"Endi to'lov chekini (screenshot) shu yerga rasm qilib yuboring.".replace(",", " ")
    )


@router.message(TopupStates.waiting_amount)
async def bad_amount(message: Message):
    await message.answer("❗️Iltimos faqat raqam yuboring, masalan: 50000")


@router.message(TopupStates.waiting_receipt, F.photo)
async def get_receipt(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    amount = data["amount"]
    method = data["method"]
    file_id = message.photo[-1].file_id

    tx_id = await db.create_transaction(message.from_user.id, amount, method, file_id)
    await state.clear()

    await message.answer(
        "✅ Chek qabul qilindi. Admin tekshirib, balansingizga qo'shadi. "
        "Iltimos kuting."
    )

    caption = (
        f"🧾 <b>Yangi to'lov so'rovi</b>\n\n"
        f"👤 Foydalanuvchi: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"💳 Usul: {method}\n"
        f"💰 Summa: {amount:,} so'm\n"
        f"🔢 Tranzaksiya ID: {tx_id}"
    ).replace(",", " ")

    for admin_id in ADMIN_IDS:
        await bot.send_photo(admin_id, file_id, caption=caption, reply_markup=admin_topup_decision_kb(tx_id))


@router.message(TopupStates.waiting_receipt)
async def bad_receipt(message: Message):
    await message.answer("❗️Iltimos, to'lov chekining rasmini (screenshot) yuboring.")


# ---------- Telegram Stars (native, provider_token shart emas) ----------

@router.callback_query(F.data == "topup_stars")
async def stars_amount_prompt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TopupStates.waiting_stars_amount)
    await callback.message.edit_text("⭐ Nechta Stars sotib olmoqchisiz? (raqam kiriting, masalan: 100)")
    await callback.answer()


@router.message(TopupStates.waiting_stars_amount, F.text.regexp(r"^\d+$"))
async def stars_amount_received(message: Message, state: FSMContext, bot: Bot):
    stars = int(message.text)
    await state.clear()
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Balansni to'ldirish",
        description=f"{stars} ⭐ Stars orqali balansni to'ldirish",
        payload=f"stars_topup_{message.from_user.id}_{stars}",
        provider_token="",  # Stars uchun bo'sh qoldiriladi
        currency="XTR",
        prices=[LabeledPrice(label="Stars", amount=stars)],
    )


@router.pre_checkout_query()
async def pre_checkout(pre_checkout_q: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    stars = message.successful_payment.total_amount
    # 1 Stars ~ narxni o'zingiz belgilagan kursga ko'ra so'mga aylantiring
    som_equivalent = stars * 250  # namunaviy kurs, config'ga chiqarish tavsiya etiladi
    await db.change_balance(message.from_user.id, som_equivalent)
    await message.answer(f"✅ To'lov qabul qilindi! Balansingizga {som_equivalent:,} so'm qo'shildi.".replace(",", " "))
