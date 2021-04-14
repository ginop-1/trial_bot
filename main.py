# bot.py
import os, random
import wikipedia_for_humans, discord
from asyncio import sleep
from dotenv import load_dotenv
# from gtts import gTTS
from discord.ext import commands

load_dotenv()

offese = [
    " ha bisogno di un nuovo buco del culo",
    " ha il cazzo storto",
    " non si lava da due anni",
    " piace essere picchiato con delle mazze chiodate",
    " vuole essere sodomizzato",
]

TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix="asd ", )


@bot.command(name="join")
async def join(ctx):
    channel = ctx.author.voice.channel
    connected = await channel.connect()
    connected.play(
        discord.FFmpegPCMAudio(
            source='./sounds/user-joined-your-channel.mp3'), )


@bot.command(name="leave")
async def leave(ctx):
    guild = ctx.guild
    voice_client: discord.VoiceClient = discord.utils.get(bot.voice_clients,
    guild=guild)
    audio_source = discord.FFmpegPCMAudio(
        source='./sounds/teamspeak_disconnect.mp3')
    if not voice_client.is_playing():
        voice_client.play(audio_source, after=None)
    while voice_client.is_playing():
        await sleep(1)
    await voice_client.disconnect()


@bot.command(name="offendi")
async def shame(ctx, args):
    await ctx.send(args + offese[random.randint(0, len(offese) - 1)])


@bot.command(name="wiki")
async def wiki(ctx, args):
    try:
        search = wikipedia_for_humans.summary(args)
    except:
        await ctx.send("Page not found")
        search = None
        return

    if search != None:
        # tts = gTTS(search)
        # tts.save('yes.mp3')
        await ctx.send(search)
        '''
        guild = ctx.guild
        voice_client: discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=guild)
        audio_source = discord.FFmpegPCMAudio(source='./yes.mp3')
        if not voice_client.is_playing():
            voice_client.play(audio_source, after=None)
        '''

#lollo_magie 
#kick di tutti gli utenti in chat vocale
@bot.command(name='clear')
async def cleal_all(ctx):
  



bot.run(TOKEN)
