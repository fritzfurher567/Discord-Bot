# Complete Discord Bot Guide

Made by Fritz

This guide walks you through every single command in the bot. All examples are copy-paste ready.

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
13. [Permissions](#permissions)
14. [Roblox Verification](#roblox-verification)
15. [Awards & Leave of Absence](#awards--leave-of-absence)
16. [Rank Hierarchy & Divisions](#rank-hierarchy--divisions)
17. [Discharge & Desertions](#discharge--desertions)
18. [Background Checks](#background-checks)
19. [Events](#events)
20. [Audit Log](#audit-log)
21. [Embeds & Messages](#embeds--messages)
22. [Utility & Info](#utility--info)

---

## Initial Setup

### 1. Setup in Discord Developer Portal

Go to https://discord.com/developers/applications and create a new application. Under the Bot section, make sure these intents are enabled:
- Server Members Intent
- Message Content Intent
- Presence Intent

Copy your bot token and save it somewhere safe.

### 2. Install & Run

```bash
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env` and add your bot token:
```
DISCORD_TOKEN=your_token_here
```

Run the bot:
```bash
python main.py
```

### 3. Get Your Invite Link

Go to OAuth2 > URL Generator. Check `bot` and `applications.commands` under Scopes. Check `Administrator` under Permissions. Copy the URL and open it in your browser to invite the bot.

### 4. First Run

Commands sync automatically when the bot starts. Usually they appear in 5-10 minutes but can take up to an hour the first time. Try `/help` to verify everything worked.

### Hosting 24/7

You'll need a hosting service to keep the bot running. Options include PythonAnywhere (pythonanywhere.com) for a paid option or Replit (replit.com) for free hosting.

---

## Moderation

All moderation actions get logged to your mod-log channel if you've set one. Only users with the required Discord permission can use these commands.

### Set Up Mod Log Channel

```
/setmodlog #mod-logs
```

Do this first. Everything gets recorded here.

### Kick a Member

```
/kick @BadUser Spamming in chat
```

Removes them from the server. They get a DM if their DMs are open.

### Ban a Member

```
/ban @Hacker Attempting to hack
/ban @Hacker Attempting to hack delete_days:7
```

The `delete_days` option (0-7) removes their recent messages. Defaults to 0.

### Unban a User

```
/unban 123456789 They're good now
```

You need their user ID. Right-click their profile and choose "Copy User ID".

### Timeout (Mute) a Member

```
/timeout @Spammer 10m Stop advertising
/timeout @User1 1d Be respectful
```

Duration format: `10m`, `2h`, `1d`, `1w`. Max is 28 days. They can't send messages or connect to voice.

### Remove Timeout

```
/untimeout @Spammer
```

### Warn a Member

```
/warn @User1 First warning, read the rules
```

Records a warning that stacks up.

### View Warnings

```
/warnings @User1
```

Shows all warnings with IDs, reasons, dates, and who issued them.

### Clear All Warnings

```
/clearwarnings @User1
```

### Remove a Single Warning

```
/removewarning 5
```

Get the ID from `/warnings`.

### Delete Messages (Purge)

```
/purge 50
/purge 25 @Spammer
```

Delete up to 100 recent messages. You can filter by a member.

### Lock a Channel

```
/lock
```

Prevents @everyone from sending messages. Use this to cool down a heated debate or pause discussion during an event.

### Unlock a Channel

```
/unlock
```

### Lock All Channels

```
/lockdown
```

Emergency button that locks every text channel at once.

### Set Slowmode

```
/slowmode 5
/slowmode 0
```

Force a delay between messages (seconds). 0 disables it.

### Change Someone's Nickname

```
/nickname @User1 Cool Guy
/nickname @User1
```

Leave it blank to reset.

### Add a Role

```
/addrole @User1 @VIP
```

### Remove a Role

```
/removerole @User1 @VIP
```

---

## Auto-Moderation

Auto-mod runs on every message automatically. Moderators are always exempt.

### Set Banned Words

```
/automod-bannedwords add spam, abuse, badword
/automod-bannedwords list
/automod-bannedwords remove badword
```

Banned words get deleted, the user gets warned, and it's logged.

### Toggle Invite Filter

```
/automod-toggle feature:Invite_link_filter enabled:true
/automod-toggle feature:Invite_link_filter enabled:false
```

Auto-delete Discord invite links.

### Toggle Caps Filter

```
/automod-toggle feature:Excessive_caps_filter enabled:true
```

Delete messages that are more than 70% uppercase.

### Set Mention Limit

```
/automod-mentionlimit 5
/automod-mentionlimit 0
```

Delete messages with more than X mentions. 0 disables it.

---

## Server Logging

Separate from moderation logs. This logs general activity.

### Set Server Log Channel

```
/setserverlog #logs
```

Logs message edits, deletes, and channel creates/deletes.

---

## Tickets

Support ticket system where members create private channels.

### Initial Setup

```
/ticket-setup #Tickets #ticket-logs
```

Choose a category for ticket channels and a log channel. Do this once.

### Post the Ticket Panel

```
/ticket-panel
```

Posts a button in the current channel. Members click to create a ticket, pick a category (General Support, Technical, Billing, Report a User, Other), and choose priority (Low, Medium, High, Urgent). A private channel gets created.

### Inside a Ticket Channel

```
/ticket-add @Helper
/ticket-remove @Helper
/ticket-priority urgent
/ticket-close
```

Add or remove people, change priority, or close the ticket (saves a transcript and deletes the channel).

Click the Claim button on the first message to mark yourself as handling it.

---

## Welcome & Goodbye

### Set Welcome Message

```
/welcome-setup #welcome Welcome {user} to {server}! We now have {membercount} members.
```

Placeholders: `{user}`, `{username}`, `{server}`, `{membercount}`

### Set Goodbye Message

```
/goodbye-setup #goodbye {user} has left {server}. We now have {membercount} members.
```

### Send Welcome DM

```
/welcome-dm enabled:true Welcome to {server}! Check out #rules.
```

New members get a DM in addition to the channel message.

### Send Goodbye DM

```
/goodbye-dm enabled:true Sorry to see you leave {server}!
```

---

## Leveling & XP

Members earn XP for chatting (not commands). 15-25 XP per message with a 60-second cooldown per person to prevent spam.

### Check Your Rank

```
/rank
/rank @User1
```

Shows level, total XP, and progress to next level.

### See the Leaderboard

```
/leaderboard
```

Top 10 members by XP.

### Set Rank-Up Announcement Channel

```
/levelup-channel #level-ups
```

Announcements post there when someone levels up.

### Auto-Grant Role at a Level

```
/setlevelrole level:5 role:@Member
/setlevelrole level:10 role:@Regular
/setlevelrole level:25 role:@VIP
```

When they hit level 5, they automatically get the Member role.

### Remove a Level Role

```
/removelevelrole level:5
```

---

## Reaction Roles

React with an emoji to get a role.

### Link Emoji to Role

```
/reactionrole-add 987654321 emoji:gear role:@Support
/reactionrole-add 987654321 emoji:art role:@Artist
```

Get the message ID by right-clicking a message and choosing "Copy Message ID". When someone reacts, they get the role. When they remove the reaction, they lose the role.

### Unlink an Emoji

```
/reactionrole-remove 987654321 emoji:gear
```

---

## Custom Commands

Define your own text commands without coding.

### Add a Custom Command

```
/customcommand-add trigger:rules Check #rules for our guidelines!
/customcommand-add trigger:hello Welcome to the server!
```

Now if someone types `!rules`, the bot replies with your message.

### Remove a Custom Command

```
/customcommand-remove trigger:rules
```

### List Custom Commands

```
/customcommand-list
```

---

## Reminders

### Set a Reminder

```
/remind duration:10m Check the oven
/remind duration:2h Call the dentist
/remind duration:1d Pay bills
```

Duration format: `10m`, `2h`, `1d`, `1w`. You get a DM when it's due (or the bot posts in the channel if your DMs are closed).

---

## Economy & Shop

### Check Balance

```
/balance
/balance @User1
```

### Claim Daily Reward

```
/daily
```

Get 200 coins once per 24 hours.

### Work

```
/work
```

Earn 50-150 coins. 1 hour cooldown.

### Send Money

```
/pay @User1 100
```

### Economy Leaderboard

```
/economy-leaderboard
```

Top 10 richest members.

### View the Shop

```
/shop
```

### Buy an Item

```
/buy item_name:Member
/buy item_name:VIP
```

### Add Item to Shop

```
/shop-add item_name:Member price:500
/shop-add item_name:VIP price:1000 role:@VIP
```

### Remove Item from Shop

```
/shop-remove item_name:Member
```

---

## Social Alerts

### YouTube Alerts

```
/youtube-alert #streams UCddiUEpYJcSLOAekIKcyNAA
```

YouTube IDs start with UC and are 24 characters long. Bot checks every 5 minutes. No API key needed.

### Remove YouTube Alert

```
/youtube-alert-remove UCddiUEpYJcSLOAekIKcyNAA
```

### Twitch Alerts

```
/twitch-alert #streams ninja
```

Requires TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET in your .env (free at dev.twitch.tv/console). Checks every 3 minutes.

### Remove Twitch Alert

```
/twitch-alert-remove ninja
```

---

## Permissions

Restrict commands to specific roles. The server owner and anyone with Administrator always bypass restrictions.

### Restrict a Command

```
/permission-restrict command:ban role:@Moderator
/permission-restrict command:ticket-close role:@Support
```

Now only those roles (plus owner/admins) can use that command.

### Remove a Role from a Command

```
/permission-unrestrict command:ban role:@Moderator
```

### Remove All Restrictions from a Command

```
/permission-clear command:ban
```

### See What's Restricted

```
/permission-list
/permission-list command:ban
```

### Add or Remove Roles (Dedicated Command)

```
/role add @User1 @VIP
/role remove @User1 @VIP
```

---

## Roblox Verification

Link Discord members to their Roblox accounts.

### Verify Your Account

```
/verify roblox_username:your_username
```

Bot looks it up and can auto-grant a Verified role.

### Unverify Yourself

```
/unverify
```

Admins can also unverify others:
```
/unverify member:@User1
```

### Look Up Someone's Account

```
/whois
/whois member:@User1
```

Shows their linked Roblox username, ID, and when they verified.

### Set the Verified Role

```
/verified-role role:@Verified
```

Auto-grant this role when someone verifies.

---

## Awards & Leave of Absence

### Give Someone an Award

```
/award member:@User1 title:Outstanding_Contribution reason:Helped many new members this week
```

They get a DM, it can post to an announcements channel, and it shows in their history.

### View Someone's Awards

```
/awards
/awards member:@User1
```

### Request Time Off

```
/loa-request start_date:2026-09-01 end_date:2026-09-10 reason:Going on vacation
```

Staff gets a notification with Approve/Deny buttons.

### See Who's On Leave

```
/loa-list
```

Shows all currently approved leaves.

### Set Awards Channel

```
/awards-channel #announcements
```

### Set LOA Review Channel

```
/loa-channel #loa-requests
```

Where staff approve or deny requests.

---

## Rank Hierarchy & Divisions

Build a ranked ladder and organize members into units.

### Add Ranks

```
/rank-add rank_name:Private role:@Private order:1
/rank-add rank_name:Corporal role:@Corporal order:2
/rank-add rank_name:Sergeant role:@Sergeant order:3
```

Order determines the ladder (higher = higher rank). Each rank is tied to a role.

### See All Ranks

```
/rank-list
```

### Promote Someone

```
/promote member:@User1
```

Moves them up one rank.

### Demote Someone

```
/demote member:@User1
```

Moves them down one rank.

### Set Specific Rank

```
/setrank member:@User1 rank_name:Sergeant
```

Jump straight to that rank.

### Remove a Rank

```
/rank-remove rank_name:Private
```

### Add Divisions

```
/division-add division_name:Alpha role:@Alpha_Squad
/division-add division_name:Bravo role:@Bravo_Squad
```

Divisions are flat (no hierarchy). Use them for squads or teams.

### See Divisions

```
/division-list
```

### Transfer Someone

```
/transfer member:@User1 division_name:Bravo
```

Removes them from their current division, adds them to the new one.

---

## Discharge & Desertions

Remove members from rank/division and track departures.

### Discharge a Member

```
/discharge member:@User1 reason:Inactive for 30 days
/discharge member:@User1 reason:Violated server rules kick:true
```

Strips all rank and division roles. The `kick` option also removes them from the server. They get a DM explaining why.

### View Discharge History

```
/discharges member:@User1
```

### Automatic Desertion Detection

If someone with a rank or division role leaves the server on their own, it's automatically logged as a desertion. No command needed.

### See Recent Desertions

```
/desertions
```

Members who left while ranked.

### Set Discharge Log Channel

```
/discharge-channel #discharge-logs
```

---

## Background Checks

### Run a Background Check

```
/backgroundcheck member:@User1
```

Shows their join date, account age, current rank/division, Roblox link, warning count, award count, and discharge history. Useful before promoting someone.

---

## Events

Schedule activities and track RSVPs.

### Create an Event

```
/event-create name:Server_Tournament description:1v1 bracket when:Next Saturday 8PM EST channel:#events
```

Posts an announcement with three RSVP buttons: Attending, Maybe, Can't Make It.

### See Upcoming Events

```
/event-list
```

### Check Attendance

```
/event-attendance event_id:1
```

Shows breakdown of Attending/Maybe/Declined.

---

## Audit Log

Track every command used in your server.

### Set Audit Log Channel

```
/auditlog-channel #audit-logs
```

Every command gets logged there in real-time.

### Check Recent Commands

```
/auditlog
```

Shows the 15 most recent commands and who ran them.

---

## Embeds & Messages

### Build a Custom Embed

```
/embed channel:#announcements
```

Opens a form where you fill in title, description, color (hex like 5865F2), footer, and an optional image URL.

### Send Plain Text

```
/say message:Hello everyone!
/say message:Update coming soon! channel:#announcements
```

---

## Utility & Info

### Check Bot Latency

```
/ping
```

### Server Info

```
/serverinfo
```

Shows owner, member count, channels, roles, creation date.

### Member Info

```
/userinfo
/userinfo member:@User1
```

Shows join date, account creation date, and roles.

### Get Avatar

```
/avatar
/avatar member:@User1
```

### Credits

```
/credits
```

### Help

```
/help
```

Lists all commands by category.

---

## Database

Everything is stored in `bot_data.db`, a local SQLite database. It survives bot restarts and keeps data per-server. To back up, just copy `bot_data.db`.

---

## Troubleshooting

**Commands don't show up**: Enable Server Members and Message Content intents in the Developer Portal. Restart the bot. Wait up to an hour.

**Bot can't see messages**: Enable Message Content Intent and restart.

**XP not working**: Members need to send real messages, not commands. There's a 60-second cooldown per person.

**Tickets won't create**: Run `/ticket-setup` first with a valid category. Bot needs permission to create channels.

**YouTube/Twitch alerts not firing**: Double-check the YouTube ID (must start with UC). For Twitch, verify your credentials in .env.

---

## Tips

Set up `/setmodlog` first so all moderation gets recorded.

Use reaction roles to let members self-assign roles.

Custom commands save time for FAQs you mention constantly.

Level-up roles make leveling feel rewarding - people chat more.

Economy is more fun with a shop - let people spend coins on perks.

Awards recognize people publicly and boost morale.

Background checks before promoting someone prevent mistakes.

Rank promotion is cleaner than manual role management.

Event RSVPs help you plan around actual attendance.

Audit logging catches rule-breakers and shows who changed what.

---

Made by Fritz. MIT License. Attribution required.
