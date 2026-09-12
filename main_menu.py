from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🚀 Nakrutka avto")
    builder.button(text="🎁 Gift/Premium")
    builder.button(text="💳 Hisobni to'ldirish")
    builder.button(text="💰 Balans")
    builder.button(text="☎️ Qo'llab-quvvatlash")
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True)
