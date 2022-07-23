from postgres import connection
from random import choice
from exceptions import NotFound


def get_random_media_item():
    item = None
    with connection() as postgres:
        row_length = int(postgres.get_row_count("media")[0])
        row_id = choice(range(1, row_length))
        item = postgres.get_by_id("media", row_id)

    return item


def get_random_catgirl(has_been_sent_ok=False):
    item = None
    with connection() as postgres:
        row_length = int(postgres.get_row_count("media")[0])
        if row_length > 1:
            row_id = choice(range(1, row_length))
        elif row_length == 0:
            raise NotFound("there are no images in the media table")
        else:
            row_id = 1

        if has_been_sent_ok:
            item = postgres.select("media", f"id = {row_id} AND category = 'catgirl';")
        else:
            item = postgres.select("media", f"id = {row_id} AND category = 'catgirl' AND NOT has_been_sent;")
            print(item)

    return item


def upload_media(args):
    with connection() as postgres:
        postgres.insert(
            "media",
            [
                "url",
                "author",
                "category",
                "nsfw",
                "submitted_by",
            ],
            args
        )


def media_has_been_sent(id):
    with connection() as postgres:
        postgres.update_field("media", "has_been_sent", True, id)


def get_by_id(id):
    item = None
    with connection() as postgres:
        item = postgres.get_by_id("media", id)

    return item
