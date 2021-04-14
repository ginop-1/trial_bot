# bot.py
import os
import random
import wikipedia_for_humans
import discord
from asyncio import sleep
from dotenv import load_dotenv
from gtts import gTTS
from discord.ext import commands

load_dotenv()
intents = discord.Intents.default()
intents.members = True

offese = [
    " ha bisogno di un nuovo buco del culo",
    " ha il cazzo storto",
    " non si lava da due anni",
    " piace essere picchiato con delle mazze chiodate",
    " vuole essere sodomizzato",
]

TOKEN = os.getenv('DISCORD_TOKEN')
GINO_ID = os.getenv('GINO')
bot = commands.Bot(command_prefix="asd ", intents=intents)


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
    voice_client: discord.VoiceClient = discord.utils.get(
        bot.voice_clients, guild=guild)
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
        if search != "":
            # tts = gTTS(search)
            # tts.save('yes.mp3')
            '''
            guild = ctx.guild
            voice_client: discord.VoiceClient = discord.utils.get(
                bot.voice_clients, guild=guild)
            audio_source = discord.FFmpegPCMAudio(source='./yes.mp3')
            try:
                if not voice_client.is_playing():
                    voice_client.play(audio_source, after=None)
            except AttributeError as err:
                print("not in a voice channel")
            '''
            await ctx.send(search)
        else:
            await ctx.send("Page not found")

# lollo_magie

# kick di tutti gli utenti in chat vocale


@bot.command(name='killall')
async def killall(ctx):
    print("aaaa")
    if ctx.author.voice:  # if the author is connected to a voice channel
        if ctx.message.author.id == int(GINO_ID):
            channel = ctx.message.author.voice.channel
            users = channel.members
            print(users)
            for user in users:
                await user.edit(voice_channel=None)
            # await ctx.send("Kicked all the members from the voice channel!")
    else:
        await ctx.send("You need to be in a voice channel!")
        return

bot.run(TOKEN)
