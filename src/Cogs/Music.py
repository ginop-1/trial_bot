import nextcord
from nextcord.ext import commands
import asyncio
from Utils.Helpers import Helpers

# get the latest n items of a list
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}

    @commands.command(name="play", aliases=["P", "p"])
    async def play(self, ctx, *, url):
        """
        Play/search the given words/url from youtube
        """
        if ctx.author.voice is None:
            return await ctx.send("You are not in a voice channel")

        if ctx.guild.id not in self.song_queue.keys():
            self.song_queue[ctx.guild.id] = []

        local_queue = self.song_queue[ctx.guild.id]
        url = Helpers.get_url_video(guild_id=ctx.guild.id, url=url)
        if not url:
            # never gonna give u up
            return await ctx.send(
                embed=nextcord.Embed(
                    description=f"[💎 Free Clash Royale gems 💎]"
                    + f"(http://bitly.com/98K8eH)",
                )
            )
        wasEmpty = not bool(len(local_queue))

        if isinstance(url, list):
            local_queue = local_queue + url
        else:
            local_queue.append(url)

        await Helpers.join(self.bot, ctx)
        voice = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if not voice.is_playing() and wasEmpty:
            await self.start_songs_loop(ctx)
        else:
            await ctx.send(
                embed=Helpers.get_embed(local_queue[-1], "Added to queue"),
                delete_after=30,
            )

    async def start_songs_loop(self, ctx):
        local_queue = self.song_queue[ctx.guild.id]
        voice = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        while local_queue:
            Helpers.download_audio(guild_id=ctx.guild.id, video=local_queue[0])
            msg = await ctx.send(
                embed=Helpers.get_embed(local_queue[0], "Now playing")
            )
            voice.play(nextcord.FFmpegPCMAudio(source=local_queue[0]["url"]))
            while voice.is_playing():
                await asyncio.sleep(1)
                try:
                    local_queue[0]["time_elapsed"] += int(voice.is_playing())
                except IndexError as e:
                    return
            try:
                del local_queue[0]
            except IndexError as e:
                return
            await msg.delete()

    @commands.command(name="queue", aliases=["Q", "q"])
    async def queue(self, ctx):
        """
        Shows songs in queue
        """
        local_queue = self.song_queue[ctx.guild.id]
        if not local_queue:
            return await ctx.send(
                embed=nextcord.Embed(title="No songs in queue")
            )
        queue_list = [
            f"{i+1}\t- {video['title']}"
            if i
            else f"**Now Playing:** {video['title']}"
            for i, video in enumerate(local_queue)
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
        """
        Shows info about currently playing song
        """
        local_queue = self.song_queue[ctx.guild.id]
        if not local_queue:
            return await ctx.send("Nothing is playing rn")
        curr_song = local_queue[0]
        unicode_elapsed = round(
            20 * (curr_song["time_elapsed"] / curr_song["duration"])
        )
        minutes_elapsed = str(curr_song["time_elapsed"] // 60).zfill(2)
        minutes_total = str(curr_song["duration"] // 60).zfill(2)
        seconds_elapsed = str(
            curr_song["time_elapsed"] - (int(minutes_elapsed) * 60)
        ).zfill(2)
        seconds_total = str(
            curr_song["duration"] - (int(minutes_total) * 60)
        ).zfill(2)
        description = (
            f"{curr_song['title']}\n"
            + f"{'━'*unicode_elapsed}🔘{'╶'*(20-unicode_elapsed)}\n"
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
        """
        Skip the song
        """
        voice = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice is None:
            return print("not in a voice channel")
        if voice.is_playing():
            await ctx.message.add_reaction("⏭")
            voice.stop()

    @commands.command(name="pause")
    async def pause(self, ctx):
        """
        Pause the song
        """
        voice = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice is None:
            return print("not in a voice channel")
        if voice.is_playing():
            await ctx.message.add_reaction("⏸")
            voice.pause()
        else:
            await ctx.send("Currently no audio is playing.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        """
        Resume the song
        """
        voice = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice is None:
            return print("not in a voice channel")
        if not voice.is_playing():
            await ctx.message.add_reaction("▶️")
            return voice.resume()
        await ctx.send("The audio is not paused.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        """
        Stop the song
        """
        voice = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice is None:
            return print("not in a voice channel")
        local_queue = self.song_queue[ctx.guild.id]
        if not local_queue:
            return await ctx.send("Nothing is playing rn")
        del local_queue
        await ctx.message.add_reaction("🛑")
        voice.stop()


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))
