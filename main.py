from izsak import Izsak

izsak = Izsak()

client = izsak.client


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    await izsak.handle_message(message)

izsak.start()
