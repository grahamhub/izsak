from discord.ext import tasks
from izsak import Izsak

izsak = Izsak()

client = izsak.client


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    await izsak.handle_message(message)


@tasks.loop(hours=12)
async def send_random_catgirl():
    try:
        await izsak.send_random_catgirl()
    except AttributeError as e:
        print(str(e))


send_random_catgirl.start()
izsak.start()
