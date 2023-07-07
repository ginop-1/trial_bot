from .VoiceBase import VoiceBase
from trial.Utils.Helpers import Helpers
from trial.config import Config

from nextcord.ext import commands
import nextcord
import spotipy, deezer, lyricsgenius
import lavalink

import random, re, logging

class Music(VoiceBase):
    def __init__(self, bot):
        self.bot = bot
        self.yt_rx = re.compile(
            r"(https?\:\/\/)?(www\.youtube\.com|youtu\.be)\/.+"
        )
        # check if both spotify id and secret are not none
        if not None in (Config.SPOTIFY_ID, Config.SPOTIFY_SECRET):
            self.sp = spotipy.Spotify(
                client_credentials_manager=spotipy.SpotifyClientCredentials(
                    Config.SPOTIFY_ID, Config.SPOTIFY_SECRET
                )
            )
        else:
            self.sp = None
        self.deezer = deezer.Client()
        if Config.GENIUS_TOKEN is not None:
            self.genius = lyricsgenius.Genius(
                Config.GENIUS_TOKEN, verbose=False
            )
        else:
            self.genius = None

    async def _parse_Youtube(self, query: str, player, ctx, opts) -> tuple:
        if not self.yt_rx.match(query):
            # return await ctx.send(
            # "Al momento le ricerche non vanno."
            # + "Usare il link diretto youtube. Fixerò appena possibile"
            # )
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
            return await ctx.send("Currently offline")

        if not args:
            return await ctx.send("Please provide a search query.")

        if not args[0].startswith("?"):
            opts, query = None, " ".join(args)
        else:
            opts, query = args[0], " ".join(args[1:])

        logging.info(f"Received query: {query} from guild {ctx.guild.name}")

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
        if self.genius is None:
            return await ctx.send(
                "Bot has not been configured to display lyrics."
            )
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
        desc = re.sub(r"[0-9]+Embed.*$", "", desc)
        embed = nextcord.Embed(
            color=nextcord.Color.blurple(),
            title=f"{song.title} - {song.artist}",
            description=desc[: Config.CHARS_LIMIT],
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
        # Stopping the player while it's paused will cause it to block (idk why). 
        await player.set_pause(False)
        
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

    @commands.command(aliases=["Clear"])
    async def clear(self, ctx):
        """Clears the player's queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send("Nothing queued.")

        player.queue.clear()
        await ctx.message.add_reaction("👌🏽")

def setup(bot):
    bot.add_cog(Music(bot))

