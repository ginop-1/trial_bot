from trial.config import Config
import random
import wikipedia_for_humans
from nextcord.ext import commands, tasks
from trial.Utils.Helpers import Helpers


class General(commands.Cog):
    """
    Contains general purpose commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.auto_leave_afk.start()

    async def cog_before_invoke(self, ctx):
        Helpers.format_logs(self.qualified_name, ctx)

    @tasks.loop(minutes=10)
    async def auto_leave_afk(self):
        """
        Automatically leaves if the bot is AFK
        """
        pl_manager = self.bot.lavalink.player_manager
        players = pl_manager.players
        if not players:
            return
        for guild_id, player in players.copy().items():
            if not player.is_connected:
                pl_manager.remove(guild_id)
            elif player.is_playing or player.paused:
                player.store("afk", False)
            elif player.fetch("afk"):
                guild = self.bot.get_guild(guild_id)
                await guild.voice_client.disconnect(force=False)
                pl_manager.remove(guild_id)
            else:
                player.store("afk", True)

    @commands.command(name="ping")
    async def ping(self, ctx):
        """
        Debug: test bot connectivity
        """
        await ctx.send(f"Pong! bot latency is {int(self.bot.latency*1000)}ms")

    @commands.command(name="offendi")
    async def offend(self, ctx, *, words):
        """
        Shame the given person
        """
        if not Config.INSULTS:
            return await ctx.send("Insults are disabled")

        response = words + Config.INSULTS[random.randint(0, len(Config.INSULTS) - 1)]
        await ctx.send(response)

    @commands.command(name="wiki")
    async def wiki(self, ctx, *, words):
        """
        Search the given word / sentence on Wikipedia
        """

        async def _page_not_found(ctx):
            return await ctx.send("Page not found")

        try:
            search = str(wikipedia_for_humans.summary(words))
            title = str(wikipedia_for_humans._get_title(words))
        except Exception:
            return await _page_not_found(ctx)

        if search in ("", None):
            return await _page_not_found(ctx)

        search = f"**{title}**:\n" + search.splitlines()[0]
        if len(search) >= Config.CHARS_LIMIT:
            # discord 2000 chars limit
            search = search[: Config.CHARS_LIMITS]
        return await ctx.send(search)

    @commands.command(name="killall")
    async def killall(self, ctx):
        """
        Kick all the people in the voice channel
        Only works if you're guild owner or your id is
        in the configuraton file
        """
        if not ctx.author.voice:
            return await ctx.send("You need to be in a voice channel!")
        if (
            ctx.message.author.id == Config.OWNER_ID
            or ctx.message.author == ctx.guild.owner
        ):
            users = ctx.message.author.voice.channel.members
            for user in users:
                await user.move_to(None, reason="GUEEE")
        else:
            return await ctx.send("Only server owner can use this command")


def setup(bot: commands.Bot):
    bot.add_cog(General(bot))
