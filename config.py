import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
SUPPORT_GROUP_ID = int(os.getenv("SUPPORT_GROUP_ID", "0") or 0)
DB_PATH = os.getenv("DB_PATH", "bot.db")

CARD_HUMO_NUMBER = os.getenv("CARD_HUMO_NUMBER", "")
CARD_UZCARD_NUMBER = os.getenv("CARD_UZCARD_NUMBER", "")
CARD_OWNER_NAME = os.getenv("CARD_OWNER_NAME", "")

# ---- Gift katalogi (nom, narx so'mda) ----
GIFT_CATALOG = {
    "heart": {"title": "💝 Yurak", "price": 4380},
    "bear": {"title": "🧸 Ayiq", "price": 4380},
    "rose": {"title": "🌹 Atirgul", "price": 7300},
    "gift": {"title": "🎁 Sovg'a", "price": 7300},
    "cake": {"title": "🎂 Tort", "price": 14600},
    "flowers": {"title": "💐 Gul", "price": 14600},
    "rocket": {"title": "🚀 Raketa", "price": 14600},
    "champagne": {"title": "🍾 Shampan", "price": 14600},
    "cup": {"title": "🏆 Kubok", "price": 29200},
    "diamond": {"title": "💎 Olmos", "price": 29200},
    "ring": {"title": "💍 Gift ⭐100", "price": 29200},
}

PREMIUM_PLANS = {
    "premium_1m": {"title": "Premium 1 oylik", "price": 44999},
    "premium_3m": {"title": "Premium 3 oylik", "price": 119999},
    "premium_12m": {"title": "Premium 12 oylik", "price": 349999},
}

# ---- Nakrutka xizmatlari (namunaviy narxlar — o'zingiznikiga moslang) ----
NAKRUTKA_SERVICES = {
    "tg_members": {"title": "📥 Telegram obunachi", "price_per_100": 5000},
    "tg_views": {"title": "👁 Telegram ko'rishlar", "price_per_100": 1500},
    "tg_reactions": {"title": "❤️ Telegram reaksiya", "price_per_100": 2000},
    "ig_followers": {"title": "📷 Instagram obunachi", "price_per_100": 8000},
    "ig_likes": {"title": "❤️ Instagram layk", "price_per_100": 3000},
}
