import nextcord
from nextcord.ext import commands
import os
from Utils.Storage import storage as stg

intents = nextcord.Intents.default()
intents.members = True


bot = commands.Bot(
    command_prefix="?",
    activity=nextcord.Activity(
        type=nextcord.ActivityType.listening, name="?help"
    ),
    intents=intents,
)

# load all Cogs
for filename in os.listdir("./src/Cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"Cogs.{filename[:-3]}")

# how to print all the commands
# [print(i) for i in bot.walk_commands()]
if __name__ == "__main__":
    bot.run(stg.TOKEN)
