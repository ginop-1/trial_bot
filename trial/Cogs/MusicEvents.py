import nextcord
from .MusicBase import MusicBaseCog
import lavalink

from trial.Utils.Helpers import Helpers


class MusicEventsCog(MusicBaseCog):
    def __init__(self, bot):
        self.bot = bot
        lavalink.add_event_hook(
            self.track_start,
            event=lavalink.events.TrackStartEvent,
        )
        lavalink.add_event_hook(
            self.track_end,
            event=lavalink.events.TrackEndEvent,
        )
        lavalink.add_event_hook(
            self.queue_end,
            event=lavalink.events.QueueEndEvent,
        )

    async def track_start(self, event):
        event.player.afk = False
        embed = nextcord.Embed(
            title=f"Now playing",
            description=f"[{event.track.title}]({event.track.uri})",
        )
        requester = self.bot.get_user(int(event.track.requester))
        channel = self.bot.get_channel(event.player.fetch("channel"))
        embed.set_footer(text=f"Requested by {requester}")
        embed.color = nextcord.Color.blurple()
        msg = await channel.send(embed=embed)
        event.player.store("message", msg)

    async def track_end(self, event):
        player = event.player
        msg = player.fetch("message")
        try:
            await msg.delete()
        except nextcord.errors.NotFound:
            # message already deleted
            pass
        if player.queue and not isinstance(
            player.queue[0], lavalink.AudioTrack
        ):
            song = None
            while song is None:
                try:
                    song = player.queue.pop(0)
                    song = await Helpers.process_song(player, song)
                except IndexError as e:
                    pass

    async def queue_end(self, event):
        pass


def setup(bot):
    bot.add_cog(MusicEventsCog(bot))