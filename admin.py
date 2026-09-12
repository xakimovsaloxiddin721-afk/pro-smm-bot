from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.database import db
from config import ADMIN_IDS

router = Router(name="admin")


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("add_balance"))
async def add_balance_cmd(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    # Foydalanish: /add_balance <user_id> <summa>
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Foydalanish: /add_balance <user_id> <summa>")
        return
    try:
        user_id, amount = int(parts[1]), int(parts[2])
    except ValueError:
        await message.answer("user_id va summa raqam bo'lishi kerak.")
        return

    await db.change_balance(user_id, amount)
    await message.answer(f"✅ {user_id} balansiga {amount:,} so'm qo'shildi.".replace(",", " "))
    try:
        await bot.send_message(user_id, f"✅ Balansingizga {amount:,} so'm qo'shildi.".replace(",", " "))
    except Exception:
        pass


@router.callback_query(F.data.startswith("approve_tx_"))
async def approve_topup(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return
    tx_id = int(callback.data.removeprefix("approve_tx_"))
    tx = await db.get_transaction(tx_id)
    if tx is None:
        await callback.answer("Tranzaksiya topilmadi", show_alert=True)
        return
    if tx["status"] != "pending":
        await callback.answer("Bu tranzaksiya allaqachon ko'rib chiqilgan", show_alert=True)
        return

    await db.change_balance(tx["user_id"], tx["amount"])
    await db.set_transaction_status(tx_id, "approved")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ TASDIQLANDI")
    await callback.answer("Tasdiqlandi")

    try:
        await bot.send_message(
            tx["user_id"],
            f"✅ To'lovingiz tasdiqlandi! Balansingizga {tx['amount']:,} so'm qo'shildi.".replace(",", " "),
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("reject_tx_"))
async def reject_topup(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return
    tx_id = int(callback.data.removeprefix("reject_tx_"))
    tx = await db.get_transaction(tx_id)
    if tx is None:
        await callback.answer("Tranzaksiya topilmadi", show_alert=True)
        return

    await db.set_transaction_status(tx_id, "rejected")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ RAD ETILDI")
    await callback.answer("Rad etildi")

    try:
        await bot.send_message(tx["user_id"], "❌ To'lovingiz rad etildi. Qo'llab-quvvatlash bilan bog'laning.")
    except Exception:
        pass


@router.callback_query(F.data.startswith("done_order_"))
async def order_done(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return
    order_id = int(callback.data.removeprefix("done_order_"))
    await db.set_order_status(order_id, "done")
    await callback.message.edit_text(callback.message.text + "\n\n✅ BAJARILDI")
    await callback.answer("Bajarildi deb belgilandi")


@router.callback_query(F.data.startswith("cancel_order_"))
async def order_cancel(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return
    order_id = int(callback.data.removeprefix("cancel_order_"))
    await db.set_order_status(order_id, "cancelled")
    await callback.message.edit_text(callback.message.text + "\n\n❌ BEKOR QILINDI")
    await callback.answer("Bekor qilindi")
