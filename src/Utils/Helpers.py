import nextcord
import yt_dlp


class Queue_msg(nextcord.ui.View):
    def __init__(self, queue):
        super().__init__(timeout=60 * 10)
        self.pages = queue
        self.page_n = 0
        self.max_page_n = len(self.pages) // 10

    async def activity(self, interaction):
        msg = interaction.message
        embed = nextcord.Embed(
            title="Queue",
            description=Helpers.get_pages(
                self.pages, self.page_n * 10, (self.page_n + 1) * 10
            ),
            colour=0xF42F42,
        )
        embed.set_footer(text=f"Page {self.page_n+1}/{self.max_page_n+1}")
        await msg.edit(embed=embed)

    @nextcord.ui.button(label="⏮", custom_id="0")
    async def first(self, button, interaction):
        self.page_n = 0
        await self.activity(interaction)

    @nextcord.ui.button(label="◀", custom_id="1")
    async def previous(self, button, interaction):
        if self.page_n > 0:
            self.page_n -= 1
        await self.activity(interaction)

    @nextcord.ui.button(label="▶", custom_id="2")
    async def next(self, button, interaction):
        if self.page_n < self.max_page_n:
            self.page_n += 1
        await self.activity(interaction)

    @nextcord.ui.button(label="⏭", custom_id="3")
    async def last(self, button, interaction):
        self.page_n = self.max_page_n
        await self.activity(interaction)


class Helpers:
    """
    It contains useful function to clean up code
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def ydl_opts(id: int):
        return {
            "extract_flat": True,
            "format": "249/250/251",
            "outtmpl": f"./tmpsong/{id}",
            "overwrites": True,
            "logtostderr": True,
            "quiet": False,
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        }

    @staticmethod
    def download_audio(guild_id: int, video: dict):
        if video["duration"] > (20 * 60):
            return
        with yt_dlp.YoutubeDL(Helpers.ydl_opts(guild_id)) as downloader:
            downloader.download([video["id"]])

    @staticmethod
    def buildSong(video: dict, final_url: str):
        return {
            "url": final_url,
            "id": video["id"],
            "title": video["title"],
            "duration": int(video["duration"]),
            "time_elapsed": 0,
        }

    @staticmethod
    def get_url_video(guild_id: int, url: str) -> list:
        with yt_dlp.YoutubeDL(Helpers.ydl_opts(guild_id)) as downloader:
            try:
                video_info = downloader.extract_info(url, download=False)
            except yt_dlp.DownloadError as e:
                # not valid url (ex: Despacito)
                video_info = downloader.extract_info(
                    f"ytsearch:{url}", download=False
                )["entries"][0]
                video_info = downloader.extract_info(
                    video_info["url"], download=False
                )
            except IndexError as e:
                return False
            video_type = video_info["webpage_url_basename"]

            if video_type == "watch" or video_type == video_info["id"]:
                if video_info["duration"] / 60 > 20:
                    # too long, getting live url
                    final_url = video_info["url"]
                else:
                    final_url = f"./tmpsong/{guild_id}"
                return [Helpers.buildSong(video_info, final_url)]
            elif video_type == "playlist":
                final_url = f"./tmpsong/{guild_id}"
                return [
                    Helpers.buildSong(video, final_url)
                    for video in video_info["entries"]
                    # deleted video
                    if video["duration"] is not None
                ]
            return False

    @staticmethod
    def get_embed(song: dict, title: str):
        red_color = 0xFF0000
        embedvar = nextcord.Embed(
            title=title,
            description=f"[{song['title']}]"
            + f"(https://www.youtube.com/watch?v={song['id']})",
            color=red_color,
        )
        return embedvar

    @staticmethod
    def get_pages(pages: list, start: int = 0, end: int = 10):
        queue_text = [
            f"{(str(n+start)+'.')}[{song['title']}](https://www.youtube.com/watch?v={song['id']})"
            for n, song in enumerate(pages[start:end])
        ]
        return "\n".join(queue_text)

    @staticmethod
    async def createbook(ctx, title, pages):

        embed = nextcord.Embed(
            title=title,
            description=Helpers.get_pages(pages, 0, 10),
            colour=0xF42F42,
        )

        embed.set_footer(text=f"Page 1/{len(pages) // 10+1}")
        components = Queue_msg(queue=pages)
        await ctx.send(embed=embed, view=components)

    @staticmethod
    async def join(bot, ctx, verbose=False):
        """
        Join in a voice channel
        """
        if nextcord.utils.get(bot.voice_clients, guild=ctx.guild) is not None:
            if verbose:
                return await ctx.send("Alread connected to a voice channel")
            return
        channel = ctx.author.voice.channel
        return await channel.connect()

    @staticmethod
    def vc_request(voice, ctx, already_conn=True):
        """
        Check if user is connected to a voice channel and
        if it's the same as the bot's one
        """
        if voice is None and already_conn is True:
            return "I'm not in a voice channel"
        if ctx.author.voice is None:
            return "You are not in a voice channel"
        author_vc_id = ctx.author.voice.channel.id
        if voice is not None and author_vc_id != voice.channel.id:
            return "I'm in another voice channel!"

        return "safe"

    def voice_activity(func):
        """
        Reset afk timeout if a voice activity is detected
        """

        # def wrapper(*args, **kwargs):
        #     bot = args[0].bot
        #     ctx = args[1]
        #     bot.afk[ctx.guild.id] = False
        #     func(*args, **kwargs)

        # return wrapper
