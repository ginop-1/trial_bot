from gtts import gTTS
from nextcord.ext import commands
from .VoiceBase import VoiceBaseCog


class VoiceCog(VoiceBaseCog):
    def __init__(self, bot) -> None:
        super().__init__(bot)

    @commands.command(name="join")
    async def join(self, ctx):
        """
        Join the voice channel
        """
        await ctx.message.add_reaction("👌🏽")

    @commands.command(aliases=["dc", "leave"])
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
        guild_id = int(player.guild_id)
        guild = self.bot.get_guild(guild_id)
        await guild.voice_client.disconnect(force=True)
        await ctx.message.add_reaction("👌🏽")

    @commands.command(name="tts", aliases=["say", "Tts", "TTS", "Say"])
    async def tts(self, ctx, *, words):
        """
        Make the bot say something
        """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        tts = gTTS(words, lang="it")
        tts.save("./offend.mp3")
        if player.is_playing:
            return await ctx.send(
                "I'm playing something, wait for it to finish"
            )
        audio_file = await player.node.get_tracks("./offend.mp3")
        audio_file = audio_file["tracks"][0]
        player.add(track=audio_file, requester=ctx.author.id)
        await player.play()


def setup(bot: commands.Bot):
    bot.add_cog(VoiceCog(bot))
