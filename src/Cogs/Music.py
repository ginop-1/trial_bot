import nextcord
from nextcord.ext import commands
import youtube_dl
import asyncio
from Utils.funcs import Functions as funcs
from Utils.storage import storage as stg


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.song_queue = []

    @commands.command(name="play", aliases=["P", "p"])
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

        await funcs.join(self.bot, ctx)
        voice = funcs.actual_voice_channel(self.bot)

        if not voice.is_playing() and len(self.song_queue) == 1:
            msg = await ctx.send(
                embed=funcs.get_embed("Now Playing", -1, self.song_queue)
            )
            voice.play(
                nextcord.FFmpegPCMAudio(
                    source=funcs.get_url_video(self.song_queue[0])
                ),
                after=lambda e: self.play_next(ctx, msg),
            )
        else:
            await ctx.send(
                embed=funcs.get_embed("Added to queue", -1, self.song_queue),
                delete_after=30,
            )

    def play_next(self, ctx, msg):
        coro = msg.delete()
        fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
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
        vc = funcs.actual_voice_channel(self.bot)
        coro = ctx.send(
            embed=funcs.get_embed("Now Playing", 0, self.song_queue)
        )
        fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
        try:
            msg = fut.result()
        except:
            pass
        vc.play(
            nextcord.FFmpegPCMAudio(
                source=funcs.get_url_video(self.song_queue[0])
            ),
            after=lambda e: self.play_next(ctx, msg),
        )

    @commands.command(name="queue", aliases=["Q", "q"])
    async def queue(self, ctx):
        if not self.song_queue:
            return await ctx.send(
                embed=nextcord.Embed(title="No songs in queue")
            )
        queue_list = "\n".join(
            [
                f"{i+1}\t- {song_title['title']}"
                if i
                else f"**Now Playing:** {song_title['title']}"
                for i, song_title in enumerate(self.song_queue)
            ]
        )[: stg.CHARS_LIMIT]
        await ctx.send(
            embed=nextcord.Embed(
                title="Queue:",
                color=0xFF0000,
                description=queue_list,
            )
        )

    @commands.command(name="skip")
    async def skip(self, ctx):
        voice = funcs.actual_voice_channel(self.bot)
        if voice is None:
            return print("not in a voice channel")
        if voice.is_playing():
            await ctx.message.add_reaction("⏭")
            voice.stop()

    @commands.command(name="pause")
    async def pause(self, ctx):
        voice = funcs.actual_voice_channel(self.bot)
        if voice is None:
            return print("not in a voice channel")
        if voice.is_playing():
            await ctx.message.add_reaction("⏸")
            voice.pause()
        else:
            await ctx.send("Currently no audio is playing.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        voice = funcs.actual_voice_channel(self.bot)
        if voice is None:
            return print("not in a voice channel")
        if not voice.is_playing():
            await ctx.message.add_reaction("▶️")
            return voice.resume()
        await ctx.send("The audio is not paused.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        self.song_queue.clear()
        voice = funcs.actual_voice_channel(self.bot)
        if voice is None:
            return print("not in a voice channel")
        await ctx.message.add_reaction("🛑")
        voice.stop()


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))
