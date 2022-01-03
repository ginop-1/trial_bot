import nextcord
import random
from spotipy import SpotifyException


class Queue_msg(nextcord.ui.View):
    def __init__(self, queue):
        super().__init__(timeout=60 * 10)
        self.pages = queue
        self.page_n = 0
        self.max_page_n = len(self.pages) // 10

    async def interaction_check(self, interaction):
        id = interaction.data["custom_id"]
        if id == "first":
            self.page_n = 0
        elif id == "previous" and self.page_n > 0:
            self.page_n -= 1
        elif id == "next" and self.page_n < self.max_page_n:
            self.page_n += 1
        elif id == "last":
            self.page_n = self.max_page_n
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
        return True

    @nextcord.ui.button(custom_id="first", emoji="first:877152666113949736")
    async def first(self, button, interaction):
        pass

    @nextcord.ui.button(
        custom_id="previous", emoji="previous:877152666046832670"
    )
    async def previous(self, button, interaction):
        pass

    @nextcord.ui.button(custom_id="next", emoji="next:877152666080387122")
    async def next(self, button, interaction):
        pass

    @nextcord.ui.button(custom_id="last", emoji="last:877152666009092126")
    async def last(self, button, interaction):
        pass


class Helpers:
    """
    It contains useful function to clean up code
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_pages(pages: list, start: int = 0, end: int = 10):
        queue_text = [
            # f"{(str(n+start+1)+'.')}[{song['title']}]({song['uri']})"
            f"{str(n+start+1)}.{song['title']}"
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
    async def process_song(player, song):
        results = await player.node.get_tracks(f"ytsearch:{song['title']}")
        if not results["tracks"]:
            return None
        track = results["tracks"][0]
        player.add(requester=song["requester"], track=track, index=0)
        return True

    @staticmethod
    def get_Spotify_tracks(sp_client, url, requester, shuffle=False):
        try:
            if "/playlist/" in url:
                result = sp_client.playlist(url)
            elif "/track/" in url:
                result = sp_client.track(url)
            elif "/album/" in url:
                result = sp_client.album(url)
        except SpotifyException:
            return None
        pl_name = result["name"]
        res_type = result["type"]
        if res_type in ("album", "playlist"):
            result = result["tracks"]
            song_list = result["items"]
            while result["next"]:
                result = sp_client.next(result)
                song_list.extend(result["items"])
            if shuffle:
                random.shuffle(song_list)
        else:
            song_list = [result]
        return {
            "title": pl_name,
            "tracks": [
                {
                    "title": f"{song['track']['name']}"
                    + f" - {song['track']['artists'][0]['name']}",
                    "requester": requester,
                }
                if res_type in ("playlist")
                else {
                    "title": f"{song['name']}"
                    + f" - {song['artists'][0]['name']}",
                    "requester": requester,
                }
                for song in song_list
            ],
        }

    @staticmethod
    def get_Deezer_tracks(dz_client, url, requester, shuffle=False):
        id = url.split("/")[-1]
        try:
            if "/playlist/" in url:
                pl = dz_client.get_playlist(id)
            # elif "/track/" in url:
            # pl = dz_client.track(url)
            elif "/album/" in url:
                pl = dz_client.get_album(id)
        except Exception:
            return None
        if shuffle:
            random.shuffle(pl.tracks)
        return {
            "title": pl.title,
            "tracks": [
                {
                    "title": f"{song.title} - {song.artist.name}",
                    "requester": requester,
                }
                for song in pl.tracks
            ],
        }
