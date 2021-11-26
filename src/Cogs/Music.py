import nextcord
from nextcord.ext import commands
import asyncio
from Utils.Helpers import Helpers


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="play", aliases=["P", "p"])
    async def play(self, ctx, *, url):
        """
        Play/search the given words/url from youtube
        """

        voice = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        vc_connection = Helpers.vc_request(voice, ctx, already_conn=False)
        if vc_connection != "safe":
            return await ctx.send(vc_connection)

        loading_msg = await ctx.send("Loading...")

        if ctx.guild.id not in self.bot.songs_queue.keys():
            self.bot.songs_queue[ctx.guild.id] = {
                "songs_list": [],
                "loop": False,
                "pause": False,
                "afk": False,
            }

        local_queue = self.bot.songs_queue[ctx.guild.id]["songs_list"]
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

        local_queue.extend(url)

        if voice is None:
            voice = await Helpers.join(self.bot, ctx)
        await loading_msg.delete()

        if not voice.is_playing() and wasEmpty:
            await self.start_songs_loop(ctx)
        else:
            await ctx.send(
                embed=Helpers.get_embed(local_queue[-1], "Added to queue"),
                delete_after=30,
            )

    async def start_songs_loop(self, ctx):
        local_queue = self.bot.songs_queue[ctx.guild.id]["songs_list"]
        voice = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        while local_queue:
            self.bot.songs_queue[ctx.guild.id]["afk"] = False
            Helpers.download_audio(guild_id=ctx.guild.id, video=local_queue[0])
            msg = await ctx.send(
                embed=Helpers.get_embed(local_queue[0], "Now playing")
            )
            voice.play(nextcord.FFmpegPCMAudio(source=local_queue[0]["url"]))
            while (
                voice.is_playing()
                or self.bot.songs_queue[ctx.guild.id]["pause"]
            ):
                await asyncio.sleep(1)
                if local_queue:
                    # don't add times if the song is paused
                    local_queue[0]["time_elapsed"] += int(voice.is_playing())
                else:
                    return
            if local_queue:
                local_queue.pop(0)
            await msg.delete()

    @commands.command(name="queue", aliases=["Q", "q"])
    async def queue(self, ctx):
        """
        Shows songs in queue
        """
        local_queue = self.bot.songs_queue[ctx.guild.id]["songs_list"]
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
        local_queue = self.bot.songs_queue[ctx.guild.id]["songs_list"]
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
        vc_connection = Helpers.vc_request(voice, ctx)
        if vc_connection != "safe":
            return await ctx.send(vc_connection)
        if voice.is_playing():
            await ctx.message.add_reaction("⏭")
            voice.stop()

    @commands.command(name="pause")
    async def pause(self, ctx):
        """
        Pause the song
        """
        voice = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        vc_connection = Helpers.vc_request(voice, ctx)
        if vc_connection != "safe":
            return await ctx.send(vc_connection)
        if voice.is_playing():
            self.bot.songs_queue[ctx.guild.id]["pause"] = True
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
        vc_connection = Helpers.vc_request(voice, ctx)
        if vc_connection != "safe":
            return await ctx.send(vc_connection)
        if not voice.is_playing():
            self.bot.songs_queue[ctx.guild.id]["pause"] = False
            await ctx.message.add_reaction("▶️")
            return voice.resume()
        await ctx.send("The audio is not paused.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        """
        Stop the song
        """
        voice = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        vc_connection = Helpers.vc_request(voice, ctx)
        if vc_connection != "safe":
            return await ctx.send(vc_connection)
        local_queue = self.bot.songs_queue[ctx.guild.id]["songs_list"]
        if not local_queue:
            return await ctx.send("Nothing is playing rn")
        local_queue.clear()
        await ctx.message.add_reaction("🛑")
        voice.stop()


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))
