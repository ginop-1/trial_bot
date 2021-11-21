import nextcord
from nextcord.ext import commands
import yt_dlp
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

        url = funcs.get_url_video(guild_id=ctx.guild.id, url=url)
        if not url:
            # never gonna give u up
            return await ctx.send(
                "",
                embed=nextcord.Embed(
                    description=f"[Download there]"
                    + f"(http://bitly.com/98K8eH)",
                ),
            )
        wasEmpty = not bool(len(self.song_queue))

        if isinstance(url, list):
            self.song_queue = self.song_queue + url
        else:
            print("not a list")
            self.song_queue.append(url)

        await funcs.join(self.bot, ctx)
        voice = funcs.actual_voice_channel(self.bot)

        if not voice.is_playing() and wasEmpty:
            msg = await ctx.send(
                embed=funcs.get_embed("Now Playing", -1, self.song_queue)
            )
            funcs.download_audio(
                guild_id=ctx.guild.id, video=self.song_queue[0]
            )
            voice.play(
                nextcord.FFmpegPCMAudio(source=self.song_queue[0]["url"]),
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
        funcs.download_audio(guild_id=ctx.guild.id, video=self.song_queue[0])
        vc.play(
            nextcord.FFmpegPCMAudio(source=self.song_queue[0]["url"]),
            after=lambda e: self.play_next(ctx, msg),
        )

    @commands.command(name="queue", aliases=["Q", "q"])
    async def queue(self, ctx):
        if not self.song_queue:
            return await ctx.send(
                embed=nextcord.Embed(title="No songs in queue")
            )
        queue_list = [
            f"{i+1}\t- {song_title['title']}"
            if i
            else f"**Now Playing:** {song_title['title']}"
            for i, song_title in enumerate(self.song_queue)
        ]
        if len(queue_list) > 10:
            queue_list = "\n".join(queue_list[:10]) + "\n..."
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
