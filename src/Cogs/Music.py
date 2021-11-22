import nextcord
from nextcord.ext import commands
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
            await self.start_songs_loop(ctx)
        else:
            await ctx.send(
                embed=funcs.get_embed("Added to queue", -1, self.song_queue),
                delete_after=30,
            )

    async def start_songs_loop(self, ctx):
        voice = funcs.actual_voice_channel(self.bot)
        while self.song_queue:
            funcs.download_audio(
                guild_id=ctx.guild.id, video=self.song_queue[0]
            )
            msg = await ctx.send(
                embed=funcs.get_embed("Now playing", 0, self.song_queue)
            )
            voice.play(
                nextcord.FFmpegPCMAudio(source=self.song_queue[0]["url"])
            )
            while voice.is_playing():
                await asyncio.sleep(1)
                try:
                    self.song_queue[0]["time_elapsed"] += int(
                        voice.is_playing()
                    )
                except IndexError as e:
                    return
            try:
                del self.song_queue[0]
            except IndexError as e:
                return
            await msg.delete()

    @commands.command(name="queue", aliases=["Q", "q"])
    async def queue(self, ctx):
        if not self.song_queue:
            return await ctx.send(
                embed=nextcord.Embed(title="No songs in queue")
            )
        queue_list = [
            f"{i+1}\t- {video['title']}"
            if i
            else f"**Now Playing:** {video['title']}"
            for i, video in enumerate(self.song_queue)
        ]
        queue_list = "\n".join(queue_list[:10])
        if len(queue_list.split("\n")) > 10:
            queue_list += "\n..."
        await ctx.send(
            embed=nextcord.Embed(
                title="Queue:",
                color=0xFF0000,
                description=queue_list,
            )
        )

    @commands.command(name="now_playing", aliases=["NP", "Np", "np"])
    async def now_playing(self, ctx):
        if not self.song_queue:
            return await ctx.send("Nothing is playing rn")
        curr_song = self.song_queue[0]
        unicode_elapsed = round(
            20 * (curr_song["time_elapsed"] / curr_song["duration"])
        )
        minutes_elapsed = int(curr_song["time_elapsed"] / 60)
        minutes_total = int(curr_song["duration"] / 60)
        seconds_elapsed = curr_song["time_elapsed"] - (minutes_elapsed * 60)
        seconds_total = curr_song["duration"] - (minutes_total * 60)
        description = (
            f"{curr_song['title']}\n"
            + f"{'━'*unicode_elapsed}🔘{'┅'*(20-unicode_elapsed)}\n"
            + f"[{minutes_elapsed}:{seconds_elapsed}/"
            + f"{minutes_total}:{seconds_total}]"
        )
        return await ctx.send(
            embed=nextcord.Embed(
                title="Now Playing:",
                color=0xFF0000,
                description=description,
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
