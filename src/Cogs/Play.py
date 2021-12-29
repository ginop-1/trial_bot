from Cogs.MusicBase import MusicBaseCog
from Utils.Helpers import Helpers
from Utils.DB import DB

from nextcord.ext import commands
import nextcord
from spotipy import SpotifyClientCredentials
import spotipy
import deezer

import random
import re


class PlayCog(MusicBaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.yt_rx = re.compile(
            "(https?\:\/\/)?(www\.youtube\.com|youtu\.be)\/.+"
        )
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                DB.SPOTIFY_ID,
                DB.SPOTIFY_SECRET,
            ),
        )
        self.deezer = deezer.Client()

    async def _parse_Youtube(self, query: str, player, ctx, opts):
        if not self.yt_rx.match(query):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)

        if not results["tracks"]:
            return nextcord.Embed(title="No results found.")

        color = nextcord.Color.blurple()

        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]
            for track in tracks:
                player.add(track=track, requester=ctx.author.id)
            if opts in ("?shuffle", "?s"):
                random.shuffle(player.queue)
            return nextcord.Embed(
                color=color,
                title="Playlist added to queue.",
                description=f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks',
            )
        else:
            track = results["tracks"][0]
            player.add(track=track, requester=ctx.author.id)
            return nextcord.Embed(
                color=color,
                title="Added to queue.",
                description=f'[{track["info"]["title"]}]({track["info"]["uri"]})',
            )

    async def _parse_notYoutube(self, query: str, player, ctx, opts):
        if query.startswith("https://open.spotify.com/"):
            pl = Helpers.get_Spotify_tracks(
                self.sp, query, ctx.author.id, bool(opts)
            )
        else:
            pl = Helpers.get_Deezer_tracks(
                self.deezer, query, ctx.author.id, bool(opts)
            )
        if not pl or not pl["tracks"]:
            return nextcord.Embed(title="No results found.")
        for song in pl["tracks"]:
            if not player.queue and not player.is_playing and not player.paused:
                await Helpers.process_song(player, song, play=False)
            else:
                player.queue.append(song)
        return nextcord.Embed(
            color=nextcord.Color.blurple(),
            description=f"**{pl['title']}** added to queue - {len(pl['tracks'])} songs.",
        )

    @commands.command(aliases=["p", "P", "Play"])
    async def play(self, ctx, *args):
        """Searches and plays a song from a given query."""
        if self.bot.testing and str(ctx.guild.id) != DB.TEST_GUILD_ID:
            return await ctx.send("Sto testando il bot, al momento è offline")
        if not args:
            return await ctx.send("Please provide a search query.")

        if not args[0].startswith("?"):
            opts, query = None, " ".join(args)
        else:
            opts, query = args[0], " ".join(args[1:])

        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip("<>")

        if (
            query.startswith("https://www.youtube.com/")
            or not "https://" in query
        ):
            embed = await self._parse_Youtube(query, player, ctx, opts)
        else:
            embed = await self._parse_notYoutube(query, player, ctx, opts)

        if not player.is_playing and not player.paused:
            player.store("channel", ctx.channel.id)
            await player.play()

        if player.queue:
            await ctx.send(embed=embed, delete_after=30)


def setup(bot):
    bot.add_cog(PlayCog(bot))
