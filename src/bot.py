from nextcord import Activity, ActivityType, Intents
from nextcord.ext import commands
import os
from Utils.DB import DB
import logging

logging.disable(logging.CRITICAL)


def load_cogs(bot):
    for f in os.listdir("./src/Cogs"):
        if f.endswith(".py"):
            bot.load_extension(f"Cogs.{f[:-3]}")


intents = Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix=DB.PREFIX,
    intents=intents,
)

bot._enable_debug_events = True


@bot.event
async def on_ready():
    load_cogs(bot)
    await bot.change_presence(
        status=bot.status,
        activity=Activity(type=ActivityType.listening, name=f"{DB.PREFIX}help"),
    )
    print(f"{DB.PREFIX}start. Bot is ready")


if __name__ == "__main__":
    bot.run(DB.TOKEN)
