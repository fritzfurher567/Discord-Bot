# Complete Discord Bot Guide — Every Feature Explained

**Made by Fritz**

This guide covers every single command, setting, and feature in the bot. Copy-paste examples are included for each one.

---

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Moderation](#moderation)
3. [Auto-Moderation](#auto-moderation)
4. [Server Logging](#server-logging)
5. [Tickets](#tickets)
6. [Welcome & Goodbye](#welcome--goodbye)
7. [Leveling & XP](#leveling--xp)
8. [Reaction Roles](#reaction-roles)
9. [Custom Commands](#custom-commands)
10. [Reminders](#reminders)
11. [Economy & Shop](#economy--shop)
12. [Social Alerts](#social-alerts)
13. [Embeds & Messages](#embeds--messages)
14. [Utility & Info](#utility--info)

---

## Initial Setup

### 1. Install & Run

```bash
# Install Python 3.8+, then:
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env

# Add your bot token to .env
# DISCORD_TOKEN=your_token_here

# Run the bot
python main.py
```

### 2. Enable Intents in Discord Developer Portal

1. Go to https://discord.com/developers/applications
2. Click your bot application
3. Go to **Bot** → scroll down to **Privileged Gateway Intents**
4. Turn ON:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
5. Click Save

### 3. Get Invite Link

1. Go to **OAuth2** → **URL Generator**
2. Under **Scopes**, check: `bot` + `applications.commands`
3. Under **Permissions**, check: `Administrator` (or pick specific ones)
4. Copy the generated URL and paste in your browser to invite the bot

For More Help Go To The Setup README For More In Depth Explaining For Setup.

### 4. First Run

When the bot starts, slash commands sync automatically. Depending on your intents, it may take up to an hour to appear globally the first time (usually 5-10 minutes). If they don't appear in your server, try:

```
/help
```

If that works, all commands are synced.

---

## Moderation

All moderation commands log to the configured mod-log channel (if set). Only users with the corresponding Discord permission can use these commands.

### Set Up Mod Log Channel

**Command:** `/setmodlog #channel`

This is where all moderation actions get recorded. Do this first.

```
/setmodlog #mod-logs
```

### Kick a Member

**Command:** `/kick @user [reason]`

Removes a member from the server.

```
/kick @BadUser Spamming in chat
```

**What happens:**
- User is kicked
- Reason is logged to mod-log
- User gets a DM (if they accept DMs from the bot)

### Ban a Member

**Command:** `/ban @user [reason] [delete_days]`

Bans a member and optionally deletes their recent messages.

```
/ban @Hacker Hacking attempt delete_days:7
```

- `delete_days`: 0–7 (how many days of messages to delete, default 0)

### Unban a User

**Command:** `/unban <user_id> [reason]`

Unban someone by their user ID (not name). To get a user ID:
- In Discord, right-click their profile → Copy User ID

```
/unban 123456789 False alarm, they're good
```

### Timeout (Mute) a Member

**Command:** `/timeout @user <duration> [reason]`

Silences someone temporarily. They can't send messages, add reactions, or connect to voice.

**Duration format:** `10m`, `2h`, `1d`, `1w` (max 28 days)

```
/timeout @Spammer 10m Stop advertising
/timeout @BadUser 1d Harassing members
```

### Remove Timeout

**Command:** `/untimeout @user`

Let someone talk again.

```
/untimeout @Spammer
```

### Warn a Member

**Command:** `/warn @user <reason>`

Records a warning against someone. Warnings are persistent and can be reviewed later.

```
/warn @User1 First warning - be respectful
```

### View Warnings

**Command:** `/warnings @user`

See all warnings for a specific member.

```
/warnings @User1
```

**Output shows:**
- Warning ID (used to remove individual warnings)
- Reason
- When it was issued
- Who issued it

### Clear All Warnings

**Command:** `/clearwarnings @user`

Remove all warnings for a member.

```
/clearwarnings @User1
```

### Remove a Single Warning

**Command:** `/removewarning <warning_id>`

Remove one specific warning. Get the ID from `/warnings`.

```
/removewarning 5
```

### Purge (Bulk Delete) Messages

**Command:** `/purge <amount> [@member]`

Delete up to 100 recent messages. Optionally filter by a specific member.

```
/purge 50                    # Delete 50 most recent messages
/purge 25 @Spammer           # Delete 25 recent messages from @Spammer
```

### Lock a Channel

**Command:** `/lock`

Prevents @everyone from sending messages in the current channel.

```
/lock
```

**Use cases:**
- Cool down a heated debate
- Prevent spoilers during a server event
- Temporarily pause discussion

### Unlock a Channel

**Command:** `/unlock`

Re-enable @everyone to send messages.

```
/unlock
```

### Lockdown (Lock All Channels)

**Command:** `/lockdown`

Lock every text channel in the server at once (emergency nuke).

```
/lockdown
```

### Set Slowmode

**Command:** `/slowmode <seconds>`

Force a delay between messages (0 to disable).

```
/slowmode 5              # 5 seconds between each message
/slowmode 0              # Disable slowmode
```

### Change Nickname

**Command:** `/nickname @user [new_nickname]`

Change someone's server nickname (leave blank to reset to username).

```
/nickname @User1 Cool Guy
/nickname @User1          # Reset to their username
```

### Add a Role

**Command:** `/addrole @user @role`

Give someone a role.

```
/addrole @User1 @VIP
/addrole @User2 @Moderator
```

### Remove a Role

**Command:** `/removerole @user @role`

Take away a role.

```
/removerole @User1 @VIP
```

---

## Auto-Moderation

Auto-mod runs automatically on every message. It filters, warns, and logs violations. **Moderators (anyone with Manage Messages) are always exempt.**

### Set Banned Words

**Command:** `/automod-bannedwords add <words>` | `remove <words>` | `list`

Define words that get auto-deleted.

```
/automod-bannedwords add spam, abuse, badword
/automod-bannedwords list
/automod-bannedwords remove badword
```

When someone posts a banned word:
1. Message is deleted
2. User is warned
3. Violation logged to mod-log

### Toggle Invite Filter

**Command:** `/automod-toggle feature:Invite\ link\ filter enabled:true`

Auto-delete Discord invite links (blocks self-promotion).

```
/automod-toggle feature:Invite\ link\ filter enabled:true    # Turn ON
/automod-toggle feature:Invite\ link\ filter enabled:false   # Turn OFF
```

### Toggle Caps Filter

**Command:** `/automod-toggle feature:Excessive\ caps\ filter enabled:true`

Auto-delete messages that are >70% UPPERCASE.

```
/automod-toggle feature:Excessive\ caps\ filter enabled:true
```

### Set Mention Limit

**Command:** `/automod-mentionlimit <limit>`

Delete messages with more than X mentions (prevents mass-tagging).

```
/automod-mentionlimit 5        # Max 5 mentions per message
/automod-mentionlimit 0        # Disable (allow unlimited)
```

---

## Server Logging

Separate from moderation logs — this logs general activity: message edits, deletes, and channel management.

### Set Server Log Channel

**Command:** `/setserverlog #channel`

```
/setserverlog #logs
```

**What gets logged:**
- ✅ Message deleted (full text + author + channel)
- ✅ Message edited (before & after text)
- ✅ Channel created
- ✅ Channel deleted

---

## Tickets

A full support ticket system with categories, priorities, and transcripts.

### Initial Setup

**Command:** `/ticket-setup <category> <log_channel>`

Choose a category for new ticket channels, and a channel to log closed tickets.

```
/ticket-setup #Tickets #ticket-logs
```

Do this once per server.

### Post the Ticket Panel

**Command:** `/ticket-panel`

Post the "Create Ticket" button in the current channel (usually in #support or #tickets).

```
/ticket-panel
```

**What users see:**
- A message with a blue "Create Ticket" button
- Clicking it opens a dropdown to select category & priority

### How Tickets Work (User Perspective)

1. Click the "Create Ticket" button
2. Select a category (General Support, Technical, Billing, Report a User, Other)
3. Select a priority (Low, Medium, High, Urgent)
4. A private channel is created: `ticket-username`
5. Only the user and mods can see it

### Inside a Ticket Channel

Users type their issue. Staff can:

**Command:** `/ticket-add @user`

Add someone to this ticket (can be another staff member or the user's friend).

```
/ticket-add @Helper
```

**Command:** `/ticket-remove @user`

Remove someone from this ticket.

```
/ticket-remove @Helper
```

**Command:** `/ticket-priority high`

Change the ticket's priority.

```
/ticket-priority urgent
```

**Command:** `/ticket-close`

Close the ticket. The bot:
1. Saves a `.txt` transcript to the log channel
2. Deletes the channel after 5 seconds

```
/ticket-close
```

### Claim a Ticket

Inside a ticket channel, click the "Claim" button (appears on the first message). This marks you as the handler so multiple staff don't respond at once.

---

## Welcome & Goodbye

Announce new and leaving members.

### Set Welcome Channel

**Command:** `/welcome-setup #channel [message]`

Post a welcome embed when someone joins.

```
/welcome-setup #welcome Welcome {user} to {server}! We now have {membercount} members.
```

**Placeholders:**
- `{user}` → @mention of the new member
- `{username}` → their name
- `{server}` → server name
- `{membercount}` → current member count

### Set Goodbye Channel

**Command:** `/goodbye-setup #channel [message]`

Post when someone leaves.

```
/goodbye-setup #goodbye {user} has left {server}. We now have {membercount} members.
```

### Welcome DM

**Command:** `/welcome-dm enabled:true [message]`

Send a DM to new members (in addition to channel message).

```
/welcome-dm enabled:true Welcome to {server}! Read #rules and have fun!
```

### Goodbye DM

**Command:** `/goodbye-dm enabled:true [message]`

Send a DM to leaving members.

```
/goodbye-dm enabled:true Sorry to see you leave {server}!
```

---

## Leveling & XP

MEE6-style XP system. Members earn random XP for chatting (not commands).

### XP Rules

- **Earn XP:** Send a message in any channel
- **Cooldown:** XP only once every 60 seconds per user (prevents spam)
- **Amount:** 15–25 XP per message
- **Levels:** XP needed = `5 * (level^2) + 50 * level + 100`
  - Level 1: 155 XP
  - Level 5: 630 XP
  - Level 10: 1,600 XP

### View Your Rank

**Command:** `/rank [@user]`

See your (or someone else's) level and progress.

```
/rank                  # Your rank
/rank @User1           # Another member's rank
```

**Shows:**
- Level
- Total XP
- Progress bar to next level
- XP in current level / XP needed

### Top Members (Leaderboard)

**Command:** `/leaderboard`

See top 10 members by XP.

```
/leaderboard
```

**Shows:**
- 🥇 🥈 🥉 medals for top 3
- Name + Level + Total XP

### Set Level-Up Announcement Channel

**Command:** `/levelup-channel #channel`

When someone levels up, post an announcement there (or in the message channel by default).

```
/levelup-channel #level-ups
```

### Grant Role at Level

**Command:** `/setlevelrole level:5 role:@Regular`

Auto-give a role when someone reaches a level.

```
/setlevelrole level:5 role:@Member
/setlevelrole level:10 role:@Regular
/setlevelrole level:25 role:@VIP
```

When a member levels up to 5, they automatically get @Member. Stacks with other roles.

### Remove Level Role

**Command:** `/removelevelrole level:5`

Stop granting a role at that level.

```
/removelevelrole level:5
```

---

## Reaction Roles

Carl-bot style: React with an emoji to get a role.

### Add a Reaction Role

**Command:** `/reactionrole-add <message_id> <emoji> @role`

Link an emoji on an existing message to a role.

**To get message ID:**
1. In Discord, right-click a message
2. Click "Copy Message ID"

**Example:**

```
/reactionrole-add 987654321 🎮 @Gamer
/reactionrole-add 987654321 🎨 @Artist
```

Now when someone reacts to that message with 🎮, they get @Gamer. When they remove the reaction, the role is removed.

### Remove a Reaction Role

**Command:** `/reactionrole-remove <message_id> <emoji>`

Unlink an emoji.

```
/reactionrole-remove 987654321 🎮
```

---

## Custom Commands

Define your own text commands without any coding.

### Add a Custom Command

**Command:** `/customcommand-add trigger <response>`

Create a text command. When someone types `!trigger`, the bot replies with `<response>`.

```
/customcommand-add rules Check #rules for our server guidelines!
/customcommand-add hello Hey! Welcome to our server!
```

Now, if someone types:
```
!rules
```

The bot replies:
```
Check #rules for our server guidelines!
```

### Remove a Custom Command

**Command:** `/customcommand-remove trigger`

Delete a custom command.

```
/customcommand-remove rules
```

### List Custom Commands

**Command:** `/customcommand-list`

See all custom commands in your server.

```
/customcommand-list
```

---

## Reminders

Set a reminder to be notified later.

### Remind Me

**Command:** `/remind <duration> <message>`

Set a reminder. Duration format: `10m`, `2h`, `1d`, `1w`

```
/remind 10m Check the oven
/remind 2h Call the dentist
/remind 1d Pay bills
```

**What happens:**
1. You get a DM when the reminder is due
2. If DMs are closed, the bot posts in the channel where you set it
3. The reminder is checked every 30 seconds

---

## Economy & Shop

A server-wide currency system.

### Check Balance

**Command:** `/balance [@user]`

See how much currency you (or someone) have.

```
/balance
/balance @User1
```

### Daily Reward

**Command:** `/daily`

Claim 200 coins once per day.

```
/daily
```

**Cooldown:** 24 hours

### Work

**Command:** `/work`

Earn 50–150 coins with a random job message.

```
/work
```

**Messages vary:**
- "You delivered packages and earned X coins."
- "You busked in the town square and collected X coins."

**Cooldown:** 1 hour

### Send Money

**Command:** `/pay @user <amount>`

Pay another member coins.

```
/pay @User1 100
```

### Economy Leaderboard

**Command:** `/economy-leaderboard`

Top 10 richest members.

```
/economy-leaderboard
```

### View Shop

**Command:** `/shop`

List all purchasable items (roles, rewards, etc.).

```
/shop
```

### Buy an Item

**Command:** `/buy <item_name>`

Purchase an item from the shop.

```
/buy Member
/buy VIP
```

If the item is a role, you get it automatically.

### Admin: Add Shop Item

**Command:** `/shop-add item_name <price> [@role]`

Add an item to the shop. Optionally link a role.

```
/shop-add Member 500           # 500 coins, no role reward
/shop-add VIP 1000 @VIP        # 1000 coins, gives @VIP role
```

### Admin: Remove Shop Item

**Command:** `/shop-remove item_name`

Remove an item from the shop.

```
/shop-remove Member
```

---

## Social Alerts

Notifications when content creators upload or go live.

### YouTube Alerts

**Command:** `/youtube-alert #channel <channel_id>`

Get notified when a YouTube channel uploads.

**To get YouTube channel ID:**
1. Go to the channel's page
2. In the URL, it's after `/channel/` — starts with `UC`
3. Copy that ID

```
/youtube-alert #streams UCddiUEpYJcSLOAekIKcyNAA
```

**What happens:**
- Bot polls YouTube's public RSS feed every 5 minutes
- When a new video is found, posts an embed in #streams
- No API key needed

### Remove YouTube Alert

**Command:** `/youtube-alert-remove <channel_id>`

Stop alerts for a channel.

```
/youtube-alert-remove UCddiUEpYJcSLOAekIKcyNAA
```

### Twitch Alerts

**Command:** `/twitch-alert #channel <username>`

Get notified when a streamer goes live.

```
/twitch-alert #streams ninja
/twitch-alert #streams pokimane
```

**Setup required:**
- Add `TWITCH_CLIENT_ID` and `TWITCH_CLIENT_SECRET` to `.env`
- Free: Create an app at https://dev.twitch.tv/console
- Bot checks every 3 minutes

### Remove Twitch Alert

**Command:** `/twitch-alert-remove <username>`

Stop alerts for a streamer.

```
/twitch-alert-remove ninja
```

---

## Embeds & Messages

Send custom messages and embeds.

### Build a Custom Embed

**Command:** `/embed [#channel]`

Opens a form where you fill in:
- **Title** (visible)
- **Description** (main text)
- **Color** (hex code like `5865F2`, or blank for default)
- **Footer** (small text at bottom, or uses "Made by Fritz" by default)
- **Image URL** (optional banner image)

```
/embed #announcements
```

Then fill in the form:
- Title: `🎉 New Feature!`
- Description: `We just added /remind commands!`
- Color: `57F287` (green)
- Footer: `Announced today`
- Image: https://example.com/image.png

### Send Plain Text

**Command:** `/say <message> [#channel]`

Make the bot say something.

```
/say Hello everyone!
/say #announcements Big update coming soon!
```

---

## Utility & Info

General commands.

### Ping

**Command:** `/ping`

Check the bot's latency.

```
/ping
```

**Output:** Latency in milliseconds

### Server Info

**Command:** `/serverinfo`

See stats about your server.

```
/serverinfo
```

**Shows:**
- Owner
- Member count
- Text/voice channels
- Roles
- Creation date

### User Info

**Command:** `/userinfo [@user]`

See info about a member.

```
/userinfo
/userinfo @User1
```

**Shows:**
- Join date
- Account creation date
- All roles

### Avatar

**Command:** `/avatar [@user]`

Get a member's profile picture.

```
/avatar
/avatar @User1
```

### Credits

**Command:** `/credits`

See who made this bot.

```
/credits
```

### Help

**Command:** `/help`

Full list of all commands.

```
/help
```

---

## Database & Data Persistence

All data (XP, economy, warnings, tickets, etc.) is stored in `bot_data.db` — a local SQLite database.

- **Saved automatically** after every command
- **Survives restarts** — data persists when bot goes offline
- **Per-server** — each server has separate XP, economy, config

**Backup:** Just copy `bot_data.db` somewhere safe.

---

## Troubleshooting

### Commands don't appear

1. Make sure intents are enabled in the Developer Portal (Server Members + Message Content)
2. Restart the bot: `python main.py`
3. Wait up to an hour for global sync (usually 5–10 min)

### Bot can't see messages

- Enable **Message Content Intent** in Developer Portal
- Restart the bot

### XP not working

- Members must send real messages (not commands)
- XP has a 60-second cooldown per user

### Tickets not creating channels

- Make sure you ran `/ticket-setup category:<category> log_channel:<channel>`
- The category must exist in Discord
- Bot must have permission to create channels

### YouTube/Twitch alerts not firing

- YouTube: Double-check the channel ID (must start with `UC`)
- Twitch: Make sure `TWITCH_CLIENT_ID` and `TWITCH_CLIENT_SECRET` are in `.env`

---

## Tips & Best Practices

1. **Set up mod-log first** — then all moderation actions are recorded
2. **Use reaction roles for opt-ins** — let members pick roles themselves
3. **Custom commands save time** — for rules, FAQs, links you repeat
4. **Level roles encourage chat** — make levels exciting with role rewards
5. **Economy is more fun with a shop** — let members spend their coins on roles or items
6. **Welcome messages make servers friendly** — new members feel wanted

---

## Credit & License

**Made by Fritz**

MIT License — you can modify and redistribute, but keep the attribution.

```
Copyright (c) 2026 Fritz
```

---

**Questions or issues?** Check the codebase or ask in our Discord server!

https://discord.gg/MxETdBJAHd
