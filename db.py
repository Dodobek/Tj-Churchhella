"""
Слой хранения данных: язык пользователя, корзина, история заказов.
Используется SQLite — простой файл базы данных, без внешнего сервера.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from config import DB_PATH


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                lang TEXT
            );

            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_key TEXT NOT NULL,
                variant_key TEXT,
                qty_kg REAL NOT NULL,
                price_tjs REAL
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                lang TEXT,
                items_json TEXT NOT NULL,
                total_str TEXT,
                created_at TEXT NOT NULL
            );
            """
        )


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────
# ПОЛЬЗОВАТЕЛИ / ЯЗЫК
# ──────────────────────────────────────────────────────────────────────────


def get_user_lang(user_id: int) -> str | None:
    with _connect() as conn:
        row = conn.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return row["lang"] if row else None


def set_user_lang(user_id: int, username: str | None, lang: str) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, username, lang) VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET lang = excluded.lang, username = excluded.username
            """,
            (user_id, username, lang),
        )


# ──────────────────────────────────────────────────────────────────────────
# КОРЗИНА
# ──────────────────────────────────────────────────────────────────────────


def add_to_cart(user_id: int, product_key: str, variant_key: str | None, qty_kg: float, price_tjs: float | None) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO cart_items (user_id, product_key, variant_key, qty_kg, price_tjs) VALUES (?, ?, ?, ?, ?)",
            (user_id, product_key, variant_key, qty_kg, price_tjs),
        )


def get_cart(user_id: int) -> list[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute(
            "SELECT * FROM cart_items WHERE user_id = ? ORDER BY id", (user_id,)
        ).fetchall()


def clear_cart(user_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))


# ──────────────────────────────────────────────────────────────────────────
# ЗАКАЗЫ
# ──────────────────────────────────────────────────────────────────────────


def create_order(user_id: int, username: str | None, lang: str, items: list[dict], total_str: str) -> int:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO orders (user_id, username, lang, items_json, total_str, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, lang, json.dumps(items, ensure_ascii=False), total_str, datetime.utcnow().isoformat()),
        )
        return cur.lastrowid


def get_user_orders(user_id: int) -> list[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user_id,)
        ).fetchall()
