import random
import wikipedia_for_humans
import discord
import asyncio
from gtts import gTTS
from discord.ext import commands, tasks
import youtube_dl

# Custom
from storage import storage

intents = discord.Intents.default()
intents.members = True


class Utility:
    """
    It contains useful function to clean up code
    """

    def actual_voice_channel(ctx):
        return discord.utils.get(bot.voice_clients, guild=ctx.guild)

    def get_url_video(video_info: dict):
        with youtube_dl.YoutubeDL(storage.ydl_opts) as downloader:
            video_info = downloader.extract_info(
                f"{video_info['id']}", download=False
            )
        # print(video_info['formats'])
        return video_info["url"]

    def get_embed(title: str, index: int, song_queue: dict()):
        red_color = 0xFF0000
        # print(song_queue)
        embedvar = discord.Embed(
            title=title,
            description=f"[{song_queue[index]['title']}]"
            + f"({Utility.get_url_video(song_queue[index])})",
            color=red_color,
        )
        return embedvar


class main_bot(commands.Cog):
    """
    Contains all commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
        self.auto_leave_afk.start()

    @tasks.loop(minutes=2)
    async def auto_leave_afk(self):
        voice = discord.utils.get(bot.voice_clients)
        # print(voice)
        if not voice:
            return
        if not voice.is_playing():
            await voice.disconnect()

    @commands.command(name="join")
    async def join(self, ctx):
        """
        Join in a voice channel
        """
        if Utility.actual_voice_channel(ctx) is not None:
            ctx.send("Alread connected to a voice channel")
        channel = ctx.author.voice.channel
        connected = await channel.connect()
        connected.play(
            discord.FFmpegPCMAudio(
                source="./sounds/user-joined-your-channel.mp3"
            ),
        )

    @commands.command(name="leave")
    async def leave(self, ctx):
        voice_client = Utility.actual_voice_channel(ctx)
        audio_source = discord.FFmpegPCMAudio(
            source="./sounds/teamspeak_disconnect.mp3"
        )
        if not voice_client.is_playing():
            voice_client.play(audio_source, after=None)
        while voice_client.is_playing():
            await asyncio.sleep(1)
        await voice_client.disconnect()

    @commands.command(name="offendi")
    async def offend(self, ctx, *argv):
        words = " ".join(argv)
        # IDK why but using directly storage.offese[index] not works
        offese = storage.offese
        response = words + offese[random.randint(0, len(offese) - 1)]
        await ctx.send(response)
        voice = Utility.actual_voice_channel(ctx)
        if voice is None:
            channel = ctx.author.voice.channel
            voice = await channel.connect()
        tts = gTTS(response, lang="it")
        tts.save("yes.mp3")
        if not voice.is_playing():
            voice.play(discord.FFmpegPCMAudio(source="./yes.mp3"), after=None)

    @commands.command(name="wiki")
    async def wiki(self, ctx, *argv):
        async def _page_not_found(ctx):
            return await ctx.send("Page not found")

        words = " ".join(argv)
        try:
            search = str(wikipedia_for_humans.summary(words))
            title = str(wikipedia_for_humans._get_title(words))
        except Exception as e:
            return await _page_not_found(ctx)

        if search == "" or search is None:
            return await _page_not_found(ctx)

        """
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
        """
        search = f"**{title}**:\n" + search.splitlines()[0]
        if len(search) >= storage.CHARS_LIMIT:
            # discord 2000 char limit
            search = search[: storage.CHARS_LIMITS]
        return await ctx.send(search)

    @commands.command(name="killall")
    async def killall(self, ctx):
        # if the author is connected to a voice channel
        if not ctx.author.voice:
            return await ctx.send("You need to be in a voice channel!")
        if ctx.message.author.id == storage.GINO_ID:
            users = ctx.message.author.voice.channel.members
            for user in users:
                await user.move_to(None, reason="Nibba")

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *argv):
        url = " ".join(argv)  # get the url (or name) of video

        with youtube_dl.YoutubeDL({"extract_flat": True}) as downloader:
            try:
                video_info = downloader.extract_info(url, download=False)
            except youtube_dl.DownloadError as e:
                # not valid url (ex: Despacito)
                video_info = downloader.extract_info(
                    f"ytsearch:{url}", download=False
                )
        webpg_bsname = video_info["webpage_url_basename"]
        if webpg_bsname == "watch":
            # valid url
            self.song_queue.append(video_info)
        elif webpg_bsname == "playlist":
            [self.song_queue.append(i) for i in video_info["entries"]]
        else:
            # not valid url
            self.song_queue.append(video_info["entries"][0])

        voice = Utility.actual_voice_channel(ctx)

        if voice is None:
            voice = await ctx.author.voice.channel.connect()

        if not voice.is_playing():
            msg = await ctx.send(
                embed=Utility.get_embed("Now Playing", -1, self.song_queue)
            )
            voice.play(
                discord.FFmpegPCMAudio(
                    source=Utility.get_url_video(self.song_queue[0])
                ),
                after=lambda e: self.play_next(ctx, msg),
            )
        else:
            await ctx.send(
                embed=Utility.get_embed("Added to queue", -1, self.song_queue),
                delete_after=30,
            )

    def play_next(self, ctx, msg):
        coro = msg.delete()
        fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            fut.result()
        except:
            pass
        try:
            del self.song_queue[0]
        except IndexError as e:
            return
        if not len(self.song_queue):
            return
        vc = Utility.actual_voice_channel(ctx)
        coro = ctx.send(
            embed=Utility.get_embed("Now Playing", 0, self.song_queue)
        )
        fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            msg = fut.result()
        except:
            pass
        vc.play(
            discord.FFmpegPCMAudio(
                source=Utility.get_url_video(self.song_queue[0])
            ),
            after=lambda e: self.play_next(ctx, msg),
        )

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx):
        if not len(self.song_queue):
            return await ctx.send(
                embed=discord.Embed(title="No songs in queue")
            )
        await ctx.send(
            embed=discord.Embed(
                title="Queue:",
                color=0xFF0000,
                description="\n".join(
                    [
                        f"{i+1}\t- {song_title['title']}"
                        for i, song_title in enumerate(self.song_queue)
                    ]
                )[: storage.CHARS_LIMIT],
            )
        )

    @commands.command(name="skip")
    async def skip(self, ctx):
        voice = Utility.actual_voice_channel(ctx)
        if voice is None:
            return print("not in a voice channel")
        if voice.is_playing():
            await ctx.message.add_reaction("⏭")
            voice.stop()

    @commands.command(name="pause")
    async def pause(self, ctx):
        voice = Utility.actual_voice_channel(ctx)
        if voice is None:
            return print("not in a voice channel")
        if voice.is_playing():
            await ctx.message.add_reaction("⏸")
            voice.pause()
        else:
            await ctx.send("Currently no audio is playing.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        voice = Utility.actual_voice_channel(ctx)
        if voice is None:
            return print("not in a voice channel")
        if not voice.is_playing():
            await ctx.message.add_reaction("▶️")
            return voice.resume()
        await ctx.send("The audio is not paused.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        self.song_queue.clear()
        voice = Utility.actual_voice_channel(ctx)
        if voice is None:
            return print("not in a voice channel")
        await ctx.message.add_reaction("🛑")
        voice.stop()


bot = commands.Bot(command_prefix="?", intents=intents)
bot.add_cog(main_bot(bot))
bot.run(storage.TOKEN)
