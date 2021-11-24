from nextcord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{'~'*20}\nBot is online\n{'~'*20}")


def setup(bot):
    bot.add_cog(Events(bot))
