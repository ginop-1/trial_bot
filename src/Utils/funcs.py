import nextcord
import youtube_dl


class Functions:
    """
    It contains useful function to clean up code
    """

    def __init__(self) -> None:
        pass

    ydl_opts = {
        "format": "249/250/251",
        "logtostderr": False,
        "quiet": True,
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    def actual_voice_channel(bot):
        return nextcord.utils.get(bot.voice_clients)

    def get_url_video(video_info: dict):
        with youtube_dl.YoutubeDL(Functions.ydl_opts) as downloader:
            video_info = downloader.extract_info(
                f"{video_info['id']}", download=False
            )
        # print(video_info['formats'])
        return video_info["url"]

    def get_embed(title: str, index: int, song_queue: dict()):
        red_color = 0xFF0000
        # print(song_queue)
        embedvar = nextcord.Embed(
            title=title,
            description=f"[{song_queue[index]['title']}]"
            + f"({Functions.get_url_video(song_queue[index])})",
            color=red_color,
        )
        return embedvar

    async def join(bot, ctx):
        """
        Join in a voice channel
        """
        if Functions.actual_voice_channel(bot) is not None:
            return await ctx.send("Alread connected to a voice channel")
        channel = ctx.author.voice.channel
        return await channel.connect()
