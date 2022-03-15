from .VoiceBase import VoiceBaseCog
from trial.Utils.Helpers import Helpers
from trial.config import Config

from nextcord.ext import commands
import nextcord
from spotipy import SpotifyClientCredentials
import spotipy
import deezer

import random
import re


class PlayCog(VoiceBaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.yt_rx = re.compile(
            r"(https?\:\/\/)?(www\.youtube\.com|youtu\.be)\/.+"
        )
        # check if both spotify id and secret are not none
        if not None in (Config.SPOTIFY_ID, Config.SPOTIFY_SECRET):
            self.sp = spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials(
                    Config.SPOTIFY_ID, Config.SPOTIFY_SECRET
                )
            )
        else:
            self.sp = None
        self.deezer = deezer.Client()

    async def _parse_Youtube(self, query: str, player, ctx, opts) -> tuple:
        if not self.yt_rx.match(query):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)

        if not results["tracks"]:
            await ctx.send(embed=nextcord.Embed(title="No results found."))
            return None, None

        color = nextcord.Color.blurple()

        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]
            for track in tracks:
                player.add(track=track, requester=ctx.author.id)
            if opts in ("?shuffle", "?s"):
                random.shuffle(player.queue)
            return (
                nextcord.Embed(
                    color=color,
                    title="Playlist added to queue.",
                    description=f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks',
                ),
                None,
            )
        else:
            track = results["tracks"][0]
            player.add(track=track, requester=ctx.author.id)
            return (
                nextcord.Embed(
                    color=color,
                    title="Added to queue.",
                    description=f'[{track["info"]["title"]}]({track["info"]["uri"]})',
                ),
                30,
            )

    async def _parse_notYoutube(self, query: str, player, ctx, opts) -> tuple:
        if query.startswith("https://open.spotify.com/"):
            if self.sp is None:
                await ctx.send("Spotify is not configured.")
                return None, None
            pl = Helpers.get_Spotify_tracks(
                self.sp, query, ctx.author.id, bool(opts)
            )
        else:
            pl = Helpers.get_Deezer_tracks(
                self.deezer, query, ctx.author.id, bool(opts)
            )
        if not pl or not pl["tracks"]:
            await ctx.send(embed=nextcord.Embed(title="No results found."))
            return None, None
        for song in pl["tracks"]:
            if not player.queue and not player.is_playing and not player.paused:
                song = await Helpers.process_song(player, song)
                if song is None:
                    continue
            else:
                player.queue.append(song)
        return (
            nextcord.Embed(
                color=nextcord.Color.blurple(),
                description=f"**{pl['title']}** added to queue - {len(pl['tracks'])} songs.",
            ),
            None,
        )

    @commands.command(aliases=["p", "P", "Play"])
    async def play(self, ctx, *args):
        """Searches and plays a song from a given query."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if player is None:
            return await ctx.send("Sto testando il bot, al momento è offline")

        if not args:
            return await ctx.send("Please provide a search query.")

        if not args[0].startswith("?"):
            opts, query = None, " ".join(args)
        else:
            opts, query = args[0], " ".join(args[1:])

        query = query.strip("<>")
        if self.yt_rx.match(query) or not query.startswith("https://"):
            embed, self_destroy = await self._parse_Youtube(
                query, player, ctx, opts
            )
        else:
            embed, self_destroy = await self._parse_notYoutube(
                query, player, ctx, opts
            )

        if not player.is_playing and not player.paused:
            player.store("channel", ctx.channel.id)
            await player.play()

        if player.queue and embed:
            await ctx.send(embed=embed, delete_after=self_destroy)


def setup(bot):
    bot.add_cog(PlayCog(bot))
