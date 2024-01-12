"""
This is the help cog that will be called in music_main.
It belongs to Gandalf - The DJ bot in deputy's server.
"""

import discord
from discord.ext import commands
import music_cog


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.music_queue = None
        self.vc = None  # Voice channel
        self.bot = bot
        self.help_message = ""
        self.text_channel_list = []
        self.set_message()

    # Define the help message
    def set_message(self):
        embed = discord.Embed(
            title='Gandalf\'s Bot Commands',
            description='Welcome to the help section. Here are all the commands for playing music!',
            color=discord.Colour.blurple()
        )

        embed.set_thumbnail(url='https://cdn-icons-png.flaticon.com/128/2907/2907253.png')

        embed.add_field(
            name='/help',
            value='List all DJ Gandalf\'s commands',
            inline=False
        )
        embed.add_field(
            name='/queue',
            value='Displays the current music queue',
            inline=False
        )
        embed.add_field(
            name='/play <keywords>',
            value='Finds the song on youtube and plays it in your current channel. '
                  'Will resume playing the current song if it was paused',
            inline=False
        )
        embed.add_field(
            name='/skip',
            value='Skips the current song being played',
            inline=False
        )
        embed.add_field(
            name='/clear',
            value='Stops the music and clears the queue',
            inline=False
        )
        embed.add_field(
            name='/stop',
            value='Disconnects the bot from the voice channel',
            inline=False
        )
        embed.add_field(
            name='/pause',
            value='Pauses the current song being played or resumes if already paused',
            inline=False
        )
        embed.add_field(
            name='/resume',
            value='Resumes playing the current song',
            inline=False
        )
        embed.add_field(
            name='/prefix',
            value='Change command prefix',
            inline=False
        )
        embed.add_field(
            name='/remove',
            value='Removes last song from the queue',
            inline=False
        )

        self.help_message = embed

    # Bot ready and online
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(f"type {self.bot.command_prefix}help"))

    # Help
    @commands.command(name="help", help="Displays all the available commands")
    async def help(self, ctx):
        await ctx.send(embed=self.help_message) # help_message has been set in set_message()

    # Prefix
    @commands.command(name="prefix", help="change bot prefix")
    async def prefix(self, ctx, *args):
        self.bot.command_prefix = " ".join(args)
        self.set_message()
        await ctx.send(f"Prefix set to **'{self.bot.command_prefix}'**")
        await self.bot.change_presence(activity=discord.Game(f"type {self.bot.command_prefix}help"))

