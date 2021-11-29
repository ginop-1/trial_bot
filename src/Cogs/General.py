from Utils.Helpers import Helpers
from Utils.Storage import storage as stg
import random
import wikipedia_for_humans
import nextcord
from nextcord.ext import commands, tasks
from gtts import gTTS


class General(commands.Cog):
    """
    Contains general purpose commands
    """

    def __init__(self, bot):
        self.bot = bot
        # self.auto_leave_afk.start()

    # @tasks.loop(minutes=10)
    # async def auto_leave_afk(self):
    #     queue = self.bot.songs_queue
    #     for id in queue.keys():
    #         if queue[id]["afk"] is True:
    #             guild_obj = self.bot.get_guild(id)
    #             voice = nextcord.utils.get(
    #                 self.bot.voice_clients, guild=guild_obj
    #             )
    #             if voice is None:
    #                 queue[id]["afk"] = True
    #                 return
    #             elif voice.is_playing():
    #                 queue[id]["afk"] = False
    #                 return
    #             remove(f"./tmpsong/{id}")
    #             await voice.disconnect()
    #         else:
    #             queue[id]["afk"] = True

    @commands.command(name="ping")
    async def ping(self, ctx):
        """
        Debug: test bot connectivity
        """
        await ctx.send(f"Pong! bot latency is {int(self.bot.latency*1000)}ms")

    @commands.command(name="offendi")
    async def offend(self, ctx, *, words):
        """
        Shame the given person
        """
        # IDK why but using directly stg.offese[index] not works
        offese = stg.offese
        response = words + offese[random.randint(0, len(offese) - 1)]
        await ctx.send(response)
        # await Helpers.join(self.bot, ctx)
        # voice = Helpers.actual_voice_channel(self.bot)
        # tts = gTTS(response, lang="it")
        # tts.save("offend.mp3")
        # if not voice.is_playing():
        #     voice.play(
        #         nextcord.FFmpegPCMAudio(source="./offend.mp3"), after=None
        #     )

    @commands.command(name="wiki")
    async def wiki(self, ctx, *, words):
        """
        Search the given word / sentence on Wikipedia
        """

        async def _page_not_found(ctx):
            return await ctx.send("Page not found")

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

    # @commands.command(name="tts", aliases=["TTS", "Tts"])
    # async def tts(self, ctx, *, text):
    #     """
    #     Speak to voice channel, can also be used as gTTS setup template
    #     """
    #     tts = gTTS(text, lang="it")
    #     tts.save("speaking.mp3")
    #     voice = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)
    #     if voice is None:
    #         voice = await Helpers.join(self.bot, ctx)
    #     vc_connection = Helpers.vc_request(voice, ctx)
    #     if vc_connection != "safe":
    #         return await ctx.send(vc_connection)
    #     audio_source = nextcord.FFmpegPCMAudio(source="./speaking.mp3")
    #     try:
    #         if not voice.is_playing():
    #             voice.play(audio_source, after=None)
    #     except AttributeError as err:
    #         print("not in a voice channel")

    @commands.command(name="killall")
    async def killall(self, ctx):
        """
        Kick all the people in the voice channel (only works if you're gino)
        """
        if not ctx.author.voice:
            return await ctx.send("You need to be in a voice channel!")
        if ctx.message.author.id == stg.GINO_ID:
            users = ctx.message.author.voice.channel.members
            for user in users:
                await user.move_to(None, reason="Nibba")


def setup(bot: commands.Bot):
    bot.add_cog(General(bot))
