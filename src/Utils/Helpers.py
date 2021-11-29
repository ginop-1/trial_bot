import nextcord


class Queue_msg(nextcord.ui.View):
    def __init__(self, queue):
        super().__init__(timeout=60)
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

    @nextcord.ui.button(label="⏮")
    async def first(self, button, interaction):
        self.page_n = 0
        await self.activity(interaction)

    @nextcord.ui.button(label="◀")
    async def previous(self, button, interaction):
        if self.page_n > 0:
            self.page_n -= 1
        await self.activity(interaction)

    @nextcord.ui.button(label="▶")
    async def next(self, button, interaction):
        if self.page_n < self.max_page_n:
            self.page_n += 1
        await self.activity(interaction)

    @nextcord.ui.button(label="⏭")
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
    def get_pages(pages: list, start: int = 0, end: int = 10):
        queue_text = [
            f"{(str(n+start)+'.')}[{song['title']}]({song['uri']})"
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
