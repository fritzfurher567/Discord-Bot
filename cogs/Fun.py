"""
cogs/Fun.py
Entertainment and fun commands: memes, jokes, insults, compliments,
random facts, and more.
"""

import datetime
import random
import aiohttp

import discord
from discord import app_commands
from discord.ext import commands

import database as db
from config import COLOR_SUCCESS, COLOR_ERROR, COLOR_INFO, BOT_CREDIT


def base_embed(title: str, description: str = None, color: int = COLOR_INFO) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=BOT_CREDIT)
    return embed


JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
    "What do you call a fake noodle? An impasta!",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "What do you call a bear with no teeth? A gummy bear!",
]

COMPLIMENTS = [
    "You're an awesome person!",
    "You light up the room!",
    "You deserve a hug right now!",
    "You're a gift to those around you!",
    "You're a smart cookie!",
    "You are awesome!",
    "You're one of a kind!",
    "Your perspective is refreshing!",
]

INSULTS = [
    "You're a bit of a knob, aren't you?",
    "I'd roast you, but my Mom would never forgive me.",
    "You're like a cloud. When you disappear, it's a beautiful day.",
    "I would agree with you, but then we'd both be wrong.",
    "You're the kind of person who makes other people look good by comparison.",
]

FACTS = [
    "Honey never spoils. Archaeologists have found 3,000-year-old honey in Egyptian tombs that was still edible!",
    "Octopuses have three hearts.",
    "A group of flamingos is called a 'flamboyance'.",
    "Bananas are berries, but strawberries aren't.",
    "A single bolt of lightning contains enough energy to toast 100,000 slices of bread.",
    "Dolphins have names for each other.",
    "Tardigrades (water bears) can survive in space.",
    "Sharks have been around longer than dinosaurs.",
]


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="joke", description="Tell a random joke")
    async def joke(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=base_embed("😂 Here's a Joke", random.choice(JOKES)))

    @app_commands.command(name="compliment", description="Send a compliment to someone")
    @app_commands.describe(user="User to compliment")
    async def compliment(self, interaction: discord.Interaction, user: discord.Member):
        compliment = random.choice(COMPLIMENTS)
        await interaction.response.send_message(embed=base_embed("💕 Compliment", f"{user.mention}, {compliment}"))

    @app_commands.command(name="roast", description="Get roasted (gently)")
    async def roast(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=base_embed("🔥 Roast", random.choice(INSULTS)))

    @app_commands.command(name="fact", description="Learn a random interesting fact")
    async def fact(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=base_embed("🧠 Did You Know?", random.choice(FACTS)))

    @app_commands.command(name="flip-text", description="Flip text upside down")
    @app_commands.describe(text="Text to flip")
    async def flip_text(self, interaction: discord.Interaction, text: str):
        flip_map = {
            'a': 'ɐ', 'b': 'q', 'c': 'ɔ', 'd': 'p', 'e': 'ǝ', 'f': 'ɟ', 'g': 'ƃ', 'h': 'ɥ', 'i': 'ᴉ', 'j': 'ɾ',
            'k': 'ʞ', 'l': 'l', 'm': 'ɯ', 'n': 'u', 'o': 'o', 'p': 'd', 'q': 'b', 'r': 'ɹ', 's': 's', 't': 'ʇ',
            'u': 'n', 'v': 'ʌ', 'w': 'ʍ', 'x': 'x', 'y': 'ʎ', 'z': 'z', '?': '¿', '!': '¡', '.': '˙'
        }
        flipped = ''.join(flip_map.get(c.lower(), c) for c in reversed(text))
        await interaction.response.send_message(embed=base_embed("🙃 Flipped Text", f"**Original:** {text}\n**Flipped:** {flipped}"))

    @app_commands.command(name="say", description="Make the bot say something")
    @app_commands.describe(message="Message to say")
    async def say(self, interaction: discord.Interaction, message: str):
        if len(message) > 2000:
            return await interaction.response.send_message(embed=base_embed("Too Long", "Message must be under 2000 characters.", COLOR_ERROR), ephemeral=True)
        await interaction.response.defer()
        await interaction.channel.send(message)
        await interaction.followup.send("✅ Message sent!")

    @app_commands.command(name="ascii", description="Convert text to ASCII art")
    @app_commands.describe(text="Text to convert (max 10 chars)")
    async def ascii(self, interaction: discord.Interaction, text: str):
        if len(text) > 10:
            return await interaction.response.send_message(embed=base_embed("Too Long", "Max 10 characters for ASCII art.", COLOR_ERROR), ephemeral=True)
        
        # Simple ASCII conversion
        ascii_map = {
            'a': '█████', 'b': '████', 'c': '███', 'd': '██', 'e': '█',
            'i': '█', 'o': '███', 'u': '██', 'v': '█ █', 'w': '█ █ █'
        }
        result = ""
        for char in text.lower():
            result += ascii_map.get(char, char) + " "
        
        await interaction.response.send_message(embed=base_embed("🎨 ASCII Art", f"```\n{result}\n```"))

    @app_commands.command(name="pp", description="Check your pp size (joke command)")
    async def pp(self, interaction: discord.Interaction):
        size = random.randint(1, 20)
        pp_display = "8" + "=" * size + "D"
        await interaction.response.send_message(embed=base_embed("📏 PP Size", f"**{interaction.user.name}:** {pp_display}"))

    @app_commands.command(name="ship", description="Ship two people (couple compatibility)")
    @app_commands.describe(user1="First person", user2="Second person")
    async def ship(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
        compatibility = random.randint(1, 100)
        ship_name = user1.name[:len(user1.name)//2] + user2.name[len(user2.name)//2:]
        
        hearts = "❤️" * (compatibility // 20)
        empty_hearts = "🤍" * (5 - (compatibility // 20))
        
        embed = base_embed("💕 Shipping", f"{user1.mention} + {user2.mention}")
        embed.add_field(name="Ship Name", value=ship_name, inline=False)
        embed.add_field(name="Compatibility", value=f"{compatibility}% {hearts}{empty_hearts}", inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
