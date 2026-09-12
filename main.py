import os
import sqlite3
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip()
]

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

# ================= DATABASE =================

db = sqlite3.connect("bot.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    balance REAL DEFAULT 0
)
""")

db.commit()


def add_user(user_id, username):
    cur.execute(
        "INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)",
        (user_id, username)
    )
    db.commit()


def get_balance(user_id):
    cur.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    return row[0] if row else 0


# ================= KEYBOARDS =================

def main_menu():
    kb = ReplyKeyboardBuilder()

    kb.button(text="🚀 Nakrutka auto")
    kb.button(text="🎁 Gift/Premium")
    kb.button(text="📱 Virtual raqam")
    kb.button(text="⭐ Telegram Stars")
    kb.button(text="💳 Hisobni to‘ldirish")
    kb.button(text="💰 Balans")
    kb.button(text="📞 Qo‘llab-quvvatlash")

    kb.adjust(2, 2, 2, 1)

    return kb.as_markup(resize_keyboard=True)


def back_button():
    kb = InlineKeyboardBuilder()
    kb.button(text="↩️ Orqaga", callback_data="back")
    return kb.as_markup()


# ================= BOT =================

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):

    add_user(
        message.from_user.id,
        message.from_user.username
    )

    await message.answer(
        "👋 <b>Assalomu alaykum!</b>\n\n"
        "🔥 <b>PRO SMM BOT</b> ga xush kelibsiz!\n\n"
        "Bu yerda SMM xizmatlari, Telegram Gift, "
        "Premium, Stars va virtual raqam xizmatlaridan foydalanishingiz mumkin.\n\n"
        "👇 Kerakli bo‘limni tanlang:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


# ================= NAKRUTKA =================

@dp.message(F.text == "🚀 Nakrutka auto")
async def nakrutka(message: Message):

    kb = InlineKeyboardBuilder()

    kb.button(text="📸 Instagram", callback_data="smm_instagram")
    kb.button(text="🎵 TikTok", callback_data="smm_tiktok")
    kb.button(text="▶️ YouTube", callback_data="smm_youtube")
    kb.button(text="✈️ Telegram", callback_data="smm_telegram")
    kb.button(text="↩️ Orqaga", callback_data="back")

    kb.adjust(2, 2, 1)

    await message.answer(
        "🚀 <b>Nakrutka AUTO</b>\n\n"
        "Platformani tanlang:",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )


@dp.callback_query(F.data.startswith("smm_"))
async def smm_category(callback: CallbackQuery):

    category = callback.data.replace("smm_", "").title()

    await callback.message.edit_text(
        f"🚀 <b>{category}</b>\n\n"
        "⚡ Xizmatlar API orqali avtomatik yuklanadi.\n\n"
        "Hozircha xizmatlar modulini ulash bosqichidamiz.",
        parse_mode="HTML",
        reply_markup=back_button()
    )

    await callback.answer()


# ================= GIFT =================

@dp.message(F.text == "🎁 Gift/Premium")
async def gifts(message: Message):

    kb = InlineKeyboardBuilder()

    gifts_list = [
        ("💖 Yurak — 4 380 UZS", "gift_4380"),
        ("🧸 Ayiq — 4 380 UZS", "gift_4380"),
        ("🌹 Atirgul — 7 300 UZS", "gift_7300"),
        ("🎁 Sovg‘a — 7 300 UZS", "gift_7300"),
        ("🎂 Tort — 14 600 UZS", "gift_14600"),
        ("💐 Gul — 14 600 UZS", "gift_14600"),
        ("🚀 Raketa — 14 600 UZS", "gift_14600"),
        ("🍾 Shampan — 14 600 UZS", "gift_14600"),
        ("🏆 Kubok — 29 200 UZS", "gift_29200"),
        ("💎 Olmos — 29 200 UZS", "gift_29200"),
        ("💍 Gift ⭐100 — 29 200 UZS", "gift_29200"),
        ("⭐ Premium 1 oy — 44 999 UZS", "premium")
    ]

    for text, data in gifts_list:
        kb.button(text=text, callback_data=data)

    kb.button(text="↩️ Orqaga", callback_data="back")
    kb.adjust(2)

    await message.answer(
        "🎁 <b>Gift olish AUTO</b>\n\n"
        "✨ Avtomatik gift oling — keyin Stars ga almashtirish mumkin.\n\n"
        "Bo‘limni tanlang:",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )


@dp.callback_query(F.data.startswith("gift_"))
async def gift_buy(callback: CallbackQuery):

    price = callback.data.replace("gift_", "")

    await callback.message.edit_text(
        f"🎁 <b>Gift tanlandi</b>\n\n"
        f"💰 Narxi: <b>{price} UZS</b>\n\n"
        "📩 Qabul qiluvchi @username yuboring.",
        parse_mode="HTML",
        reply_markup=back_button()
    )

    await callback.answer()


@dp.callback_query(F.data == "premium")
async def premium(callback: CallbackQuery):

    await callback.message.edit_text(
        "⭐ <b>Telegram Premium — 1 oy</b>\n\n"
        "💰 Narxi: <b>44 999 UZS</b>\n\n"
        "📩 Qabul qiluvchi @username yuboring.",
        parse_mode="HTML",
        reply_markup=back_button()
    )

    await callback.answer()


# ================= BALANS =================

@dp.message(F.text == "💰 Balans")
async def balance(message: Message):

    bal = get_balance(message.from_user.id)

    await message.answer(
        f"💰 <b>Sizning balansingiz:</b>\n\n"
        f"💵 {bal:,.0f} UZS",
        parse_mode="HTML"
    )


# ================= TOP UP =================

@dp.message(F.text == "💳 Hisobni to‘ldirish")
async def topup(message: Message):

    await message.answer(
        "💳 <b>Hisobni to‘ldirish</b>\n\n"
        "🔐 To‘lovlar xavfsiz va tez qabul qilinadi.\n\n"
        "💳 HUMO\n"
        "💳 UZCARD\n"
        "⭐ Telegram Stars\n\n"
        "⚡ Avtomatik to‘lov tizimi tez orada ulanadi.",
        parse_mode="HTML"
    )


# ================= VIRTUAL NUMBER =================

@dp.message(F.text == "📱 Virtual raqam")
async def numbers(message: Message):

    await message.answer(
        "📱 <b>Virtual raqam</b>\n\n"
        "🇷🇺 Telegram\n"
        "🇺🇿 Uzbekistan\n"
        "🇺🇸 USA\n"
        "🇬🇧 UK\n\n"
        "⚡ Raqam olish tizimi API orqali ishlaydi.",
        parse_mode="HTML"
    )


# ================= STARS =================

@dp.message(F.text == "⭐ Telegram Stars")
async def stars(message: Message):

    kb = InlineKeyboardBuilder()

    for amount in [50, 100, 250, 500, 1000]:
        kb.button(
            text=f"⭐ {amount} Stars",
            callback_data=f"stars_{amount}"
        )

    kb.button(text="↩️ Orqaga", callback_data="back")
    kb.adjust(2)

    await message.answer(
        "⭐ <b>Telegram Stars</b>\n\n"
        "Kerakli paketni tanlang:",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )


# ================= SUPPORT =================

@dp.message(F.text == "📞 Qo‘llab-quvvatlash")
async def support(message: Message):

    await message.answer(
        "📞 <b>Qo‘llab-quvvatlash</b>\n\n"
        "Muammo yoki savol bo‘lsa admin bilan bog‘laning:\n"
        "👉 @xtuzs",
        parse_mode="HTML"
    )


# ================= BACK =================

@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):

    await callback.message.delete()

    await callback.message.answer(
        "🏠 <b>Asosiy menyu</b>\n\n"
        "Kerakli bo‘limni tanlang:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

    await callback.answer()


# ================= ADMIN =================

@dp.message(F.text == "/stats")
async def stats(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT SUM(balance) FROM users")
    total = cur.fetchone()[0] or 0

    await message.answer(
        "👨‍💼 <b>ADMIN STATISTIKA</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users}</b>\n"
        f"💰 Balanslar jami: <b>{total:,.0f} UZS</b>",
        parse_mode="HTML"
    )

# ================= RENDER PORT =================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"PRO SMM BOT OK")

    def log_message(self, format, *args):
        pass


def start_web_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


threading.Thread(target=start_web_server, daemon=True).start()

# ================= START =================

async def main():
    print("🔥 PRO SMM BOT ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
