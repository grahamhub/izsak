import discord

import izsak
import os

from discord import (
    ui,
    Interaction,
)
from itertools import chain
from postgres import connection
from random import choice


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
        embed = discord.Embed()
        embed.title = kwargs.get("embed_title")

        author = kwargs.get("author")
        if author:
            embed.set_author(name=author)

        embed.set_image(url=kwargs.get("url"))
        embed.set_footer(
            text=kwargs.get("footer_text"),
            icon_url=kwargs.get("footer_icon_url"),
        )
        self.embed = embed


def get_random_by_category(category, filter_key=None, filter_val=None):
    item = None
    with connection() as postgres:
        items = postgres.get_all_by_category(category)
        if filter_key:
            items = filter_db_row(items, filter_key, filter_val)

        try:
            item = choice(items)
        except IndexError:
            pass

    return item


def upload_media(**kwargs):
    with connection() as postgres:
        postgres.insert(
            "mediaV2",
            list(kwargs.keys()),
            list(kwargs.values()),
        )


def media_has_been_sent(id):
    with connection() as postgres:
        postgres.update_field("mediaV2", "has_been_sent", True, id)


def get_by_id(id):
    item = None
    with connection() as postgres:
        item = postgres.get_by_id("mediaV2", id)

    return item


def can_upload(ctx):
    upload_users = os.environ.get("IZSAK_CAN_UPLOAD", "").split(",")
    upload_users = list(map(lambda id: int(id), upload_users))
    return ctx.user.id in upload_users


def filter_db_row(row, key, val=None):
    filtered_items = []
    for item in row:
        needle = item.get(key, False)
        if needle and needle == val:
            filtered_items.append(item)
        elif needle and not val:
            filtered_items.append(item)

    return filtered_items


def flatten(arr):
    return list(chain(*arr))


def migrate_media_v2():
    with connection() as postgres:
        media_v1 = postgres.get_all("media")
        keys = media_v1[0].keys()
        values = []
        categories = {}
        for item in media_v1:
            item_v2 = item
            cat = item.get("category")
            item_v2["category"] = [cat]
            name = item.get("submitted_by")
            can_upload = os.environ.get("IZSAK_CAN_DM").split(",")
            if name == "grotto":
                name = can_upload[0]
            else:
                name = can_upload[0]

            item_v2["submitted_by"] = name

            values.append(list(item_v2.values()))
            if cat not in categories.keys():
                categories[cat] = name

        print(f"Preparing mediav2 insert with {len(values)} rows...")
        postgres.insert(
            "mediaV2",
            keys,
            values,
        )
        print(f"Inserted!\nPreparing category insert with {len(categories)} rows...")

        postgres.insert(
            "category",
            [
                "name",
                "created_by",
            ],
            list(map(lambda x: [x, categories.get(x)], categories.keys())),
        )
        print("Done with migration!")
