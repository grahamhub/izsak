import logging
import os

from clients.postgres import connection
from discord.ext import tasks
from izsak import Izsak
from utils import can_upload

logging.basicConfig(level=logging.INFO)
environment = os.environ.get("IZSAK_ENV")
izsak = Izsak()

client = izsak.client

with connection() as postgres:
    categories = postgres.get_all("category")


async def media(ctx):
    if ctx.command.name == "catgirl":
        await izsak.send_random_catgirl(ctx)
    else:
        await izsak.send_media_by_category(ctx, ctx.command.name)

for cat in categories:
    print(cat)
    client.slash_command(
        name=cat.get("name"),
        description=f"Get some {cat.get('name')} goodness",
        guild_ids=[izsak.guild_id],
    )(media)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.slash_command(
    description="Upload media",
    guild_ids=[izsak.guild_id],
)
async def upload(ctx):
    await Izsak.upload_modal(ctx) if can_upload(ctx) else await Izsak.forbidden(ctx)


@client.slash_command(
    description="Tell Izsak you love him",
    guild_ids=[izsak.guild_id],
)
async def love(ctx):
    await izsak.love(ctx)


@client.slash_command(
    description="What did you just say?",
    guild_ids=[izsak.guild_id],
)
async def wtf(ctx, role):
    await izsak.wtf(ctx, role)


@client.slash_command(
    name="categories",
    description="List available categories",
    guild_ids=[izsak.guild_id],
)
async def get_categories(ctx):
    cats = '\n-'.join(list(map(lambda cat: cat.get("name"), categories)))
    msg = f"Categories:\n-{cats}"
    await izsak.send_ephemeral(ctx, msg)


@tasks.loop(hours=12)
async def send_random_catgirl():
    try:
        await izsak.send_scheduled_catgirl()
    except AttributeError as e:
        print(str(e))

izsak.start()
if environment == "PROD":
    send_random_catgirl.start()
