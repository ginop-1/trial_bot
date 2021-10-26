from Utils.funcs import Functions as funcs
from Utils.storage import storage as stg
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

    @commands.command(name="ping")
    async def ping(self, ctx, *argv):
        await ctx.send(f"Pong! bot latency is {int(self.bot.latency*1000)}ms")

    @commands.command(name="offendi")
    async def offend(self, ctx, *argv):
        words = " ".join(argv)
        # IDK why but using directly stg.offese[index] not works
        offese = stg.offese
        response = words + offese[random.randint(0, len(offese) - 1)]
        await ctx.send(response)
        await funcs.join(self.bot, ctx)
        voice = funcs.actual_voice_channel(self.bot)
        tts = gTTS(response, lang="it")
        tts.save("offend.mp3")
        if not voice.is_playing():
            voice.play(
                nextcord.FFmpegPCMAudio(source="./offend.mp3"), after=None
            )

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
            # discord 2000 chars limit
            search = search[: stg.CHARS_LIMITS]
        return await ctx.send(search)

    @commands.command(name="tts", aliases=["TTS", "Tts"])
    async def tts(self, ctx, *argv):
        """
        Speak to voice channel, can also be used as gTTS setup template
        """
        text = " ".join(argv)
        tts = gTTS(text, lang="it")
        tts.save("speaking.mp3")
        await funcs.join(self.bot, ctx)
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
