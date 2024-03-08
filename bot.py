from nextcord import Activity, ActivityType, Intents
from nextcord.ext import commands
import os, sys, logging
from trial.config import Config

Config.load()

# setup logging to file
logging.basicConfig(
    # filename="logs/bot.log",
    # filemode="a+",
    format="%(asctime)s:%(levelname)s:%(name)s -> %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.INFO,
)
# set lavalink logging level to WARNING
logging.getLogger("lavalink").setLevel(logging.WARNING)
# set nextcord logging level to WARNING
logging.getLogger("nextcord").setLevel(logging.WARNING)


def load_cogs(bot):
    bot.load_extension("trial.Cogs.VoiceBase")
    for f in os.listdir("./trial/Cogs"):
        if f.endswith(".py") and ("VoiceBase" not in f):
            bot.load_extension(f"trial.Cogs.{f[:-3]}")


intents = Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=Config.PREFIX,
    intents=intents,
)

bot._enable_debug_events = True
# testing mode is enabled by passing "test" as command line argument
bot.testing = len(sys.argv) > 1 and sys.argv[1] == "debug"

bot_activity = Activity(
    type=ActivityType.listening,
    name=f"{f'{Config.PREFIX}help' if not bot.testing else 'debug'}",
)


@bot.event
async def on_ready():
    with open("logs/guilds.txt", "w") as f:
        for guild in bot.guilds:
            f.write(f"{guild.id}-{guild.name}\n")
    load_cogs(bot)
    await bot.change_presence(
        status=bot.status,
        activity=bot_activity,
    )
    logging.info(f"{Config.PREFIX}start. Bot is ready")


# this check is needed because if the list is empty
# nextcord raise an exception
if Config.TEST_GUILD_IDS:

    @bot.slash_command(guild_ids=Config.TEST_GUILD_IDS)
    async def test_one(interaction):
        await interaction.response.send_message("TEST 1")

    @bot.slash_command(guild_ids=Config.TEST_GUILD_IDS)
    async def test_two(interaction, message):
        await interaction.response.send_message(f"{message}")


if __name__ == "__main__":
    bot.run(Config.TOKEN)
