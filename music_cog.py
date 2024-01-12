"""
This is the music cog that will be called in music_main.
It belongs to Gandalf - The DJ bot in deputy's server.
"""

import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
import asyncio


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Track the bot's playback status
        self.is_playing = False
        self.is_paused = False

        # 2nd array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best'}  # YouTube downloader
        self.FFMPEG_OPTIONS = {'options': '-vn',
                               'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}

        self.vc = None
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)     # Instance of the 'YouTubeDL' class

    # Search the item on YouTube
    def search_yt(self, item):
        if item.startswith("https://"):
            # If the item is a valid URL, it extracts the title from the URL
            title = self.ytdl.extract_info(item, download=False)['title']
            return {'source': item, 'title': title}
        # If the item is a search query, it uses the 'VideosSearch' library to find the top result
        # and returns its link and title
        search = VideosSearch(item, limit=1)
        return {'source': search.result()["result"][0]["link"], 'title': search.result()["result"][0]["title"]}

    # Play music: starts playing music
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            # Try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                # If connection is failed
                if self.vc == None:
                    await ctx.send("```Could not connect to the voice channel```")
                    return
            # Moves to the current voice channel
            else:
                await self.vc.move_to(self.music_queue[0][1])

            # Play next song in queue
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.FFMPEG_OPTIONS),
                         after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False

    # Commands
    # Play
    @commands.command(name="play", help="Plays a selected song from YouTube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        channel_id = 1193754397243609158
        try:
            voice_channel = discord.utils.get(ctx.guild.voice_channels, id=channel_id)
        except:
            await ctx.send("```You need to connect to a voice channel first!```")
            return
        if self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send(
                    "```Could not donwload the song. Incorrect format try another keyboeard. This could be due to playlist or a livestream format.```")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.music_queue) + 2} - '{song['title']}'** added to the queue")
                else:
                    await ctx.send(f"**'{song['title']}'** added to the queue")
                self.music_queue.append([song, voice_channel])
                if self.is_playing == False:
                    await self.play_music(ctx)

    # Pause
    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    # Resume
    @commands.command(name="resume", help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    # Skip
    @commands.command(name="skip", help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            # Try to play next in the queue if it exists
            await self.play_music(ctx)

    # Queue
    @commands.command(name="queue", help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f"#{i + 1} -" + self.music_queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(f"```queue:\n{retval}```")
        else:
            await ctx.send("```No music in queue```")

    # Clear
    @commands.command(name="clear", help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("```Music queue cleared```")

    # Stop
    @commands.command(name="stop", help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

    # Remove
    @commands.command(name="remove", help="Removed last song added to the queue")
    async def re(self, ctx):
        self.music_queue.pop()
        await ctx.send("```Last song removed```")
