from .VoiceBase import VoiceBaseCog
from trial.Utils.Helpers import Helpers
from lavalink import AudioTrack

from nextcord.ext import commands
import random


class QueueCog(VoiceBaseCog):
    @commands.command()
    async def move(self, ctx, source, dest):
        """Move a track in the queue."""

        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send("Nothing in queue.")

        if source == "first":
            source = 1
        elif source == "last":
            source = len(player.queue)
        if dest == "first":
            dest = 1
        elif dest == "last":
            dest = len(player.queue)

        try:
            source = int(source) - 1
            dest = int(dest) - 1
        except (TypeError, ValueError) as e:
            return await ctx.send("Please provide valid indexes")

        try:
            player.queue[source], player.queue[dest] = (
                player.queue[dest],
                player.queue[source],
            )
        except ValueError:
            return await ctx.send("Invalid positions.")

        await ctx.message.add_reaction("👌🏽")

    @commands.command(aliases=["forceskip"])
    async def skip(self, ctx):
        """Skips the current track."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        # await ctx.send("ok")

        if not player.is_playing:
            return await ctx.send("Not playing.")

        await Helpers.add_song(player)

        await player.skip()
        await ctx.message.add_reaction("⏭")

    @commands.command(aliases=["Stop", "STOP"])
    async def stop(self, ctx):
        """Stops the player and clears its queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("Not playing.")

        player.queue.clear()
        await player.stop()
        await ctx.message.add_reaction("🛑")

    @commands.command(aliases=["q"])
    async def queue(self, ctx):
        """Shows the player's queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send("Nothing queued.")

        await Helpers.createbook(ctx, "Queue", player.queue)

    @commands.command()
    async def shuffle(self, ctx):
        """Shuffles the player's queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("Nothing playing.")

        random.shuffle(player.queue)
        await ctx.message.add_reaction("🔀")

    @commands.command(aliases=["loop", "l"])
    async def repeat(self, ctx):
        """Repeats the current song until the command is invoked again."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("Nothing playing.")

        player.repeat = not player.repeat
        await ctx.message.add_reaction("🔁")
        await ctx.send("Repeat " + ("enabled" if player.repeat else "disabled"))

    @commands.command(aliases=["rm"])
    async def remove(self, ctx, index):
        """Removes an item from the player's queue with the given index."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send("Nothing queued.")

        if index == "first":
            index = 1
        elif index == "last":
            index = len(player.queue)

        if index > len(player.queue) or index < 1:
            return await ctx.send(
                f"Index has to be **between** 1 and {len(player.queue)}"
            )

        removed = player.queue.pop(index - 1)

        await ctx.send(f"Removed **{removed['title']}** from the queue.")


def setup(bot):
    bot.add_cog(QueueCog(bot))
