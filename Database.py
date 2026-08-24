"""
database.py
Handles all persistent storage using SQLite (via aiosqlite).
Stores per-guild settings, warnings, and ticket records.
"""

import aiosqlite

DB_PATH = "bot_data.db"


async def init_db():
    """Create all tables if they don't already exist. Call this once on bot startup."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id INTEGER PRIMARY KEY,
                welcome_channel INTEGER,
                welcome_message TEXT DEFAULT 'Welcome {user} to {server}! We now have {membercount} members.',
                goodbye_channel INTEGER,
                goodbye_message TEXT DEFAULT '{user} has left {server}. We now have {membercount} members.',
                dm_on_join INTEGER DEFAULT 0,
                dm_on_join_message TEXT DEFAULT 'Welcome to {server}! Glad to have you here.',
                dm_on_leave INTEGER DEFAULT 0,
                dm_on_leave_message TEXT DEFAULT 'Sorry to see you leave {server}!',
                mod_log_channel INTEGER,
                mute_role_id INTEGER,
                ticket_category_id INTEGER,
                ticket_log_channel INTEGER,
                ticket_panel_channel INTEGER,
                server_log_channel INTEGER,
                levelup_channel INTEGER
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                timestamp TEXT NOT NULL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                category TEXT,
                priority TEXT,
                status TEXT DEFAULT 'open',
                claimed_by INTEGER,
                created_at TEXT NOT NULL
            )
        """)

        # ---- Leveling ----
        await db.execute("""
            CREATE TABLE IF NOT EXISTS levels (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                last_xp_time TEXT,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS level_roles (
                guild_id INTEGER NOT NULL,
                level INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                PRIMARY KEY (guild_id, level)
            )
        """)

        # ---- Reaction roles ----
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reaction_roles (
                guild_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                emoji TEXT NOT NULL,
                role_id INTEGER NOT NULL,
                PRIMARY KEY (message_id, emoji)
            )
        """)

        # ---- Auto-moderation ----
        await db.execute("""
            CREATE TABLE IF NOT EXISTS automod_config (
                guild_id INTEGER PRIMARY KEY,
                banned_words TEXT DEFAULT '',
                anti_invite INTEGER DEFAULT 0,
                caps_filter INTEGER DEFAULT 0,
                mention_limit INTEGER DEFAULT 0
            )
        """)

        # ---- Custom commands ----
        await db.execute("""
            CREATE TABLE IF NOT EXISTS custom_commands (
                guild_id INTEGER NOT NULL,
                trigger TEXT NOT NULL,
                response TEXT NOT NULL,
                PRIMARY KEY (guild_id, trigger)
            )
        """)

        # ---- Reminders ----
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                guild_id INTEGER,
                remind_at TEXT NOT NULL,
                message TEXT
            )
        """)

        # ---- Economy ----
        await db.execute("""
            CREATE TABLE IF NOT EXISTS economy (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                balance INTEGER DEFAULT 0,
                last_daily TEXT,
                last_work TEXT,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS shop_items (
                guild_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                price INTEGER NOT NULL,
                role_id INTEGER,
                PRIMARY KEY (guild_id, item_name)
            )
        """)

        # ---- Social alerts ----
        await db.execute("""
            CREATE TABLE IF NOT EXISTS youtube_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                yt_channel_id TEXT NOT NULL,
                last_video_id TEXT,
                UNIQUE(guild_id, yt_channel_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS twitch_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                twitch_username TEXT NOT NULL,
                is_live INTEGER DEFAULT 0,
                UNIQUE(guild_id, twitch_username)
            )
        """)

        await db.commit()


