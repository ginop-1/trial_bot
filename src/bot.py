import nextcord
from nextcord.ext import commands
import os
from Utils.Storage import storage as stg


def clear_songs_files():
    for f in os.listdir("./tmpsong"):
        os.remove("./tmpsong/" + f)


def load_cogs(bot):
    for f in os.listdir("./src/Cogs"):
        if f.endswith(".py"):
            bot.load_extension(f"Cogs.{f[:-3]}")


intents = nextcord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix="?",
    activity=nextcord.Activity(
        type=nextcord.ActivityType.listening, name="?help"
    ),
    intents=intents,
)

clear_songs_files()
load_cogs(bot)

if __name__ == "__main__":
    bot.run(stg.TOKEN)
