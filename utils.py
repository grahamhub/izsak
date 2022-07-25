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


def get_random_by_category(category, filter_key=None, filter_val=None):
    item = None
    with connection() as postgres:
        items = postgres.get_all_by_attr("media", "category", category)
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


def filter_db_row(row, key, val=None):
    filtered_items = []
    for item in row:
        needle = item.get(key, False)
        if needle and needle == val:
            filtered_items.append(item)
        elif needle and not val:
            filtered_items.append(item)

    return filtered_items
