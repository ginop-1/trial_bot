import nextcord
from nextcord.ext import commands
import lavalink


class MusicEventsCog(commands.Cog):
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
        msg = await channel.send(embed=embed)
        event.player.store("message", msg)

    async def track_end(self, event):
        msg = event.player.fetch("message")
        if msg:
            await msg.delete()

    async def queue_end(self, event):
        pass
        # guild_id = int(event.player.guild_id)
        # guild = self.bot.get_guild(guild_id)
        # await guild.voice_client.disconnect(force=True)


def setup(bot):
    bot.add_cog(MusicEventsCog(bot))