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

    def _args_to_str(args):
        word = ""
        for arg in args:
            word = word + " " + arg
        return word

    def _actual_voice_channel(ctx):
        return discord.utils.get(bot.voice_clients, guild=ctx.guild)

    def get_url_video(info: dict):
        return "https://www.youtube.com/watch?v="+info['id']


class main_bot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
        self.song_path = "./sounds/queue/song.mp3"

    @commands.command(name="join")
    async def join(self, ctx):
        print(type(ctx))
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
        words = Utility._args_to_str(argv)
        offese = storage.offese
        parlare_asd = words + offese[random.randint(0, len(offese) - 1)]
        await ctx.send(parlare_asd)
        voice = Utility._actual_voice_channel(ctx)
        if voice is None:
            channel = ctx.author.voice.channel
            voice = await channel.connect()
        tts = gTTS(parlare_asd, lang='it')
        tts.save('yes.mp3')
        if not voice.is_playing():
            voice.play(discord.FFmpegPCMAudio(source='./yes.mp3'), after=None)

    @commands.command(name="wiki")
    async def wiki(self, ctx, *argv):
        words = Utility._args_to_str(argv)
        try:
            search = str(wikipedia_for_humans.summary(words))
        except Exception as e:
            await ctx.send("Page not found, error")
            search = None
            return

        if search is None:
            return

        if search != "":
            # tts = gTTS(search, lang="it")
            # tts.save('yes.mp3')
            '''
            voice_client: discord.VoiceClient = discord.utils.get(
                bot.voice_clients, guild=ctx.guild)
            audio_source = discord.FFmpegPCMAudio(source='./yes.mp3')
            try:
                if not voice_client.is_playing():
                    voice_client.play(audio_source, after=None)
            except AttributeError as err:
                print("not in a voice channel")
            '''
            search = search.splitlines()[0]
            if len(search) > 2000:
                search = search[:2000]
            return await ctx.send(search)

        return await ctx.send("Page not found")

    @commands.command(name='killall')
    async def killall(self, ctx):
        # if the author is connected to a voice channel
        if ctx.author.voice:
            if ctx.message.author.id == storage.GINO_ID:
                channel = ctx.message.author.voice.channel
                users = channel.members
                # print(users)
                for user in users:
                    await user.edit(voice_channel=None)
                # await ctx.send("Kicked all the members from the voice channel")
        else:
            await ctx.send("You need to be in a voice channel!")
            return

    @commands.command(name="play")
    async def play(self, ctx, *argv):
        
        # Get the ytsarch + search word for initial searching
        video_info = "ytsearch:"+Utility._args_to_str(argv)

        # Get the info about the video. Dict['entries'][0]['blablabla']
        video_info = youtube_dl.YoutubeDL(storage.ydl_opts).extract_info(
            video_info, download=False)['entries'][0]
        # print(url)
        self.song_queue.append(Utility.get_url_video(video_info))
        voice = Utility._actual_voice_channel(ctx)
        # queue.append(url)
        # not connected to voice channel
        if voice is None:
            voice = await ctx.author.voice.channel.connect()

        if not voice.is_playing():
            print(self.song_queue[0])
            if os.path.isfile(self.song_path):
                os.remove(self.song_path)
            with youtube_dl.YoutubeDL(storage.ydl_opts) as ydl:
                ydl.download([self.song_queue[0]])
            voice.play(discord.FFmpegOpusAudio(source=self.song_path),
                       after=lambda e: self.play_next(ctx))
        else:
            await ctx.send(embed=discord.Embed(title=f"Added to que: {video_info['title']}"))
            # voice.play(discord.FFmpegOpusAudio("song.mp3"))

    def play_next(self, ctx):
        if len(self.song_queue) < 1:
            return
        del self.song_queue[0]
        if len(self.song_queue) == 0:
            return
        os.remove(self.song_path)
        # print("Now playing:"+self.song_queue[0]['title'])
        with youtube_dl.YoutubeDL(storage.ydl_opts) as ydl:
            ydl.download([self.song_queue[0]])
        vc = Utility._actual_voice_channel(ctx)
        vc.play(discord.FFmpegPCMAudio(
            source=self.song_path),
            after=lambda e: self.play_next(ctx)
        )
        return

    @commands.command(name="pause")
    async def pause(self, ctx):
        voice = Utility._actual_voice_channel(ctx)
        if voice is None:
            print("not in a voice channel")
            return
        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send("Currently no audio is playing.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        voice = Utility._actual_voice_channel(ctx)
        if voice is None:
            print("not in a voice channel")
            return
        if not voice.is_playing():
            voice.resume()
        else:
            await ctx.send("The audio is not paused.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        self.song_queue.clear()
        voice = Utility._actual_voice_channel(ctx)
        voice.stop()


bot = commands.Bot(command_prefix="?", intents=intents)
bot.add_cog(main_bot(bot))
bot.run(storage.TOKEN)
