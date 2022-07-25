import os

from discord import (
    ui,
    Interaction,
)

import izsak
from postgres import connection
from random import choice


class UploadModal(ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(ui.InputText(label="URL"))
        self.add_item(ui.InputText(label="Artist"))
        self.add_item(ui.InputText(label="Category"))
        self.add_item(ui.InputText(label="NSFW"))

    async def callback(self, interaction: Interaction):
        await izsak.Izsak.upload(
            interaction,
            *map(lambda x: x.value, self.children)
        )


def get_random_by_category(category):
    item = None
    with connection() as postgres:
        items = postgres.get_all_by_attr("media", "category", category)
        item = choice(items)

    return item


def upload_media(**kwargs):
    with connection() as postgres:
        postgres.insert(
            "media",
            list(kwargs.keys()),
            list(kwargs.values()),
        )


def media_has_been_sent(id):
    with connection() as postgres:
        postgres.update_field("media", "has_been_sent", True, id)


def get_by_id(id):
    item = None
    with connection() as postgres:
        item = postgres.get_by_id("media", id)

    return item


def can_upload(ctx):
    upload_users = os.environ.get("IZSAK_CAN_UPLOAD", "").split(",")
    upload_users = list(map(lambda id: int(id), upload_users))
    return ctx.user.id in upload_users
