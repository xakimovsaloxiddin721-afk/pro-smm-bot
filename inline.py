from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import GIFT_CATALOG, PREMIUM_PLANS, NAKRUTKA_SERVICES


def gift_premium_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🎁 Gift olish", callback_data="menu_gift")
    b.button(text="⭐ Premium olish", callback_data="menu_premium")
    b.button(text="⬅️ Orqaga", callback_data="menu_back")
    b.adjust(2, 1)
    return b.as_markup()


def gift_catalog_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key, item in GIFT_CATALOG.items():
        b.button(text=f"{item['title']} — {item['price']:,} so'm".replace(",", " "), callback_data=f"gift_{key}")
    b.button(text="⬅️ Orqaga", callback_data="menu_gift_premium")
    b.adjust(2)
    return b.as_markup()


def premium_catalog_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key, item in PREMIUM_PLANS.items():
        b.button(text=f"{item['title']} — {item['price']:,} so'm".replace(",", " "), callback_data=f"premium_{key}")
    b.button(text="⬅️ Orqaga", callback_data="menu_gift_premium")
    b.adjust(1)
    return b.as_markup()


def nakrutka_catalog_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key, item in NAKRUTKA_SERVICES.items():
        b.button(text=f"{item['title']} — {item['price_per_100']:,} so'm/100ta".replace(",", " "), callback_data=f"nakrutka_{key}")
    b.button(text="⬅️ Orqaga", callback_data="menu_back")
    b.adjust(1)
    return b.as_markup()


def topup_methods_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="💳 HUMO", callback_data="topup_humo")
    b.button(text="💳 UZCARD", callback_data="topup_uzcard")
    b.button(text="⭐ Telegram Stars", callback_data="topup_stars")
    b.button(text="⬅️ Orqaga", callback_data="menu_back")
    b.adjust(2, 1, 1)
    return b.as_markup()


def admin_topup_decision_kb(tx_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Tasdiqlash", callback_data=f"approve_tx_{tx_id}")
    b.button(text="❌ Rad etish", callback_data=f"reject_tx_{tx_id}")
    b.adjust(2)
    return b.as_markup()


def admin_order_decision_kb(order_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Bajarildi", callback_data=f"done_order_{order_id}")
    b.button(text="❌ Bekor qilish", callback_data=f"cancel_order_{order_id}")
    b.adjust(2)
    return b.as_markup()
