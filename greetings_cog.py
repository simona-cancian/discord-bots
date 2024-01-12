"""
This is the help cog that will be called in baki_main.
It belongs to Baki bot in deputy's server.
"""


import discord
from discord.ext import commands
import requests
import json


class GreetingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged on as', self.bot.user)
        await self.bot.change_presence(activity=discord.Game(f"type {self.bot.command_prefix}help"))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        latency = self.bot.latency * 1000  # Convert to milliseconds

        if message.content == 'ping':
            embed = discord.Embed(description=f"Pong ~ 🏓 In {latency:.2f}ms!", color=discord.Color.random())
            await message.channel.send(embed=embed)

        if message.content == 'cool':
            await message.add_reaction('\U0001F60E')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Send a welcome message to the new member
        channel = member.guild.system_channel  # Get the default channel of the server
        if channel is not None:
            await channel.send(f"Welcome to the server, {member.mention}!")

    # Commands
    # Info
    @commands.command()
    async def info(self, ctx):
        await ctx.send(ctx.guild)
        await ctx.send(ctx.author)
        await ctx.send(ctx.channel)

    # Greet
    @commands.command()
    async def greet(self, ctx):
        # Send a greeting message to the channel where the command was invoked
        await ctx.send(f'Hello {ctx.author.mention}! Welcome to this channel!')

    # Greet All
    @commands.command()
    async def greet_all(self, ctx):
        for member in ctx.guild.members:
            # Check if member is a bot
            if member.bot or member == ctx.bot.user:
                continue
            try:
                # Send a greeting message to each non-bot member
                await ctx.send(f'Hello {member.mention}! Welcome to {ctx.guild}!')
            except discord.Forbidden:
                # If message cannot be sent by the bot, skip them
                continue

    # Dad Joke
    @commands.command()
    async def joke(self, ctx):
        # Send an HTTP GET request to this API to fetch a dad joke
        # 'headers' parameter specifies that the response should be in JSON format
        response = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"})
        if response.status_code == 200:
            # This method parses the content of the response as JSON and converts it into a Python dictionary
            joke_data = response.json()
            # Extracts the joke text from the dictionary
            joke_text = joke_data['joke']
            embed = discord.Embed(description=f"**{joke_text}**", color=discord.Color.random())
            embed.set_thumbnail(url="https://img.icons8.com/?size=48&id=PjUpgs6o2IFx&format=png")
            await ctx.send(embed=embed)
        else:
            await ctx.send("```Sorry, I couldn't fetch a dad joke right now. Try again later.```")

    # Anime
    @commands.command()
    async def anime(self, ctx, *, query):
        # Sets the URL for the AniList GraphQL API
        url = 'https://graphql.anilist.co/'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        # Defines a GraphQL query string
        query_string = '''
        query ($search: String) {
          Media (search: $search, type: ANIME) {
            title {
              romaji
              english
              native
            }
            description(asHtml: false)
            episodes
            status
            averageScore
            coverImage {
              large
            }
          }
        }
        '''
        # Sets the GraphQL variable '$search' to the input provided by the user when invoking the command
        variables = {'search': query}

        try:
            # Sends a POST request to this API with the specified query and variables
            response = requests.post(url, headers=headers, json={'query': query_string, 'variables': variables})
            response.raise_for_status()  # Raise HTTPError for bad status codes
            data = response.json()

            if 'errors' in data:
                await ctx.send(f"Error: {data['errors'][0]['message']}")
            # If there are no errors, extracts relevant information about the anime from the API response
            elif 'data' in data and data['data']['Media']:
                anime_data = data['data']['Media']

                title = anime_data['title']['romaji'] or anime_data['title']['english'] or anime_data['title']['native']
                description = anime_data['description']
                episodes = anime_data['episodes']
                status = anime_data['status']
                score = anime_data['averageScore']
                cover_image = anime_data['coverImage']['large']

                embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
                embed.add_field(name="Episodes", value=episodes, inline=True)
                embed.add_field(name="Status", value=status, inline=True)
                embed.add_field(name="Average Score", value=score, inline=True)
                embed.set_image(url=cover_image)

                await ctx.send(embed=embed)
            else:
                await ctx.send("Anime not found.")
        except requests.HTTPError as e:
            await ctx.send(f"Error fetching data from AniList API: {e}")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    # Help
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title='Baki\'s Bot Commands',
            description='Welcome to the help section. Here are all the commands for greeting members '
                        'and playing casino!',
            color=discord.Colour.yellow()

        )

        embed.set_thumbnail(url='https://cdn-icons-png.flaticon.com/128/2314/2314797.png')

        embed.add_field(
            name='-help',
            value='List all Baki\'s commands',
            inline=False
        )
        embed.add_field(
            name='-greet',
            value='Greet the member who called this command',
            inline=False
        )
        embed.add_field(
            name='-b',
            value='Check your balance',
            inline=False
        )
        embed.add_field(
            name='-d <amount>',
            value='Deposit some coins into your wallet',
            inline=False
        )
        embed.add_field(
            name='-w <amount>',
            value='Withdraw some coins from your bank',
            inline=False
        )
        embed.add_field(
            name='-g <amount>',
            value='Gamble some coins',
            inline=False
        )
        embed.add_field(
            name='-s <amount>',
            value='Slap some coins',
            inline=False
        )
        embed.add_field(
            name='-f <heads> or <tails>',
            value='Flip a coin',
            inline=False
        )
        embed.add_field(
            name='-joke',
            value='Tells a dad joke',
            inline=False
        )
        embed.add_field(
            name='-anime <keywords>',
            value='Shows info on the selected anime',
            inline=False
        )

        await ctx.send(embed=embed)
