"""
Baki bot
"""


import asyncio
import os

import discord
from discord.ext import commands

# Import cogs
from gamble_cog import Gamble
from greetings_cog import GreetingsCog


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='-', intents=intents)
bot.remove_command('help')


async def main():
    await bot.add_cog(GreetingsCog(bot))
    await bot.add_cog(Gamble(bot))
    await bot.start(os.getenv('BAKI_TOKEN'))

asyncio.run(main())







