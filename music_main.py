"""
Gandalf - The DJ bot
"""

import asyncio
import os

import discord
from discord.ext import commands

# Import cogs
from help_cog import HelpCog
from music_cog import MusicCog

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

# Remove the default help command so that we can write out own
bot.remove_command('help')


async def main():
    async with bot:
        await bot.add_cog(HelpCog(bot))
        await bot.add_cog(MusicCog(bot))
        await bot.start(os.getenv('GANDALF_TOKEN'))


# Run main function asynchronously and run the bot
asyncio.run(main())
