"""
cogs/Multex.py
Advanced Multex-style features: Roblox group management, background checks,
automated admin tools, and enterprise-grade security checks.
"""

import datetime
import aiohttp
import random

import discord
from discord import app_commands
from discord.ext import commands

import database as db
from config import COLOR_SUCCESS, COLOR_ERROR, COLOR_INFO, BOT_CREDIT


def base_embed(title: str, description: str = None, color: int = COLOR_INFO) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=BOT_CREDIT)
    return embed


async def check_roblox_account_safety(roblox_id: int) -> dict:
    """Check if a Roblox account has red flags (limited, banned, new, etc)"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://users.roblox.com/v1/users/{roblox_id}") as resp:
                if resp.status != 200:
                    return {"safe": False, "flags": ["Account not found"]}
                data = await resp.json()
                
                flags = []
                if data.get("description", "").lower() in ["limited", "banned"]:
                    flags.append("Account may be limited")
                
                return {"safe": len(flags) == 0, "flags": flags, "account_age": data.get("created", "Unknown")}
    except:
        return {"safe": None, "flags": ["API error"], "account_age": "Unknown"}


class Multex(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ==================== BACKGROUND CHECKS ====================

    @app_commands.command(name="bgcheck", description="Run an automated background check on a member")
    @app_commands.describe(member="Member to check")
    @app_commands.checks.has_permissions(administrator=True)
    async def background_check(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer()
        
        # Check Discord account age
        account_age = (datetime.datetime.utcnow() - member.created_at).days
        discord_flags = []
        
        if account_age < 7:
            discord_flags.append("⚠️ Very new Discord account (< 7 days)")
        if member.bot:
            discord_flags.append("⚠️ Bot account")
        if not member.avatar:
            discord_flags.append("⚠️ No profile picture")
        
        # Check Roblox verification
        roblox_data = await db.get_roblox_verification(interaction.guild.id, member.id)
        roblox_flags = []
        roblox_status = "✅ Verified"
        
        if not roblox_data:
            roblox_status = "❌ Not Verified"
            roblox_flags.append("No Roblox account linked")
        else:
            roblox_safety = await check_roblox_account_safety(roblox_data["roblox_id"])
            if not roblox_safety.get("safe"):
                roblox_flags.extend(roblox_safety.get("flags", []))
            roblox_status = f"✅ {roblox_data['roblox_username']}"
        
        # Check moderation history
        warnings = await db.get_warnings(interaction.guild.id, member.id)
        mod_flags = []
        if len(warnings) > 0:
            mod_flags.append(f"⚠️ {len(warnings)} warning(s)")
        
        # Build report
        embed = base_embed("🔍 Background Check Report", f"**User:** {member.mention}")
        embed.add_field(name="📱 Discord Account", value=f"Age: {account_age} days\n{chr(10).join(discord_flags) if discord_flags else '✅ Clean'}", inline=False)
        embed.add_field(name="🎮 Roblox Status", value=f"{roblox_status}\n{chr(10).join(roblox_flags) if roblox_flags else '✅ Clean'}", inline=False)
        embed.add_field(name="⚖️ Moderation History", value=f"{chr(10).join(mod_flags) if mod_flags else '✅ Clean'}", inline=False)
        
        risk_level = "🟢 LOW"
        if len(discord_flags) + len(roblox_flags) + len(mod_flags) >= 3:
            risk_level = "🔴 HIGH"
        elif len(discord_flags) + len(roblox_flags) + len(mod_flags) >= 1:
            risk_level = "🟡 MEDIUM"
        
        embed.add_field(name="Risk Level", value=risk_level, inline=False)
        await interaction.followup.send(embed=embed)

    # ==================== ROBLOX GROUP MANAGEMENT ====================

    @app_commands.command(name="group-setrank", description="Set a member's rank in a Roblox group")
    @app_commands.describe(member="Discord member", rank="Rank name")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def group_set_rank(self, interaction: discord.Interaction, member: discord.Member, rank: str):
        roblox_data = await db.get_roblox_verification(interaction.guild.id, member.id)
        if not roblox_data:
            return await interaction.response.send_message(embed=base_embed("Not Verified", "User hasn't verified a Roblox account.", COLOR_ERROR), ephemeral=True)
        
        ranks = await db.get_ranks(interaction.guild.id)
        rank_match = None
        for r in ranks:
            if r["rank_name"].lower() == rank.lower():
                rank_match = r
                break
        
        if not rank_match:
            return await interaction.response.send_message(embed=base_embed("Invalid Rank", f"Available ranks: {', '.join(r['rank_name'] for r in ranks)}", COLOR_ERROR), ephemeral=True)
        
        # Award the rank role
        role = interaction.guild.get_role(rank_match["role_id"])
        if role:
            try:
                await member.add_roles(role, reason=f"Ranked to {rank}")
            except discord.Forbidden:
                pass
        
        await interaction.response.send_message(embed=base_embed("✅ Rank Set", f"{member.mention} is now a **{rank}**", COLOR_SUCCESS))

    @app_commands.command(name="group-transfer", description="Transfer member to a different division")
    @app_commands.describe(member="Discord member", division="Target division")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def group_transfer(self, interaction: discord.Interaction, member: discord.Member, division: str):
        divisions = await db.get_divisions(interaction.guild.id)
        target_div = None
        for d in divisions:
            if d["division_name"].lower() == division.lower():
                target_div = d
                break
        
        if not target_div:
            return await interaction.response.send_message(embed=base_embed("Invalid Division", f"Available divisions: {', '.join(d['division_name'] for d in divisions)}", COLOR_ERROR), ephemeral=True)
        
        # Remove old division roles and add new one
        for d in divisions:
            old_role = interaction.guild.get_role(d["role_id"])
            if old_role and old_role in member.roles:
                try:
                    await member.remove_roles(old_role)
                except discord.Forbidden:
                    pass
        
        new_role = interaction.guild.get_role(target_div["role_id"])
        if new_role:
            try:
                await member.add_roles(new_role, reason=f"Transferred to {division}")
            except discord.Forbidden:
                pass
        
        await interaction.response.send_message(embed=base_embed("✅ Transfer Complete", f"{member.mention} transferred to **{division}**", COLOR_SUCCESS))

    # ==================== AUTOMATED MODERATION ====================

    @app_commands.command(name="auto-kick-new-accounts", description="Auto-kick accounts younger than N days")
    @app_commands.describe(days="Minimum account age in days")
    @app_commands.checks.has_permissions(administrator=True)
    async def auto_kick_new(self, interaction: discord.Interaction, days: int):
        config = await db.get_guild_config(interaction.guild.id)
        await db.update_guild_config(interaction.guild.id, auto_kick_new_accounts_days=days)
        await interaction.response.send_message(embed=base_embed("✅ Config Updated", f"Will auto-kick accounts < {days} days old", COLOR_SUCCESS))

    @app_commands.command(name="require-verification", description="Require Roblox verification before access")
    @app_commands.describe(enabled="True/False")
    @app_commands.checks.has_permissions(administrator=True)
    async def require_verification(self, interaction: discord.Interaction, enabled: bool):
        await db.update_guild_config(interaction.guild.id, require_roblox_verification=enabled)
        status = "✅ ENABLED" if enabled else "❌ DISABLED"
        await interaction.response.send_message(embed=base_embed("Verification Requirement", f"Status: {status}", COLOR_SUCCESS))

    # ==================== ANALYTICS & STATISTICS ====================

    @app_commands.command(name="server-stats", description="View detailed server statistics")
    async def server_stats(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # Count verified members
        verified_count = 0
        unverified_count = 0
        for member in guild.members:
            if await db.get_roblox_verification(guild.id, member.id):
                verified_count += 1
            else:
                unverified_count += 1
        
        # Get moderation stats
        audit_entries = await db.get_recent_audit_entries(guild.id, limit=100)
        
        embed = base_embed("📊 Server Statistics", f"**{guild.name}**")
        embed.add_field(name="Members", value=f"Total: {guild.member_count}\n✅ Verified: {verified_count}\n❌ Unverified: {unverified_count}", inline=False)
        embed.add_field(name="Channels", value=f"Text: {len(guild.text_channels)}\nVoice: {len(guild.voice_channels)}", inline=False)
        embed.add_field(name="Recent Actions", value=f"Logged: {len(audit_entries)}", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="member-info", description="Get detailed info on a member")
    @app_commands.describe(member="Member to inspect")
    async def member_info(self, interaction: discord.Interaction, member: discord.Member):
        joined_at = member.joined_at.strftime("%Y-%m-%d") if member.joined_at else "Unknown"
        created_at = member.created_at.strftime("%Y-%m-%d") if member.created_at else "Unknown"
        
        warnings = await db.get_warnings(interaction.guild.id, member.id)
        roblox = await db.get_roblox_verification(interaction.guild.id, member.id)
        
        embed = base_embed(f"👤 Member Info - {member}", f"ID: {member.id}")
        embed.add_field(name="Account Created", value=created_at, inline=False)
        embed.add_field(name="Joined Server", value=joined_at, inline=False)
        embed.add_field(name="Roles", value=f"{len(member.roles)} roles" if member.roles else "None", inline=False)
        embed.add_field(name="Warnings", value=f"{len(warnings)} warning(s)", inline=False)
        embed.add_field(name="Roblox Account", value=f"✅ {roblox['roblox_username']}" if roblox else "❌ Not Verified", inline=False)
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        await interaction.response.send_message(embed=embed)

    # ==================== ALERTS & SECURITY ====================

    @app_commands.command(name="alert-on-join", description="Get alerted when new members join")
    @app_commands.describe(channel="Alert channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def alert_on_join(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await db.update_guild_config(interaction.guild.id, join_alert_channel=channel.id)
        await interaction.response.send_message(embed=base_embed("✅ Config Updated", f"Join alerts will be sent to {channel.mention}", COLOR_SUCCESS))

    @app_commands.command(name="set-mod-role", description="Set the moderator role for automated tasks")
    @app_commands.describe(role="Moderator role")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_mod_role(self, interaction: discord.Interaction, role: discord.Role):
        await db.update_guild_config(interaction.guild.id, mod_role_id=role.id)
        await interaction.response.send_message(embed=base_embed("✅ Mod Role Set", f"Moderators: {role.mention}", COLOR_SUCCESS))

    # ==================== RANK MANAGEMENT ====================

    @app_commands.command(name="addrank", description="Add a rank to the hierarchy")
    @app_commands.describe(name="Rank name", order="Rank order (0=lowest)")
    @app_commands.checks.has_permissions(administrator=True)
    async def addrank(self, interaction: discord.Interaction, name: str, order: int):
        # Create a role for this rank
        try:
            role = await interaction.guild.create_role(name=name, reason=f"Rank: {name}")
            await db.add_rank(interaction.guild.id, name, role.id, order)
            await interaction.response.send_message(embed=base_embed("✅ Rank Added", f"**{name}** added at position {order}", COLOR_SUCCESS))
        except discord.Forbidden:
            await interaction.response.send_message(embed=base_embed("Permission Denied", "Cannot create roles.", COLOR_ERROR), ephemeral=True)

    @app_commands.command(name="removerank", description="Remove a rank")
    @app_commands.describe(name="Rank name")
    @app_commands.checks.has_permissions(administrator=True)
    async def removerank(self, interaction: discord.Interaction, name: str):
        success = await db.remove_rank(interaction.guild.id, name)
        if success:
            await interaction.response.send_message(embed=base_embed("✅ Rank Removed", f"**{name}** removed", COLOR_SUCCESS))
        else:
            await interaction.response.send_message(embed=base_embed("Not Found", "Rank doesn't exist.", COLOR_ERROR), ephemeral=True)

    @app_commands.command(name="listranks", description="List all ranks")
    async def listranks(self, interaction: discord.Interaction):
        ranks = await db.get_ranks(interaction.guild.id)
        if not ranks:
            return await interaction.response.send_message(embed=base_embed("No Ranks", "No ranks configured."))
        
        rank_list = "\n".join([f"{r['rank_order']}. **{r['rank_name']}**" for r in ranks])
        await interaction.response.send_message(embed=base_embed("📊 Rank Hierarchy", rank_list))

    # ==================== DIVISION MANAGEMENT ====================

    @app_commands.command(name="adddivision", description="Add a division")
    @app_commands.describe(name="Division name")
    @app_commands.checks.has_permissions(administrator=True)
    async def adddivision(self, interaction: discord.Interaction, name: str):
        try:
            role = await interaction.guild.create_role(name=name, reason=f"Division: {name}")
            await db.add_division(interaction.guild.id, name, role.id)
            await interaction.response.send_message(embed=base_embed("✅ Division Added", f"**{name}** created", COLOR_SUCCESS))
        except discord.Forbidden:
            await interaction.response.send_message(embed=base_embed("Permission Denied", "Cannot create roles.", COLOR_ERROR), ephemeral=True)

    @app_commands.command(name="listdivisions", description="List all divisions")
    async def listdivisions(self, interaction: discord.Interaction):
        divisions = await db.get_divisions(interaction.guild.id)
        if not divisions:
            return await interaction.response.send_message(embed=base_embed("No Divisions", "No divisions configured."))
        
        div_list = "\n".join([f"• {d['division_name']}" for d in divisions])
        await interaction.response.send_message(embed=base_embed("🏢 Divisions", div_list))


async def setup(bot: commands.Bot):
    await bot.add_cog(Multex(bot))
