import izsak
from discord import (
    Embed,
    ui,
    Interaction,
)
from utils import filter_embed_url


class UploadModal(ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(ui.InputText(
            label="URL",
            placeholder="https://google.com",
        ))
        self.add_item(ui.InputText(
            label="Artist",
            placeholder="Catgirl Supremacist",
        ))
        self.add_item(ui.InputText(
            label="Category",
            placeholder="catgirl,video,jerma"
        ))
        self.add_item(ui.InputText(
            label="NSFW",
            placeholder="False",
        ))

    async def callback(self, interaction: Interaction):
        await izsak.Izsak.upload(
            interaction,
            *map(lambda x: x.value, self.children)
        )


class ResponseEmbed:
    def __init__(self, **kwargs):
        embed = Embed()
        embed.title = kwargs.get("embed_title")

        url, avatar = filter_embed_url(kwargs.get("url"))
        author = kwargs.get("author")
        if author:
            embed.set_author(name=author, url=kwargs.get("url"))

        if avatar and "http" in avatar:
            embed.set_author(name=author, url=kwargs.get("url"), icon_url=avatar)

        embed.set_image(url=url)
        embed.set_footer(
            text=kwargs.get("footer_text"),
            icon_url=kwargs.get("footer_icon_url"),
        )
        self.embed = embed