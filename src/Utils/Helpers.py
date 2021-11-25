import nextcord
import yt_dlp


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
            "options": "-vn",
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
    def get_url_video(guild_id: int, url: str):
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
                return Helpers.buildSong(video_info, final_url)
            elif video_type == "playlist":
                final_url = f"./tmpsong/{guild_id}"
                return [
                    Helpers.buildSong(video, final_url)
                    for video in video_info["entries"]
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
    async def createbook(bot, ctx, title, pages, **kwargs):

        header = kwargs.get("header", "")  # String
        results = kwargs.get("results", 0)  # Int

        pagenum = 1

        def get_results():
            results_min = (pagenum - 1) * 8 + 1
            if pagenum == len(pages):
                results_max = results
            else:
                results_max = pagenum * 8
            return f"Showing {results_min} - {results_max} results out of {results}"

        pagemax = len(pages)
        if results:
            header = get_results()
            if len(pages) == 0:
                pagemax = 1

        embed = nextcord.Embed(
            title=title,
            description=f"{header}\n\n{pages[pagenum - 1]}",
            colour=0xF42F42,
        )
        embed.set_footer(text=f"Page {pagenum}/{pagemax}")
        msg = await ctx.send(embed=embed)

        await msg.add_reaction("⬅️")
        await msg.add_reaction("➡")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡"]

        while True:
            try:
                reaction, user = await bot.wait_for(
                    "reaction_add", timeout=60, check=check
                )
                await msg.remove_reaction(reaction, user)

                if str(reaction.emoji) == "⬅️":
                    pagenum -= 1
                    if pagenum < 1:
                        pagenum = len(pages)

                elif str(reaction.emoji) == "➡":
                    pagenum += 1
                    if pagenum > len(pages):
                        pagenum = 1

                header = get_results() if results else header
                if str(reaction.emoji) == "⬅️" or str(reaction.emoji) == "➡":
                    embed = nextcord.Embed(
                        title=title,
                        description=f"{header}\n\n{pages[pagenum - 1]}",
                        colour=0xF42F42,
                    )
                    embed.set_footer(text=f"Page {pagenum}/{len(pages)}")
                    await msg.edit(embed=embed)
            except:
                header = get_results() if results else header
                embed = nextcord.Embed(
                    title="FBot Server Status",
                    description=f"{header}\n\n{pages[pagenum - 1]}",
                    colour=0xF42F42,
                )
                embed.set_footer(text=f"Request timed out")
                await msg.edit(embed=embed)
                break

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