async def get_guild_config(guild_id: int) -> dict:
    """Return the config row for a guild as a dict, creating a default row if missing."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM guild_config WHERE guild_id = ?", (guild_id,))
        row = await cursor.fetchone()
        if row is None:
            await db.execute("INSERT INTO guild_config (guild_id) VALUES (?)", (guild_id,))
            await db.commit()
            cursor = await db.execute("SELECT * FROM guild_config WHERE guild_id = ?", (guild_id,))
            row = await cursor.fetchone()
        return dict(row)


async def update_guild_config(guild_id: int, **kwargs):
    """Update arbitrary columns in guild_config for a guild. Pass column=value kwargs."""
    if not kwargs:
        return
    await get_guild_config(guild_id)  # ensure row exists
    columns = ", ".join(f"{key} = ?" for key in kwargs.keys())
    values = list(kwargs.values())
    values.append(guild_id)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE guild_config SET {columns} WHERE guild_id = ?", values)
        await db.commit()


async def add_warning(guild_id: int, user_id: int, moderator_id: int, reason: str, timestamp: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO warnings (guild_id, user_id, moderator_id, reason, timestamp) VALUES (?, ?, ?, ?, ?)",
            (guild_id, user_id, moderator_id, reason, timestamp)
        )
        await db.commit()
        return cursor.lastrowid


async def get_warnings(guild_id: int, user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM warnings WHERE guild_id = ? AND user_id = ? ORDER BY id DESC",
            (guild_id, user_id)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def clear_warnings(guild_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM warnings WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
        await db.commit()


async def remove_warning(guild_id: int, warning_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM warnings WHERE guild_id = ? AND id = ?", (guild_id, warning_id)
        )
        await db.commit()
        return cursor.rowcount > 0


async def create_ticket(guild_id: int, channel_id: int, user_id: int, category: str, priority: str, timestamp: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO tickets (guild_id, channel_id, user_id, category, priority, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, 'open', ?)",
            (guild_id, channel_id, user_id, category, priority, timestamp)
        )
        await db.commit()
        return cursor.lastrowid


async def get_ticket_by_channel(channel_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM tickets WHERE channel_id = ?", (channel_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def claim_ticket(channel_id: int, moderator_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE tickets SET claimed_by = ? WHERE channel_id = ?", (moderator_id, channel_id))
        await db.commit()


async def close_ticket(channel_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE tickets SET status = 'closed' WHERE channel_id = ?", (channel_id,))
        await db.commit()


async def set_ticket_priority(channel_id: int, priority: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE tickets SET priority = ? WHERE channel_id = ?", (priority, channel_id))
        await db.commit()


async def get_open_ticket_for_user(guild_id: int, user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM tickets WHERE guild_id = ? AND user_id = ? AND status = 'open'",
            (guild_id, user_id)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


# ==================== LEVELING ====================

async def get_level_data(guild_id: int, user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM levels WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
        row = await cursor.fetchone()
        if row is None:
            await db.execute("INSERT INTO levels (guild_id, user_id, xp, level) VALUES (?, ?, 0, 0)", (guild_id, user_id))
            await db.commit()
            return {"guild_id": guild_id, "user_id": user_id, "xp": 0, "level": 0, "last_xp_time": None}
        return dict(row)


async def update_xp(guild_id: int, user_id: int, xp: int, level: int, last_xp_time: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE levels SET xp = ?, level = ?, last_xp_time = ? WHERE guild_id = ? AND user_id = ?",
            (xp, level, last_xp_time, guild_id, user_id)
        )
        await db.commit()


async def get_level_leaderboard(guild_id: int, limit: int = 10) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM levels WHERE guild_id = ? ORDER BY xp DESC LIMIT ?", (guild_id, limit)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def set_level_role(guild_id: int, level: int, role_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO level_roles (guild_id, level, role_id) VALUES (?, ?, ?) "
            "ON CONFLICT(guild_id, level) DO UPDATE SET role_id = excluded.role_id",
            (guild_id, level, role_id)
        )
        await db.commit()


async def get_level_roles(guild_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM level_roles WHERE guild_id = ? ORDER BY level ASC", (guild_id,))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def remove_level_role(guild_id: int, level: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM level_roles WHERE guild_id = ? AND level = ?", (guild_id, level))
        await db.commit()
        return cursor.rowcount > 0


# ==================== REACTION ROLES ====================

async def add_reaction_role(guild_id: int, message_id: int, emoji: str, role_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO reaction_roles (guild_id, message_id, emoji, role_id) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(message_id, emoji) DO UPDATE SET role_id = excluded.role_id",
            (guild_id, message_id, emoji, role_id)
        )
        await db.commit()


async def remove_reaction_role(message_id: int, emoji: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM reaction_roles WHERE message_id = ? AND emoji = ?", (message_id, emoji))
        await db.commit()
        return cursor.rowcount > 0


async def get_reaction_role(message_id: int, emoji: str) -> int | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT role_id FROM reaction_roles WHERE message_id = ? AND emoji = ?", (message_id, emoji))
        row = await cursor.fetchone()
        return row[0] if row else None


# ==================== AUTOMOD ====================

async def get_automod_config(guild_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM automod_config WHERE guild_id = ?", (guild_id,))
        row = await cursor.fetchone()
        if row is None:
            await db.execute("INSERT INTO automod_config (guild_id) VALUES (?)", (guild_id,))
            await db.commit()
            cursor = await db.execute("SELECT * FROM automod_config WHERE guild_id = ?", (guild_id,))
            row = await cursor.fetchone()
        return dict(row)


async def update_automod_config(guild_id: int, **kwargs):
    if not kwargs:
        return
    await get_automod_config(guild_id)
    columns = ", ".join(f"{key} = ?" for key in kwargs.keys())
    values = list(kwargs.values())
    values.append(guild_id)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE automod_config SET {columns} WHERE guild_id = ?", values)
        await db.commit()


# ==================== CUSTOM COMMANDS ====================

async def add_custom_command(guild_id: int, trigger: str, response: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO custom_commands (guild_id, trigger, response) VALUES (?, ?, ?) "
            "ON CONFLICT(guild_id, trigger) DO UPDATE SET response = excluded.response",
            (guild_id, trigger.lower(), response)
        )
        await db.commit()


async def remove_custom_command(guild_id: int, trigger: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM custom_commands WHERE guild_id = ? AND trigger = ?", (guild_id, trigger.lower())
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_custom_command(guild_id: int, trigger: str) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT response FROM custom_commands WHERE guild_id = ? AND trigger = ?", (guild_id, trigger.lower())
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def list_custom_commands(guild_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM custom_commands WHERE guild_id = ? ORDER BY trigger ASC", (guild_id,))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


# ==================== REMINDERS ====================

async def add_reminder(user_id: int, channel_id: int, guild_id: int, remind_at: str, message: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO reminders (user_id, channel_id, guild_id, remind_at, message) VALUES (?, ?, ?, ?, ?)",
            (user_id, channel_id, guild_id, remind_at, message)
        )
        await db.commit()
        return cursor.lastrowid


async def get_due_reminders(now_iso: str) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM reminders WHERE remind_at <= ?", (now_iso,))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def delete_reminder(reminder_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        await db.commit()


# ==================== ECONOMY ====================

async def get_balance_data(guild_id: int, user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM economy WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
        row = await cursor.fetchone()
        if row is None:
            await db.execute("INSERT INTO economy (guild_id, user_id, balance) VALUES (?, ?, 0)", (guild_id, user_id))
            await db.commit()
            return {"guild_id": guild_id, "user_id": user_id, "balance": 0, "last_daily": None, "last_work": None}
        return dict(row)


async def update_balance(guild_id: int, user_id: int, new_balance: int):
    await get_balance_data(guild_id, user_id)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE economy SET balance = ? WHERE guild_id = ? AND user_id = ?", (new_balance, guild_id, user_id)
        )
        await db.commit()


async def set_last_daily(guild_id: int, user_id: int, timestamp: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE economy SET last_daily = ? WHERE guild_id = ? AND user_id = ?", (timestamp, guild_id, user_id))
        await db.commit()


async def set_last_work(guild_id: int, user_id: int, timestamp: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE economy SET last_work = ? WHERE guild_id = ? AND user_id = ?", (timestamp, guild_id, user_id))
        await db.commit()


async def get_economy_leaderboard(guild_id: int, limit: int = 10) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM economy WHERE guild_id = ? ORDER BY balance DESC LIMIT ?", (guild_id, limit)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def add_shop_item(guild_id: int, item_name: str, price: int, role_id: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO shop_items (guild_id, item_name, price, role_id) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(guild_id, item_name) DO UPDATE SET price = excluded.price, role_id = excluded.role_id",
            (guild_id, item_name.lower(), price, role_id)
        )
        await db.commit()


async def get_shop_items(guild_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM shop_items WHERE guild_id = ? ORDER BY price ASC", (guild_id,))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_shop_item(guild_id: int, item_name: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM shop_items WHERE guild_id = ? AND item_name = ?", (guild_id, item_name.lower())
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def remove_shop_item(guild_id: int, item_name: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM shop_items WHERE guild_id = ? AND item_name = ?", (guild_id, item_name.lower())
        )
        await db.commit()
        return cursor.rowcount > 0


# ==================== SOCIAL ALERTS ====================

async def add_youtube_alert(guild_id: int, channel_id: int, yt_channel_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO youtube_alerts (guild_id, channel_id, yt_channel_id) VALUES (?, ?, ?) "
            "ON CONFLICT(guild_id, yt_channel_id) DO UPDATE SET channel_id = excluded.channel_id",
            (guild_id, channel_id, yt_channel_id)
        )
        await db.commit()


async def get_youtube_alerts() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM youtube_alerts")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def update_youtube_last_video(alert_id: int, video_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE youtube_alerts SET last_video_id = ? WHERE id = ?", (video_id, alert_id))
        await db.commit()


async def remove_youtube_alert(guild_id: int, yt_channel_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM youtube_alerts WHERE guild_id = ? AND yt_channel_id = ?", (guild_id, yt_channel_id)
        )
        await db.commit()
        return cursor.rowcount > 0


async def add_twitch_alert(guild_id: int, channel_id: int, twitch_username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO twitch_alerts (guild_id, channel_id, twitch_username) VALUES (?, ?, ?) "
            "ON CONFLICT(guild_id, twitch_username) DO UPDATE SET channel_id = excluded.channel_id",
            (guild_id, channel_id, twitch_username.lower())
        )
        await db.commit()


async def get_twitch_alerts() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM twitch_alerts")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def update_twitch_live_state(alert_id: int, is_live: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE twitch_alerts SET is_live = ? WHERE id = ?", (int(is_live), alert_id))
        await db.commit()


async def remove_twitch_alert(guild_id: int, twitch_username: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM twitch_alerts WHERE guild_id = ? AND twitch_username = ?", (guild_id, twitch_username.lower())
        )
        await db.commit()
        return cursor.rowcount > 0
