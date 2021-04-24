#!env/bin/python3

import os
import random
import wikipedia_for_humans
import discord
from asyncio import sleep
from dotenv import load_dotenv
from gtts import gTTS
from discord.ext import commands
import youtube_dl

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
bot = commands.Bot(command_prefix="__", intents=intents)


def _args_to_str(args):
    word = ""
    for arg in args:
        word = word + " " + arg
    return word


def _actual_voice_channel(ctx):
    return discord.utils.get(bot.voice_clients, guild=ctx.guild)


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
    voice_client = _actual_voice_channel(ctx)
    audio_source = discord.FFmpegPCMAudio(
        source='./sounds/teamspeak_disconnect.mp3')
    if not voice_client.is_playing():
        voice_client.play(audio_source, after=None)
    while voice_client.is_playing():
        await sleep(1)
    await voice_client.disconnect()


@bot.command(name="offendi")
async def shame(ctx, *argv):
    words = _args_to_str(argv)
    await ctx.send(words + offese[random.randint(0, len(offese) - 1)])


@bot.command(name="wiki")
async def wiki(ctx, *argv):
    words = _args_to_str(argv)
    try:
        search = str(wikipedia_for_humans.summary(words))
    except:
        await ctx.send("Page not found, error")
        search = None
        return

    if search is None:
        return

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
        search = search.splitlines()[0]
        if len(search) > 2000:
            search = search[:2000]
        return await ctx.send(search)

    return await ctx.send("Page not found")


@bot.command(name='killall')
async def killall(ctx):
    # if the author is connected to a voice channel
    if ctx.author.voice:
        if ctx.message.author.id == int(GINO_ID):
            channel = ctx.message.author.voice.channel
            users = channel.members
            # print(users)
            for user in users:
                await user.edit(voice_channel=None)
            # await ctx.send("Kicked all the members from the voice channel!")
    else:
        await ctx.send("You need to be in a voice channel!")
        return


@bot.command(name="play")
async def play(ctx, *argv):
    url = _args_to_str(argv)
    voice = _actual_voice_channel(ctx)

    # not connected to voice channel
    if voice is None:
        voiceChannel = ctx.author.voice.channel
        voice = await voiceChannel.connect()

    # is playing another song
    elif voice.is_playing():
        return await ctx.send(
            "Wait for the current playing music\
            to end or use the 'stop' command")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            # 'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(["ytsearch:"+url])
    for file in os.listdir("./"):
        if file.endswith(".opus"):
            os.rename(file, "song.mp3")
            break

    voice.play(discord.FFmpegPCMAudio("song.mp3"))


@bot.command(name="pause")
async def pause(ctx):
    voice = _actual_voice_channel(ctx)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")


@bot.command(name="resume")
async def resume(ctx):
    voice = _actual_voice_channel(ctx)
    if not voice.is_playing():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")


@bot.command(name="stop")
async def stop(ctx):
    voice = _actual_voice_channel(ctx)
    voice.stop()


bot.run(TOKEN)
