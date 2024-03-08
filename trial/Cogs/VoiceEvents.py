import nextcord
from .VoiceBase import VoiceBase
import lavalink
import os

from trial.Utils.Helpers import Helpers


class VoiceEvents(VoiceBase):
    def __init__(self, bot):
        self.bot = bot
        bot.lavalink.add_event_hook(
            self.track_start,
            event=lavalink.events.TrackStartEvent,
        )
        bot.lavalink.add_event_hook(
            self.track_end,
            event=lavalink.events.TrackEndEvent,
        )
        bot.lavalink.add_event_hook(
            self.queue_end,
            event=lavalink.events.QueueEndEvent,
        )

    async def track_start(self, event):
        event.player.store("afk", False)
        if event.track.uri.startswith("./"):  # local file
            return
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
        except (nextcord.errors.NotFound, AttributeError):
            # message already deleted OR never sent (local files)
            try:
                os.remove(f"./{player.guild_id}.mp3")
            except FileNotFoundError:
                pass

        await Helpers.add_song(player)

    async def queue_end(self, event):
        pass


def setup(bot):
    bot.add_cog(VoiceEvents(bot))
