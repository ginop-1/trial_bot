from Cogs.MusicBase import MusicBaseCog
from Utils.DB import DB

import nextcord
from nextcord.ext import commands
import lavalink
import lyricsgenius

import re


class PlayingCog(MusicBaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.genius = lyricsgenius.Genius(
            DB.GENIUS_TOKEN,
            verbose=False,
        )

    @commands.command(aliases=["resume"])
    async def pause(self, ctx):
        """Pauses/Resumes the current track."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("Not playing.")

        if player.paused:
            await player.set_pause(False)
            await ctx.message.add_reaction("▶")
        else:
            await player.set_pause(True)
            await ctx.message.add_reaction("⏸")

    @commands.command(aliases=["np", "n", "playing"])
    async def now(self, ctx):
        """Shows some stats about the currently playing song."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.current:
            return await ctx.send("Nothing playing.")

        s_elapsed = player.position // 1000
        s_total = player.current.duration // 1000
        n_emoji = round(20 * s_elapsed / s_total)

        position = lavalink.utils.format_time(player.position)
        if player.current.stream:
            duration = "🔴 LIVE"
        else:
            duration = lavalink.utils.format_time(player.current.duration)
        song = (
            f"**[{player.current.title}]({player.current.uri})**\n"
            + f"{'━'*n_emoji}🔘{'╶'*(20-n_emoji)}\n"
            + f"({position}/{duration})"
        )

        embed = nextcord.Embed(
            color=nextcord.Color.blurple(),
            title="Now Playing",
            description=song,
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["lyric"])
    async def lyrics(self, ctx):
        """
        Search for playing song's lyrics
        """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.current:
            return await ctx.send("Nothing playing.")
        remove_re = r"[\(\[].*?[\)\]]"
        title = re.sub(remove_re, "", player.current.title)
        song = self.genius.search_song(title)
        if song is None:
            return await ctx.send("Couldn't find any lyrics.")
        desc = re.sub(remove_re, "", song.lyrics)
        desc.replace("\n\n", "\n")
        desc = re.sub(r"\b[1-9]+.*$", "", desc)
        embed = nextcord.Embed(
            color=nextcord.Color.blurple(),
            title=f"{song.title} - {song.artist}",
            description=desc,
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["ff", "FF", "Ff", "fastforward"])
    async def fast_forward(self, ctx, *, seconds: int):
        """Jump to a current+seconds position in a track."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        track_time = player.position + (seconds * 1000)
        await player.seek(track_time)

        await ctx.send(
            f"FF track to **{lavalink.utils.format_time(track_time)}**"
        )

    @commands.command(aliases=["vol"])
    async def volume(self, ctx, volume):
        """Changes the player's volume (0-1000)."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        try:
            volume = int(volume)
        except:
            volume = int(volume[:-1])

        if not volume:
            return await ctx.send(f"🔈 | {player.volume}%")

        await player.set_volume(
            volume
        )  # Values are automatically capped between, or equal to 0-1000.
        await ctx.message.add_reaction("🔈")
        await ctx.send(f"Volume Set to {player.volume}%")

    @commands.command()
    async def find(self, ctx, *, query):
        """Lists the first 10 search results from a given query."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not query.startswith("ytsearch:") and not query.startswith(
            "scsearch:"
        ):
            query = "ytsearch:" + query

        results = await player.node.get_tracks(query)

        if not results or not results["tracks"]:
            return await ctx.send("Nothing found.")

        tracks = results["tracks"][:10]  # First 10 results

        o = ""
        for index, track in enumerate(tracks, start=1):
            track_title = track["info"]["title"]
            track_uri = track["info"]["uri"]
            o += f"`{index}.` [{track_title}]({track_uri})\n"

        embed = nextcord.Embed(color=nextcord.Color.blurple(), description=o)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(PlayingCog(bot))
