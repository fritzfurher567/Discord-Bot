"""
main.py
Entry point for the bot. Loads environment variables, sets up intents,
loads all cogs, initializes the database, and starts the bot.

Run with:  python main.py
"""

import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database import init_db
from config import BOT_CREDIT

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
log = logging.getLogger("bot")

intents = discord.Intents.default()
intents.members = True          # required for join/leave events
intents.message_content = True  # required for prefix commands / message-based features

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

STARTUP_COGS = [
    "cogs.moderation",
    "cogs.tickets",
    "cogs.welcome",
    "cogs.embeds",
    "cogs.utility",
    "cogs.leveling",
    "cogs.reactionroles",
    "cogs.automod",
    "cogs.customcommands",
    "cogs.logging_cog",
    "cogs.reminders",
    "cogs.economy",
    "cogs.socialalerts",
]


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"the server | {BOT_CREDIT}")
    )
    try:
        synced = await bot.tree.sync()
        log.info(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        log.error(f"Failed to sync commands: {e}")

    log.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    log.info(BOT_CREDIT)


async def main():
    if not TOKEN:
        raise RuntimeError(
            "No DISCORD_TOKEN found. Copy .env.example to .env and add your bot token."
        )

    await init_db()

    async with bot:
        for cog in STARTUP_COGS:
            try:
                await bot.load_extension(cog)
                log.info(f"Loaded {cog}")
            except Exception as e:
                log.error(f"Failed to load {cog}: {e}")

        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
