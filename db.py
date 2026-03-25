# db.py
import time
import aiosqlite

DB_PATH = "bot.db"

MUTE_SECONDS = 60 * 10  # 10 минут


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS warnings (
                user_id INTEGER PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS mutes (
                user_id INTEGER PRIMARY KEY,
                until INTEGER NOT NULL
            )
            """
        )
        await db.commit()


# ---------- пользователи ----------

async def add_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,),
        )
        await db.commit()


async def get_all_users() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
    return [row[0] for row in rows]


async def get_users_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
    return row[0] if row else 0


# ---------- предупреждения ----------

async def add_warning(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO warnings (user_id, count) VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE SET count = count + 1
            """,
            (user_id,),
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT count FROM warnings WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
    return row[0] if row else 0


async def get_warning_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT count FROM warnings WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
    return row[0] if row else 0


async def get_warned_users_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM warnings")
        row = await cursor.fetchone()
    return row[0] if row else 0


# ---------- муты ----------

async def mute_user(user_id: int):
    until = int(time.time()) + MUTE_SECONDS
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO mutes (user_id, until) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET until = excluded.until
            """,
            (user_id, until),
        )
        await db.commit()


async def is_muted(user_id: int) -> bool:
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT until FROM mutes WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()

        if not row:
            return False

        if row[0] <= now:
            await db.execute("DELETE FROM mutes WHERE user_id = ?", (user_id,))
            await db.commit()
            return False

    return True


async def get_muted_users_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM mutes")
        row = await cursor.fetchone()
    return row[0] if row else 0
