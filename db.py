import aiosqlite
from datetime import datetime
from config import DB_PATH

_CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    balance INTEGER DEFAULT 0,
    created_at TEXT
)
"""

_CREATE_TRANSACTIONS = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    method TEXT,
    status TEXT DEFAULT 'pending',
    receipt_file_id TEXT,
    created_at TEXT
)
"""

_CREATE_ORDERS = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    order_type TEXT,
    item_key TEXT,
    quantity INTEGER DEFAULT 1,
    target TEXT,
    price INTEGER,
    status TEXT DEFAULT 'pending',
    created_at TEXT
)
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(_CREATE_USERS)
        await db.execute(_CREATE_TRANSACTIONS)
        await db.execute(_CREATE_ORDERS)
        await db.commit()


async def get_or_create_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if row is None:
            await db.execute(
                "INSERT INTO users (user_id, username, full_name, balance, created_at) VALUES (?, ?, ?, 0, ?)",
                (user_id, username, full_name, datetime.utcnow().isoformat()),
            )
            await db.commit()


async def get_balance(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else 0


async def change_balance(user_id: int, delta: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (delta, user_id))
        await db.commit()


async def create_transaction(user_id: int, amount: int, method: str, receipt_file_id: str = None) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO transactions (user_id, amount, method, receipt_file_id, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, method, receipt_file_id, datetime.utcnow().isoformat()),
        )
        await db.commit()
        return cur.lastrowid


async def set_transaction_status(tx_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE transactions SET status = ? WHERE id = ?", (status, tx_id))
        await db.commit()


async def get_transaction(tx_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
        return await cur.fetchone()


async def create_order(user_id: int, order_type: str, item_key: str, price: int, target: str = None, quantity: int = 1) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO orders (user_id, order_type, item_key, quantity, target, price, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, order_type, item_key, quantity, target, price, datetime.utcnow().isoformat()),
        )
        await db.commit()
        return cur.lastrowid


async def set_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        await db.commit()
