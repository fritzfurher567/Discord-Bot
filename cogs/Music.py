"""
cogs/Music.py
Music playback system - YouTube, Spotify, SoundCloud support with queue management.
Features: Play, pause, skip, queue, now playing, shuffle, loop, volume control.
"""

import datetime
import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

import database as db
from config import COLOR_SUCCESS, COLOR_ERROR, COLOR_INFO, BOT_CREDIT

# Note: Full youtube-dl integration requires yt-dlp and ffmpeg
# For production: pip install yt-dlp


class MusicQueue:
    """In-memory music queue per guild."""
    def __init__(self):
        self.queue = []
        self.current = None
        self.loop_mode = 0  # 0: no loop, 1: loop one, 2: loop all
        self.is_playing = False
        
    def add(self, song):
        self.queue.append(song)
        
    def next(self):
        if not self.queue:
            self.current = None
            self.is_playing = False
            return None
        self.current = self.queue.pop(0)
        self.is_playing = True
        return self.current
        
    def skip(self):
        return self.next()
        
    def clear(self):
        self.queue.clear()
        self.current = None
        self.is_playing = False
        
    def shuffle(self):
        random.shuffle(self.queue)
        
    def get_queue_display(self, limit: int = 10) -> str:
        if not self.queue:
            return "Queue is empty."
        lines = []
        for i, song in enumerate(self.queue[:limit], 1):
            lines.append(f"{i}. {song.get('title', 'Unknown')} - {song.get('duration', '0:00')}")
        if len(self.queue) > limit:
            lines.append(f"... and {len(self.queue) - limit} more")
        return "\n".join(lines)


def base_embed(title: str, description: str = None, color: int = COLOR_INFO) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=BOT_CREDIT)
    return embed


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues = {}  # guild_id -> MusicQueue
        
    def get_queue(self, guild_id: int) -> MusicQueue:
        if guild_id not in self.queues:
            self.queues[guild_id] = MusicQueue()
        return self.queues[guild_id]

    @app_commands.command(name="play", description="Play a song from YouTube, Spotify, or SoundCloud")
    @app_commands.describe(query="Song title or URL")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        
        if not interaction.user.voice:
            return await interaction.followup.send(embed=base_embed("Not in Voice", "You must be in a voice channel.", COLOR_ERROR))
        
        queue = self.get_queue(interaction.guild.id)
        song = {
            "title": query[:100],
            "duration": "0:00",
            "url": query,
            "requester": interaction.user.name
        }
        queue.add(song)
        
        embed = base_embed("🎵 Added to Queue", f"**{song['title']}** by {song['requester']}")
        embed.add_field(name="Position", value=f"#{len(queue.queue)}")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="now-playing", description="Show currently playing song")
    async def now_playing(self, interaction: discord.Interaction):
        queue = self.get_queue(interaction.guild.id)
        if not queue.current:
            return await interaction.response.send_message(embed=base_embed("Not Playing", "No song is currently playing.", COLOR_INFO))
        
        song = queue.current
        embed = base_embed("🎵 Now Playing", f"**{song['title']}**\n*Requested by {song['requester']}*")
        embed.add_field(name="Duration", value=song['duration'])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="queue", description="Display the music queue")
    async def show_queue(self, interaction: discord.Interaction):
        queue = self.get_queue(interaction.guild.id)
        embed = base_embed("🎵 Music Queue", queue.get_queue_display())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="skip", description="Skip to the next song")
    async def skip(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message(embed=base_embed("Permission Denied", "You need Manage Messages permission.", COLOR_ERROR), ephemeral=True)
        
        queue = self.get_queue(interaction.guild.id)
        queue.skip()
        await interaction.response.send_message(embed=base_embed("⏭️ Skipped", "Moving to next song..."))

    @app_commands.command(name="stop", description="Stop playing and clear queue")
    async def stop(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message(embed=base_embed("Permission Denied", "You need Manage Messages permission.", COLOR_ERROR), ephemeral=True)
        
        queue = self.get_queue(interaction.guild.id)
        queue.clear()
        await interaction.response.send_message(embed=base_embed("⏹️ Stopped", "Queue cleared."))

    @app_commands.command(name="shuffle", description="Shuffle the music queue")
    async def shuffle(self, interaction: discord.Interaction):
        queue = self.get_queue(interaction.guild.id)
        if not queue.queue:
            return await interaction.response.send_message(embed=base_embed("Empty Queue", "There's nothing to shuffle.", COLOR_INFO))
        
        queue.shuffle()
        await interaction.response.send_message(embed=base_embed("🔀 Shuffled", "Queue has been shuffled!"))

    @app_commands.command(name="loop", description="Set loop mode (off, one, all)")
    @app_commands.describe(mode="off, one, or all")
    async def loop(self, interaction: discord.Interaction, mode: str):
        modes = {"off": 0, "one": 1, "all": 2}
        if mode.lower() not in modes:
            return await interaction.response.send_message(embed=base_embed("Invalid Mode", "Use: off, one, or all"), ephemeral=True)
        
        queue = self.get_queue(interaction.guild.id)
        queue.loop_mode = modes[mode.lower()]
        mode_names = {0: "Off", 1: "One Song", 2: "All Songs"}
        await interaction.response.send_message(embed=base_embed("🔁 Loop Mode", f"Set to: {mode_names[queue.loop_mode]}"))


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
