import nextcord
import yt_dlp


class Functions:
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
    def actual_voice_channel(bot):
        return nextcord.utils.get(bot.voice_clients)

    @staticmethod
    def download_audio(guild_id: int, video: dict):
        if video["duration"] > (20 * 60):
            return
        with yt_dlp.YoutubeDL(Functions.ydl_opts(guild_id)) as downloader:
            downloader.download([video["id"]])

    @staticmethod
    def buildSong(video: dict, final_url: str):
        return {
            "url": final_url,
            "id": video["id"],
            "title": video["title"],
            "duration": video["duration"],
            "time_elapsed": 0,
        }

    @staticmethod
    def get_url_video(guild_id: int, url: str):
        with yt_dlp.YoutubeDL(Functions.ydl_opts(guild_id)) as downloader:
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
            video_type = video_info["webpage_url_basename"]

            if video_type == "watch" or video_type == video_info["id"]:
                if video_info["duration"] / 60 > 20:
                    # too long, getting live url
                    final_url = video_info["url"]
                else:
                    final_url = f"./tmpsong/{guild_id}"
                return Functions.buildSong(video_info, final_url)
            elif video_type == "playlist":
                final_url = f"./tmpsong/{guild_id}"
                return [
                    Functions.buildSong(video, final_url)
                    for video in video_info["entries"]
                ]
            return False

    @staticmethod
    def get_embed(title: str, index: int, song_queue: dict):
        red_color = 0xFF0000
        # print(song_queue)
        embedvar = nextcord.Embed(
            title=title,
            description=f"[{song_queue[index]['title']}]"
            + f"(https://www.youtube.com/watch?v={song_queue[index]['id']})",
            color=red_color,
        )
        return embedvar

    @staticmethod
    async def join(bot, ctx, verbose=False):
        """
        Join in a voice channel
        """
        if Functions.actual_voice_channel(bot) is not None:
            if verbose:
                return await ctx.send("Alread connected to a voice channel")
            return
        channel = ctx.author.voice.channel
        return await channel.connect()
