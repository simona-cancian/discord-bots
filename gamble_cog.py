"""
This is the gamble cog that will be called in baki_main.
It belongs to Baki bot in deputy's server.
"""


import discord
from discord.ext import commands, tasks
import sqlite3
import random
import datetime


class Gamble(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.gain_daily.start()     # Start the task

    # Cancel the task whe the cog is unloaded
    def cog_unload(self):
        self.gain_daily.cancel()

    # Log in
    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS main (
        user_id INTEGER, 
        wallet INTEGER,
        bank INTEGER
        )
        ''')

    # Create member if they are not in the database yet
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        author = message.author

        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        cursor.execute('SELECT user_id FROM main WHERE user_id = ?', (author.id,))
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO main (user_id, wallet, bank) VALUES (?, ?, ?)"
            val = (author.id, 100, 0)
            cursor.execute(sql, val)

        db.commit()
        cursor.close()
        db.close()

    # Check balance
    @commands.command(name="b")
    async def balance(self, ctx):
        try:
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            cursor.execute(f"SELECT wallet, bank FROM main WHERE user_id = ?", (ctx.author.id,))
            bal = cursor.fetchone()

            wallet = bal[0] if bal else 0
            bank = bal[1] if bal else 0

            formatted_wallet = "{:,}".format(wallet)
            formatted_bank = "{:,}".format(bank)

            em = discord.Embed(color=discord.Color.random())
            em.set_author(name=f"{ctx.author.name} Bank Account")
            em.add_field(name="Wallet", value=f"💰 {formatted_wallet}")
            em.add_field(name="Bank", value=f"💰 {formatted_bank}")
            em.add_field(name="Assets", value=f"💰 {"{:,}".format(wallet + bank)}")
            em.set_thumbnail(url="https://cdn-icons-png.flaticon.com/128/2382/2382307.png")
            em.timestamp = datetime.datetime.now(datetime.timezone.utc)

            await ctx.send(embed=em)

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            await ctx.send("An error occurred while retrieving the balance.")

        finally:
            cursor.close()
            db.close()

    # Daily free coins
    @tasks.loop(hours=24)
    async def gain_daily(self):
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()

        for guild in self.bot.guilds:
            for member in guild.members:
                if not member.bot:
                    cursor.execute("SELECT wallet FROM main WHERE user_id = ?", (member.id,))
                    wallet = cursor.fetchone()

                    earnings = random.randint(5, 5000)
                    new_balance = wallet[0] + earnings

                    cursor.execute("UPDATE main SET wallet = ? WHERE user_id = ?", (new_balance, member.id))
                    db.commit()

                    await member.send(f'Hello! You have earned **{earnings}** Gaki Coins as daily rewards.')

        cursor.close()
        db.close()

    @gain_daily.before_loop
    async def before_gain_daily(self):
        await self.bot.wait_until_ready()

    # Deposit
    @commands.command(name="d")
    async def deposit(self, ctx, amount: str):
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        cursor.execute(f'SELECT wallet, bank FROM main WHERE user_id = ?', (ctx.author.id,))
        data = cursor.fetchone()

        wallet = data[0] if data else 0
        bank = data[1] if data else 0

        if amount == "all".strip():
            amount = wallet
        else:
            amount = int(amount.replace(",", "").replace(".", ""))

        formatted_amount = "{:,}".format(amount)

        if wallet < amount:
            return await ctx.send("```You do not have enough Gaki coins to deposit```")
        elif amount <= 0:
            return await ctx.send("```You should deposit some Gaki coins```")
        else:
            cursor.execute("UPDATE main SET bank = ? WHERE user_id = ?", (bank + amount, ctx.author.id))
            cursor.execute("UPDATE main SET wallet = ? WHERE user_id = ?", (wallet - amount, ctx.author.id))
            em = discord.Embed(
                description=f"{ctx.author.name} you have deposited **{formatted_amount}** Gaki coins into your bank",
                color=discord.Color.random())
            await ctx.send(embed=em)

        db.commit()
        cursor.close()
        db.close()

    # Withdraw
    @commands.command(name="w")
    async def withdraw(self, ctx, amount: str):
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        cursor.execute(f'SELECT wallet, bank FROM main WHERE user_id = ?', (ctx.author.id,))
        data = cursor.fetchone()

        wallet = data[0] if data else 0
        bank = data[1] if data else 0

        if amount == "all".strip():
            amount = bank
        else:
            amount = int(amount.replace(",", "").replace(".", ""))

        formatted_amount = "{:,}".format(amount)

        if bank < amount:
            return await ctx.send("```You do not have enough Gaki coins to withdraw```")
        elif amount <= 0:
            return await ctx.send("```You should withdraw some Gaki coins```")
        else:
            cursor.execute("UPDATE main SET wallet = ? WHERE user_id = ?", (wallet + amount, ctx.author.id))
            cursor.execute("UPDATE main SET bank = ? WHERE user_id = ?", (bank - amount, ctx.author.id))
            em = discord.Embed(
                description=f"{ctx.author.name} you have withdrawed **{formatted_amount}** Gaki coins from your bank",
                color=discord.Color.random())
            await ctx.send(embed=em)

        db.commit()
        cursor.close()
        db.close()

    # Gamble Game
    @commands.command(name="g")
    async def gamble(self, ctx, amount: str):
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        cursor.execute(f'SELECT wallet FROM main WHERE user_id = ?', (ctx.author.id,))
        wallet = cursor.fetchone()

        try:
            wallet = wallet[0]
        except Exception as e:
            wallet = wallet

        if amount == "all".strip():
            amount = wallet
        else:
            amount = int(amount.replace(",", "").replace(".", ""))

        if wallet < amount:
            return await ctx.reply("```You're too poor to gamble```")
        if amount <= 0:
            return await ctx.reply("```You should gamble some Gaki coins```")

        user_strikes = random.randint(1, 15)
        bot_strikes = random.randint(5, 15)

        if user_strikes > bot_strikes:
            percentage = random.randint(50, 100)
            amount_won = int(amount * (percentage / 100))
            formatted_amount_won = "{:,}".format(amount_won)
            cursor.execute("UPDATE main SET wallet = ? WHERE user_id = ?", (wallet + amount_won, ctx.author.id))
            db.commit()
            embed = discord.Embed(description=f"You won! **{formatted_amount_won}** 🪙\nPercentage **{percentage}%**\n"
                                              f"New Balance **{"{:,}".format(wallet + amount_won)}** 🪙",
                                  color=discord.Color.green())
            embed.set_author(name=f"Wow {ctx.author.name} You are a pro!")

        elif user_strikes < bot_strikes:
            percentage = random.randint(0, 80)
            amount_lost = int(amount * (percentage / 100))
            formatted_amount_lost = "{:,}".format(amount_lost)
            cursor.execute("UPDATE main SET wallet = ? WHERE user_id = ?", (wallet - amount_lost, ctx.author.id))
            db.commit()
            embed = discord.Embed(description=f"You lost! **{formatted_amount_lost}** 🪙\nPercentage **{percentage}%**\n"
                                              f"New Balance **{"{:,}".format(wallet - amount_lost)}** 🪙",
                                  color=discord.Color.red())
            embed.set_author(name=f"Congratulations, you're officially POOR {ctx.author.name}")

        else:
            embed = discord.Embed(description=f"**It was a tie**", color=discord.Color.orange())
            embed.set_author(name=f"Nothing happens here. {ctx.author.name}")

        embed.add_field(name=f"**{ctx.author.name.title()}**", value=f"Strikes {user_strikes}")
        embed.add_field(name=f"**{ctx.bot.user.name.title()}**", value=f"Strikes {bot_strikes}")
        await ctx.reply(embed=embed)

        cursor.close()
        db.close()

    # Slots Game
    @commands.command(name="s")
    async def slots(self, ctx, amount: str):
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        cursor.execute(f'SELECT wallet FROM main WHERE user_id = ?', (ctx.author.id,))
        wallet = cursor.fetchone()
        try:
            wallet = wallet[0]
        except Exception as e:
            wallet = 0

        if amount == "all".strip():
            amount = wallet
        else:
            amount = int(amount.replace(",", "").replace(".", ""))

        if wallet < amount:
            return await ctx.reply("```You're too poor to play slots```")
        if amount <= 0:
            return await ctx.reply("```Slap some coins!```")

        final = []
        for i in range(5):
            a = random.choice(["💎", "🍉", "🍋", "🥝", "🎰"])
            final.append(a)

        # Count occurrences of each fruit
        fruit_count = {fruit: final.count(fruit) for fruit in final}

        if 5 in fruit_count.values():
            times_factors = 5
        elif 4 in fruit_count.values():
            times_factors = 3
        elif 3 in fruit_count.values():
            times_factors = 2
        elif 2 in fruit_count.values():
            times_factors = 1
        else:
            times_factors = 0

        earning = amount * times_factors

        # Format numbers with commas
        formatted_earning = "{:,}".format(earning)
        formatted_amount = "{:,}".format(amount)

        if earning > 0:
            cursor.execute("UPDATE main SET wallet = ? WHERE user_id = ?", (wallet + earning, ctx.author.id))
            db.commit()
            cursor.execute(f'SELECT wallet FROM main WHERE user_id = ?', (ctx.author.id,))
            wallet = cursor.fetchone()[0]
            formatted_wallet = "{:,}".format(wallet)
            embed = discord.Embed(title=f"Slot Machine", color=discord.Color.green())
            embed.add_field(name=f"-----------------------\n{ctx.author.name} Won 🪙 {formatted_earning}"
                                 f"\n-----------------------", value=f"{final}")
            embed.add_field(name=f"-----------------------", value=f"**Multiplier** X{times_factors}", inline=False)
            embed.add_field(name=f"-----------------------", value=f"**New Balance** 🪙 {formatted_wallet} Gaki coins",
                            inline=False)
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/128/13799/13799063.png")
            await ctx.reply(embed=embed)
        else:
            cursor.execute("UPDATE main SET wallet = ? WHERE user_id = ?", (wallet - amount, ctx.author.id))
            db.commit()
            embed = discord.Embed(title=f"Slot Machine", color=discord.Color.red())
            embed.add_field(name=f"{ctx.author.name} Lost 🪙 {formatted_amount}\n-----------------------", value=f"{final}")
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/128/11176/11176407.png")
            await ctx.reply(embed=embed)
            if wallet - amount == 0:
                cursor.execute("UPDATE main SET wallet = ? WHERE user_id = ?", (100, ctx.author.id))
                db.commit()
                embed = discord.Embed(description=f"Here 100 Gaki coins for you. You poor thing.")
                embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/128/4441/4441670.png")
                await ctx.reply(embed=embed)

        cursor.close()
        db.close()

    # Heads/Tail game
    @commands.command(name="f")
    async def coin_flip(self, ctx, expected_result):
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        cursor.execute(f'SELECT wallet FROM main WHERE user_id = ?', (ctx.author.id,))
        wallet = cursor.fetchone()[0]

        cost = 200
        earning = cost * 2
        coin = random.choice(["heads", "tails"])

        formatted_earning = "{:,}".format(earning)

        if wallet >= cost:
            cursor.execute("UPDATE main SET wallet = ? WHERE user_id = ?", (wallet - cost, ctx.author.id))
            db.commit()
            # Update the wallet variable after deducting the cost
            cursor.execute(f'SELECT wallet FROM main WHERE user_id = ?', (ctx.author.id,))
            wallet = cursor.fetchone()[0]

        else:
            cursor.close()
            db.close()
            return await ctx.send("```You don't have enough Gaki coins to flip a coin```")

        # Check if the expected_result is either 'heads' or 'tails'
        if expected_result.lower().strip() not in ["heads", "tails"]:
            return await ctx.send("```Please enter either 'heads' or 'tails'```")

        if expected_result.lower().strip() == coin:
            cursor.execute("UPDATE main SET wallet = ? WHERE user_id = ?", (wallet + earning, ctx.author.id))
            db.commit()
            # Update the wallet variable after winning
            cursor.execute(f'SELECT wallet FROM main WHERE user_id = ?', (ctx.author.id,))
            wallet = cursor.fetchone()[0]
            formatted_wallet = "{:,}".format(wallet)
            embed = discord.Embed(title=f"Heads or Tails??", color=discord.Color.green())
            embed.add_field(
                name=f"-----------------------\n{ctx.author.name} just won 🪙 {formatted_earning} Gaki coins!"
                     f"\n-----------------------", value=f"I just flipped **{coin}**")
            embed.add_field(name=f"-----------------------", value=f"**New Balance** 🪙 {formatted_wallet} Gaki coins",
                            inline=False)
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/128/867/867453.png")
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title=f"Heads or Tails??", color=discord.Color.red())
            embed.add_field(name=f"-----------------------\n{ctx.author.name} Lost 🪙 {cost} Gaki coins!"
                                 f"\n-----------------------", value=f"I just flipped **{coin}**")
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/128/867/867453.png")
            await ctx.reply(embed=embed)
            if wallet == 0:
                cursor.execute("UPDATE main SET wallet = ? WHERE user_id = ?", (100, ctx.author.id))
                db.commit()
                embed = discord.Embed(description=f"Here 100 Gaki coins for you. You poor thing.")
                embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/128/4441/4441670.png")
                await ctx.reply(embed=embed)

        cursor.close()
        db.close()

