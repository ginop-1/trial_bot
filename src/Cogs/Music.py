import re
import nextcord
import lavalink
from nextcord.ext import commands
from Utils.Helpers import Helpers
from Utils.Lavalink import LavalinkVoiceClient
from Utils.Storage import Storage as stg
import random
import lyricsgenius
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

yt_rx = re.compile("(https?\:\/\/)?(www\.youtube\.com|youtu\.be)\/.+")


class Music(commands.Cog):
    """Music Time"""

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(
            bot, "lavalink"
        ):  # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node(
                "localhost", 7000, "testing", "eu", "default-node"
            )  # Host, Port, Password, Region, Name
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                stg.SPOTIFY_ID, stg.SPOTIFY_SECRET
            ),
        )
        lavalink.add_event_hook(
            self.track_start,
            event=lavalink.events.TrackStartEvent,
        )
        lavalink.add_event_hook(
            self.track_end,
            event=lavalink.events.TrackEndEvent,
        )

    async def _parse_Spotify(self, query: str, player, ctx, opts):
        pl = Helpers.get_Spotify_tracks(self.sp, query, bool(opts))
        if not pl or not pl["tracks"]:
            return nextcord.Embed(title="No results found.")
        for song in pl["tracks"]:
            results = await player.node.get_tracks(song)
            track = results["tracks"][0]
            player.add(requester=ctx.author.id, track=track)
            if not player.is_playing:
                await player.play()
        return nextcord.Embed(
            description=f"**{pl['title']}** added to queue - {len(pl['tracks'])} songs."
        )

    async def _parse_Youtube(self, query: str, player, ctx, opts):
        if not yt_rx.match(query):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)

        if not results["tracks"]:
            return nextcord.Embed(title="No results found.")

        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]
            for track in tracks:
                player.add(track=track, requester=ctx.author.id)
            if opts == "?shuffle" or opts == "?s":
                random.shuffle(player.queue)
            return nextcord.Embed(
                title="Playlist added to queue.",
                description=f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks',
            )
        else:
            track = results["tracks"][0]
            player.add(track=track, requester=ctx.author.id)
            return nextcord.Embed(
                title="Added to queue.",
                description=f'[{track["info"]["title"]}]({track["info"]["uri"]})',
            )

    def cog_unload(self):
        """Cog unload handler. This removes any event hooks that were registered."""
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """Command before-invoke handler."""
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def ensure_voice(self, ctx):
        """This check ensures that the bot and command author are in the same voicechannel."""
        player = self.bot.lavalink.player_manager.create(
            ctx.guild.id, endpoint=str(ctx.guild.region)
        )
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        should_connect = ctx.command.name in ("play",)

        if not ctx.author.voice or not ctx.author.voice.channel:
            # Our cog_command_error handler catches this and sends it to the voicechannel.
            # Exceptions allow us to "short-circuit" command invocation via checks so the
            # execution state of the command goes no further.
            raise commands.CommandInvokeError("Join a voicechannel first.")

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError("Not connected.")

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if (
                not permissions.connect or not permissions.speak
            ):  # Check user limit too?
                raise commands.CommandInvokeError(
                    "I need the `CONNECT` and `SPEAK` permissions."
                )

            player.store("channel", ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError(
                    "You need to be in my voicechannel."
                )

    async def track_start(self, event):
        embed = nextcord.Embed(
            title=f"Now playing: {event.track.title}",
            description=f"[{event.track.title}]({event.track.uri})",
        )
        requester = self.bot.get_user(int(event.track.requester))
        channel = self.bot.get_channel(event.player.fetch("channel"))
        duration = event.track.duration // 1000 - 2
        embed.set_footer(text=f"Requested by {requester}")
        msg = await channel.send(embed=embed)
        event.player.store("message", msg)

    async def track_end(self, event):
        msg = event.player.fetch("message")
        await msg.delete()

    @commands.command(aliases=["p", "P", "Play"])
    async def play(self, ctx, *args):
        """Searches and plays a song from a given query."""
        if not args:
            return await ctx.send("Please provide a search query.")

        if not args[0].startswith("?"):
            opts, query = None, " ".join(args)
        else:
            opts, query = args[0], " ".join(args[1:])

        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip("<>")

        if query.startswith("https://open.spotify.com/"):
            embed = await self._parse_Spotify(query, player, ctx, opts)
        else:
            embed = await self._parse_Youtube(query, player, ctx, opts)

        if not player.is_playing and not player.paused:
            player.store("channel", ctx.channel.id)
            await player.play()

        if player.queue:
            await ctx.send(embed=embed, delete_after=30)

    @commands.command(aliases=["ff", "FF", "Ff", "fastforward"])
    async def fast_forward(self, ctx, *, seconds: int):
        """Jump to a current+seconds position in a track."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        track_time = player.position + (seconds * 1000)
        await player.seek(track_time)

        await ctx.send(
            f"FF track to **{lavalink.utils.format_time(track_time)}**"
        )

    @commands.command(aliases=["lyric"])
    async def lyrics(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.current:
            return await ctx.send("Nothing playing.")
        if not hasattr(self.bot.lavalink, "genius"):
            self.bot.lavalink.genius = lyricsgenius.Genius(
                stg.GENIUS_TOKEN, verbose=False
            )
        remove_re = r"[\(\[].*?[\)\]]"
        genius = self.bot.lavalink.genius
        title = re.sub(remove_re, "", player.current.title)
        song = genius.search_song(title)
        if song is None:
            return await ctx.send("Couldn't find any lyrics.")
        desc = re.sub(remove_re, "", song.lyrics)
        desc.replace("\n\n", "\n")
        embed = nextcord.Embed(
            color=nextcord.Color.blurple(),
            title=f"{song.title} - {song.artist}",
            description=desc,
        )
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
        except TypeError as e:
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

        if not player.is_playing:
            return await ctx.send("Not playing.")

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

    @commands.command(aliases=["q"])
    async def queue(self, ctx):
        """Shows the player's queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send("Nothing queued.")

        await Helpers.createbook(ctx, "Queue", player.queue)

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

    @commands.command()
    async def remove(self, ctx, index: int):
        """Removes an item from the player's queue with the given index."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send("Nothing queued.")

        if index > len(player.queue) or index < 1:
            return await ctx.send(
                f"Index has to be **between** 1 and {len(player.queue)}"
            )

        removed = player.queue.pop(index - 1)  # Account for 0-index.

        await ctx.send(f"Removed **{removed.title}** from the queue.")

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

    @commands.command(aliases=["dc"])
    async def disconnect(self, ctx):
        """Disconnects the player from the voice channel and clears its queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send("Not connected.")

        if not ctx.author.voice or (
            player.is_connected
            and ctx.author.voice.channel.id != int(player.channel_id)
        ):
            return await ctx.send("You're not in my voice channel!")

        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        await ctx.send("*⃣ | Disconnected.")

    # async def cog_command_error(self, ctx, error):
    #     if isinstance(error, commands.CommandInvokeError):
    #         pass
    #         # await ctx.send(error.original)
    #         # The above handles errors thrown in this cog and shows them to the user.
    #         # This shouldn't be a problem as the only errors thrown in this cog are from `ensure_voice`
    #         # which contain a reason string, such as "Join a voicechannel" etc. You can modify the above
    #         # if you want to do things differently.


def setup(bot):
    """Initialize music module"""
    bot.add_cog(Music(bot))
