# -*- coding: utf-8 -*-
"""SQLite persistence for Bot Factory admin."""
from __future__ import annotations

import os
from pathlib import Path

import aiosqlite

DB_PATH = os.getenv("DB_PATH") or str(Path(os.getenv("RAILWAY_VOLUME_MOUNT_PATH") or ".") / "factory_data.db")


async def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                is_banned INTEGER DEFAULT 0,
                builds_count INTEGER DEFAULT 0,
                last_template TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS disabled_templates (
                template_key TEXT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS disabled_menus (
                menu_key TEXT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS disabled_categories (
                category TEXT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS build_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                template_key TEXT,
                brand TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        await db.commit()


async def get_setting(key: str, default: str = "") -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cur.fetchone()
        return row[0] if row else default


async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )
        await db.commit()


async def is_bot_enabled() -> bool:
    return (await get_setting("bot_enabled", "1")) != "0"


async def set_bot_enabled(on: bool):
    await set_setting("bot_enabled", "1" if on else "0")


async def is_maintenance() -> bool:
    return (await get_setting("maintenance", "0")) == "1"


async def set_maintenance(on: bool):
    await set_setting("maintenance", "1" if on else "0")


async def upsert_user(user_id: int, username: str | None, full_name: str | None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, username, full_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, username or "", full_name or ""),
        )
        await db.commit()


async def is_banned(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return bool(row and row[0])


async def set_banned(user_id: int, banned: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, is_banned) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET is_banned = excluded.is_banned, updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, 1 if banned else 0),
        )
        await db.commit()


async def count_users(only_banned: bool = False) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        if only_banned:
            cur = await db.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1")
        else:
            cur = await db.execute("SELECT COUNT(*) FROM users")
        return int((await cur.fetchone())[0])


async def users_page(page: int = 0, per_page: int = 8, only_banned: bool = False):
    offset = page * per_page
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if only_banned:
            cur = await db.execute(
                "SELECT * FROM users WHERE is_banned = 1 ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                (per_page, offset),
            )
        else:
            cur = await db.execute(
                "SELECT * FROM users ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                (per_page, offset),
            )
        return [dict(r) for r in await cur.fetchall()]


async def find_users(query: str, limit: int = 15):
    q = (query or "").strip()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if q.isdigit():
            cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (int(q),))
        else:
            like = f"%{q}%"
            cur = await db.execute(
                "SELECT * FROM users WHERE username LIKE ? OR full_name LIKE ? ORDER BY updated_at DESC LIMIT ?",
                (like, like, limit),
            )
        return [dict(r) for r in await cur.fetchall()]


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def bump_build(user_id: int, template_key: str, brand: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET builds_count = builds_count + 1, last_template = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (template_key, user_id),
        )
        await db.execute(
            "INSERT INTO build_logs (user_id, template_key, brand) VALUES (?, ?, ?)",
            (user_id, template_key, brand),
        )
        await db.commit()


async def is_template_enabled(key: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT 1 FROM disabled_templates WHERE template_key = ?", (key,))
        return (await cur.fetchone()) is None


async def set_template_enabled(key: str, enabled: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        if enabled:
            await db.execute("DELETE FROM disabled_templates WHERE template_key = ?", (key,))
        else:
            await db.execute(
                "INSERT OR IGNORE INTO disabled_templates (template_key) VALUES (?)", (key,)
            )
        await db.commit()


async def is_menu_enabled(key: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT 1 FROM disabled_menus WHERE menu_key = ?", (key,))
        return (await cur.fetchone()) is None


async def set_menu_enabled(key: str, enabled: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        if enabled:
            await db.execute("DELETE FROM disabled_menus WHERE menu_key = ?", (key,))
        else:
            await db.execute("INSERT OR IGNORE INTO disabled_menus (menu_key) VALUES (?)", (key,))
        await db.commit()


async def is_category_enabled(cat: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT 1 FROM disabled_categories WHERE category = ?", (cat,))
        return (await cur.fetchone()) is None


async def set_category_enabled(cat: str, enabled: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        if enabled:
            await db.execute("DELETE FROM disabled_categories WHERE category = ?", (cat,))
        else:
            await db.execute("INSERT OR IGNORE INTO disabled_categories (category) VALUES (?)", (cat,))
        await db.commit()


async def recent_builds(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM build_logs ORDER BY id DESC LIMIT ?", (limit,)
        )
        return [dict(r) for r in await cur.fetchall()]


async def count_builds() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM build_logs")
        return int((await cur.fetchone())[0])
