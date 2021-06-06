#!./env/bin/python3

import os
import random
import wikipedia_for_humans
import discord
import asyncio
from gtts import gTTS
from discord.ext import commands
import youtube_dl
# Custom
from storage import storage

intents = discord.Intents.default()
intents.members = True


class Utility():
    """Class
    It contains useful function to clean up code
    """

    def _actual_voice_channel(ctx):
        return discord.utils.get(bot.voice_clients, guild=ctx.guild)

    def get_url_video(video_info: dict):
        # print(video_info['formats'])
        return video_info['formats'][0]['url']

    def get_embed(title: str, index: int, song_queue: dict()):
        red_color = 0xff0000
        # print(song_queue)
        embedvar = discord.Embed(
            title=title,
            description=f"[{song_queue[index]['title']}]" +
                        f"({Utility.get_url_video(song_queue[index])})",
            color=red_color)
        return embedvar


class main_bot(commands.Cog):
    '''
    Main class
    ----------
    contains all commands
    '''

    def __init__(self, bot):
        self.bot = bot
        queue = self.song_queue = []

    @commands.command(name="join")
    async def join(self, ctx):
        if Utility._actual_voice_channel(ctx) is not None:
            ctx.send("Alread connected to a voice channel")
        channel = ctx.author.voice.channel
        connected = await channel.connect()
        connected.play(
            discord.FFmpegPCMAudio(
                source='./sounds/user-joined-your-channel.mp3'), )

    @commands.command(name="leave")
    async def leave(self, ctx):
        guild = ctx.guild
        voice_client = Utility._actual_voice_channel(ctx)
        audio_source = discord.FFmpegPCMAudio(
            source='./sounds/teamspeak_disconnect.mp3')
        if not voice_client.is_playing():
            voice_client.play(audio_source, after=None)
        while voice_client.is_playing():
            await asyncio.sleep(1)
        await voice_client.disconnect()

    @commands.command(name="offendi")
    async def shame(self, ctx, *argv):
        words = ' '.join(argv)
        # IDK why but using directly storage.offese[index] not works
        offese = storage.offese
        response = words + offese[random.randint(0, len(offese) - 1)]
        await ctx.send(response)
        voice = Utility._actual_voice_channel(ctx)
        if voice is None:
            channel = ctx.author.voice.channel
            voice = await channel.connect()
        tts = gTTS(response, lang='it')
        tts.save('yes.mp3')
        if not voice.is_playing():
            voice.play(discord.FFmpegPCMAudio(source='./yes.mp3'), after=None)

    @commands.command(name="wiki")
    async def wiki(self, ctx, *argv):

        async def _page_not_found(ctx):
            return await ctx.send("Page not found")

        words = ' '.join(argv)
        try:
            search = str(wikipedia_for_humans.summary(words))
            title = str(wikipedia_for_humans._get_title(words))
        except Exception as e:
            return await _page_not_found(ctx)

        if search == "" or search is None:
            return await _page_not_found(ctx)

        '''
        uncomment this lines for TTS
        tts = gTTS(search, lang="it")
        tts.save('yes.mp3')
        
        voice_client: discord.VoiceClient = discord.utils.get(
            bot.voice_clients, guild=ctx.guild)
        audio_source = discord.FFmpegPCMAudio(source='./yes.mp3')
        try:
            if not voice_client.is_playing():
                voice_client.play(audio_source, after=None)
        except AttributeError as err:
            print("not in a voice channel")
        '''
        search = f"**{title}**:\n" + search.splitlines()[0]
        if len(search) > 2000:
            # discord 2000 char limit
            search = search[:2000]
        return await ctx.send(search)

    @commands.command(name='killall')
    async def killall(self, ctx):
        # print(f"ctx type: {type(ctx)}")
        # if the author is connected to a voice channel
        if not ctx.author.voice:
            return await ctx.send("You need to be in a voice channel!")
        if ctx.message.author.id == storage.GINO_ID:
            users = ctx.message.author.voice.channel.members
            for user in users:
                await user.move_to(None, reason="Nibba")
            # await ctx.send("Kicked all the members from the voice channel")

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *argv):

        # Get the ytsarch + search word for initial searching
        video_info = "ytsearch:" + ' '.join(argv)

        # Get the info about the video. Dict['entries'][0]['blablabla']
        video_info = youtube_dl.YoutubeDL(storage.ydl_opts).extract_info(
            video_info, download=False)['entries'][0]
        self.song_queue.append(video_info)
        voice = Utility._actual_voice_channel(ctx)
        # queue.append(url)
        # not connected to voice channel
        if voice is None:
            voice = await ctx.author.voice.channel.connect()

        if not voice.is_playing():
            # print(self.song_queue[0])
            # print(self.song_queue[-1]['title'])
            message = await ctx.send(embed=Utility.get_embed(
                "Now Playing", -1, self.song_queue)
            )
            voice.play(discord.FFmpegPCMAudio(source=Utility.get_url_video(video_info)),
                       after=lambda e: self.play_next(ctx, message))
        else:
            await ctx.send(embed=Utility.get_embed(
                "Added to queue", -1, self.song_queue), delete_after=30)
            # voice.play(discord.FFmpegOpusAudio("song.mp3"))

    def play_next(self, ctx, message):
        coro = message.delete()
        fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            fut.result()
        except:
            pass
        try:
            del self.song_queue[0]
        except IndexError as e:
            return
        if len(self.song_queue) == 0:
            return
        vc = Utility._actual_voice_channel(ctx)
        coro = ctx.send(embed=Utility.get_embed(
            "Now Playing", 0, self.song_queue))
        fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            coro = fut.result()
        except:
            pass
        vc.play(discord.FFmpegPCMAudio(
            source=Utility.get_url_video(self.song_queue[0])),
            after=lambda e: self.play_next(ctx, coro)
        )

    @commands.command(name="skip")
    async def skip(self, ctx):
        voice = Utility._actual_voice_channel(ctx)
        if voice is None:
            return print("not in a voice channel")
        if voice.is_playing():
            await ctx.message.add_reaction("⏭")
            voice.stop()

    @commands.command(name="pause")
    async def pause(self, ctx):
        voice = Utility._actual_voice_channel(ctx)
        if voice is None:
            return print("not in a voice channel")
        if voice.is_playing():
            await ctx.message.add_reaction("⏸")
            voice.pause()
        else:
            await ctx.send("Currently no audio is playing.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        voice = Utility._actual_voice_channel(ctx)
        if voice is None:
            return print("not in a voice channel")
        if not voice.is_playing():
            await ctx.message.add_reaction("▶️")
            return voice.resume()
        await ctx.send("The audio is not paused.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        self.song_queue.clear()
        voice = Utility._actual_voice_channel(ctx)
        if voice is None:
            return print("not in a voice channel")
        await ctx.message.add_reaction("🛑")
        voice.stop()


bot = commands.Bot(command_prefix="?", intents=intents)
bot.add_cog(main_bot(bot))
bot.run(storage.TOKEN)
