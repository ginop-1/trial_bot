import lavalink
import logging

from nextcord.ext import commands
from nextcord.errors import ClientException
from trial.Utils.LavalinkVC import LavalinkVoiceClient
from trial.config import Config
from trial.Utils.Helpers import Helpers


class VoiceBase(commands.Cog):
    """Base of all Voice related Cogs."""

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(
            bot, "lavalink"
        ):  # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node(
                Config.LAVA_CREDENTIALS["host"],
                Config.LAVA_CREDENTIALS["port"],
                Config.LAVA_CREDENTIALS["password"],
                "eu",
                "default-node",
            )
            logging.info("Lavalink node connected.")

    def cog_unload(self):
        """Cog unload handler. This removes any event hooks that were registered."""
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """Command before-invoke handler."""
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        # checks if bot is in testing mode
        if self.bot.testing and ctx.guild.id not in Config.TEST_GUILD_IDS:
            return None

        if guild_check:
            Helpers.format_logs(self.qualified_name, ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.
            await self.ensure_voice(ctx)

        return guild_check

    async def ensure_voice(self, ctx):
        """This check ensures that the bot and command author are in the same voicechannel."""
        try:
            player = self.bot.lavalink.player_manager.create(
                ctx.guild.id, endpoint=str(ctx.guild.region)
            )
        except lavalink.exceptions.NodeException:
            raise commands.CommandInvokeError(
                "Lavalink node is not connected. Please try again later."
            )
        should_connect = ctx.command.name in ("play", "tts", "join")

        if not ctx.author.voice or not ctx.author.voice.channel:
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
            try:
                await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
            except ClientException:
                guild = self.bot.get_guild(ctx.author.guild.id)
                await guild.voice_client.connect(timeout=60, reconnect=True)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError("You need to be in my voicechannel.")

    async def cog_command_error(self, ctx, error):
        logging.info(f"ERROR IN {ctx.guild.name}: {error}")
        # disconnected from lavalink backend
        if str(error).startswith("Attempting a reconnect in"):
            exit(1)

    #   if isinstance(error, commands.CommandInvokeError):
    #     await ctx.send(error)
    #   The above handles errors thrown in this cog and shows them to the user.
    #   This shouldn't be a problem as the only errors thrown in this cog are from `ensure_voice`
    #   which contain a reason string, such as "Join a voicechannel" etc. You can modify the above
    #   if you want to do things differently.


def setup(bot):
    bot.add_cog(VoiceBase(bot))
