from Utils.funcs import Functions as funcs
from Utils.storage import storage as stg
import asyncio
import random
import wikipedia_for_humans
import nextcord
from nextcord.ext import commands, tasks
from gtts import gTTS


class General(commands.Cog):
    """
    Contains all commands
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.auto_leave_afk.start()

    @tasks.loop(minutes=5)
    async def auto_leave_afk(self):
        voice = funcs.actual_voice_channel(self.bot)
        if not voice:
            return
        if not voice.is_playing():
            await voice.disconnect()

    @commands.command(name="join")
    async def join(self, ctx):
        """
        Join in a voice channel
        """
        if funcs.actual_voice_channel(self.bot) is not None:
            return await ctx.send("Alread connected to a voice channel")
        channel = ctx.author.voice.channel
        connected = await channel.connect()
        connected.play(
            nextcord.FFmpegPCMAudio(
                source="./sounds/user-joined-your-channel.mp3"
            ),
        )

    @commands.command(name="leave")
    async def leave(self, ctx):
        voice = funcs.actual_voice_channel(self.bot)
        if voice is None:
            return
        audio_source = nextcord.FFmpegPCMAudio(
            source="./sounds/teamspeak_disconnect.mp3"
        )
        if not voice.is_playing():
            voice.play(audio_source, after=None)
        while voice.is_playing():
            await asyncio.sleep(1)
        await voice.disconnect()

    @commands.command(name="offendi")
    async def offend(self, ctx, *argv):
        words = " ".join(argv)
        # IDK why but using directly stg.offese[index] not works
        offese = stg.offese
        response = words + offese[random.randint(0, len(offese) - 1)]
        await ctx.send(response)
        voice = funcs.actual_voice_channel(self.bot)
        if voice is None:
            channel = ctx.author.voice.channel
            voice = await channel.connect()
        tts = gTTS(response, lang="it")
        tts.save("yes.mp3")
        if not voice.is_playing():
            voice.play(nextcord.FFmpegPCMAudio(source="./yes.mp3"), after=None)

    @commands.command(name="wiki")
    async def wiki(self, ctx, *argv):
        async def _page_not_found(ctx):
            return await ctx.send("Page not found")

        words = " ".join(argv)
        try:
            search = str(wikipedia_for_humans.summary(words))
            title = str(wikipedia_for_humans._get_title(words))
        except Exception as e:
            return await _page_not_found(ctx)

        if search == "" or search is None:
            return await _page_not_found(ctx)

        search = f"**{title}**:\n" + search.splitlines()[0]
        if len(search) >= stg.CHARS_LIMIT:
            # discord 2000 char limit
            search = search[: stg.CHARS_LIMITS]
        return await ctx.send(search)

    @commands.command(name="tts")
    async def tts(self, ctx, *argv):
        """
        Speak to voice channel, can also be used as gTTs setup template
        """
        text = " ".join(argv)
        tts = gTTS(text, lang="it")
        tts.save("speaking.mp3")
        voice = funcs.actual_voice_channel(self.bot)
        audio_source = nextcord.FFmpegPCMAudio(source="./speaking.mp3")
        try:
            if not voice.is_playing():
                voice.play(audio_source, after=None)
        except AttributeError as err:
            print("not in a voice channel")

    @commands.command(name="killall")
    async def killall(self, ctx):
        # if the author is connected to a voice channel
        if not ctx.author.voice:
            return await ctx.send("You need to be in a voice channel!")
        if ctx.message.author.id == stg.GINO_ID:
            users = ctx.message.author.voice.channel.members
            for user in users:
                await user.move_to(None, reason="Nibba")


def setup(bot: commands.Bot):
    bot.add_cog(General(bot))
