from nextcord import Activity, ActivityType, Intents
from nextcord.ext import commands
import os
import sys
from trial.config import Config


def load_cogs(bot):
    for f in os.listdir("./trial/Cogs"):
        if f.endswith(".py"):
            bot.load_extension(f"trial.Cogs.{f[:-3]}")


intents = Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix=Config.PREFIX,
    intents=intents,
)

bot._enable_debug_events = True
# testing mode is enabled by passing "test" as command line argument
bot.testing = len(sys.argv) > 1 and sys.argv[1] == "test"

bot_activity = Activity(
    type=ActivityType.listening,
    name=f"{f'{Config.PREFIX}help' if not bot.testing else 'TESTING'}",
)


@bot.event
async def on_ready():
    load_cogs(bot)
    await bot.change_presence(
        status=bot.status,
        activity=bot_activity,
    )
    print(f"{Config.PREFIX}start. Bot is ready")


@bot.slash_command(guild_ids=Config.TEST_GUILD_IDS)
async def test_one(interaction):
    await interaction.response.send_message("TEST 1")


@bot.slash_command(guild_ids=Config.TEST_GUILD_IDS)
async def test_two(interaction, message):
    await interaction.response.send_message(f"{message}")


if __name__ == "__main__":
    bot.run(Config.TOKEN)
