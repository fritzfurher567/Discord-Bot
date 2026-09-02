"""
cogs/Games.py
Fun games and entertainment commands: trivia, rock-paper-scissors, 
coin flip, slots, guess the number, and more.
"""

import datetime
import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

import database as db
from config import COLOR_SUCCESS, COLOR_ERROR, COLOR_INFO, BOT_CREDIT


def base_embed(title: str, description: str = None, color: int = COLOR_INFO) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=BOT_CREDIT)
    return embed


TRIVIA_QUESTIONS = [
    {"q": "What is the capital of France?", "a": "paris"},
    {"q": "What is 2 + 2?", "a": "4"},
    {"q": "What is the largest planet in our solar system?", "a": "jupiter"},
    {"q": "What year did World War II end?", "a": "1945"},
    {"q": "What is the chemical symbol for gold?", "a": "au"},
    {"q": "Who painted the Mona Lisa?", "a": "leonardo"},
    {"q": "What is the smallest country in the world?", "a": "vatican"},
    {"q": "How many sides does a hexagon have?", "a": "6"},
    {"q": "What is the speed of light?", "a": "300000"},
    {"q": "What is the largest ocean on Earth?", "a": "pacific"},
]


class Games(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ongoing_trivia = {}  # user_id -> (correct_count, current_question)

    @app_commands.command(name="trivia", description="Play a trivia game!")
    async def trivia(self, interaction: discord.Interaction):
        if interaction.user.id in self.ongoing_trivia:
            return await interaction.response.send_message(embed=base_embed("Already Playing", "You're already in a trivia game!"), ephemeral=True)
        
        self.ongoing_trivia[interaction.user.id] = {"score": 0, "current": 0}
        
        async def trivia_game():
            for i in range(5):
                q_data = random.choice(TRIVIA_QUESTIONS)
                await interaction.channel.send(
                    embed=base_embed(f"📚 Trivia Question {i+1}/5", q_data["q"])
                )
                
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author == interaction.user,
                        timeout=15
                    )
                    if msg.content.lower() in q_data["a"].lower():
                        self.ongoing_trivia[interaction.user.id]["score"] += 1
                        await interaction.channel.send(embed=base_embed("✅ Correct!", color=COLOR_SUCCESS))
                    else:
                        await interaction.channel.send(embed=base_embed("❌ Wrong!", f"Answer: {q_data['a']}", COLOR_ERROR))
                except:
                    await interaction.channel.send(embed=base_embed("⏱️ Time's Up!", "No answer provided.", COLOR_ERROR))
            
            score = self.ongoing_trivia.pop(interaction.user.id)["score"]
            await interaction.channel.send(embed=base_embed("🏁 Game Over!", f"Your Score: **{score}/5**"))
        
        await interaction.response.send_message(embed=base_embed("🎮 Starting Trivia", "Get ready! 5 questions incoming..."))
        await trivia_game()

    @app_commands.command(name="rps", description="Play Rock, Paper, Scissors against the bot")
    @app_commands.describe(choice="rock, paper, or scissors")
    async def rock_paper_scissors(self, interaction: discord.Interaction, choice: str):
        choices = ["rock", "paper", "scissors"]
        if choice.lower() not in choices:
            return await interaction.response.send_message(embed=base_embed("Invalid Choice", "Choose: rock, paper, or scissors"), ephemeral=True)
        
        bot_choice = random.choice(choices)
        user_choice = choice.lower()
        
        if user_choice == bot_choice:
            result = "🤝 It's a tie!"
        elif (user_choice == "rock" and bot_choice == "scissors") or \
             (user_choice == "paper" and bot_choice == "rock") or \
             (user_choice == "scissors" and bot_choice == "paper"):
            result = "🎉 You win!"
        else:
            result = "😔 Bot wins!"
        
        embed = base_embed("🎮 Rock, Paper, Scissors", f"**Your choice:** {user_choice}\n**Bot's choice:** {bot_choice}\n\n{result}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])
        await interaction.response.send_message(embed=base_embed("🪙 Coin Flip", f"**Result: {result}**"))

    @app_commands.command(name="slots", description="Play the slot machine (earn/lose currency)")
    async def slots(self, interaction: discord.Interaction):
        symbols = ["🍎", "🍊", "🍋", "🍌", "🍉", "🍇", "🎁", "⭐"]
        slot1 = random.choice(symbols)
        slot2 = random.choice(symbols)
        slot3 = random.choice(symbols)
        
        result_text = f"{slot1} | {slot2} | {slot3}\n"
        
        if slot1 == slot2 == slot3:
            result_text += "🎉 **JACKPOT! You won 500 coins!**"
            await db.update_balance(interaction.guild.id, interaction.user.id, 
                                  (await db.get_balance_data(interaction.guild.id, interaction.user.id))["balance"] + 500)
        elif slot1 == slot2 or slot2 == slot3:
            result_text += "✨ **Two match! You won 100 coins!**"
            await db.update_balance(interaction.guild.id, interaction.user.id,
                                  (await db.get_balance_data(interaction.guild.id, interaction.user.id))["balance"] + 100)
        else:
            result_text += "😔 **No match! You lost 50 coins.**"
            balance_data = await db.get_balance_data(interaction.guild.id, interaction.user.id)
            new_balance = max(0, balance_data["balance"] - 50)
            await db.update_balance(interaction.guild.id, interaction.user.id, new_balance)
        
        await interaction.response.send_message(embed=base_embed("🎰 Slots", result_text))

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question")
    @app_commands.describe(question="Your question")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        responses = [
            "Yes, definitely!", "No, never.", "Maybe...", "Concentrate and ask again.",
            "Don't count on it.", "It is certain.", "Ask again later.", "Outlook good.",
            "Very doubtful.", "Signs point to yes.", "My sources say no.", "Absolutely!"
        ]
        await interaction.response.send_message(embed=base_embed("🎱 Magic 8-Ball", f"**Q:** {question}\n**A:** {random.choice(responses)}"))

    @app_commands.command(name="guess", description="Guess a number between 1-100")
    async def guess(self, interaction: discord.Interaction):
        secret = random.randint(1, 100)
        attempts = 0
        
        await interaction.response.send_message(embed=base_embed("🎯 Guess the Number", "I'm thinking of a number between 1-100. You have 10 tries."))
        
        async def check_guess():
            nonlocal attempts
            for _ in range(10):
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author == interaction.user,
                        timeout=30
                    )
                    attempts += 1
                    try:
                        guess = int(msg.content)
                    except:
                        await interaction.channel.send("Please enter a valid number.")
                        continue
                    
                    if guess == secret:
                        await interaction.channel.send(embed=base_embed("🎉 Correct!", f"You guessed it in {attempts} tries!", COLOR_SUCCESS))
                        return
                    elif guess < secret:
                        await interaction.channel.send(f"📈 Higher! (Attempts: {attempts}/10)")
                    else:
                        await interaction.channel.send(f"📉 Lower! (Attempts: {attempts}/10)")
                except:
                    await interaction.channel.send("Time's up!")
                    break
            
            await interaction.channel.send(embed=base_embed("😔 Game Over!", f"The number was {secret}.", COLOR_ERROR))
        
        await check_guess()


async def setup(bot: commands.Bot):
    await bot.add_cog(Games(bot))
