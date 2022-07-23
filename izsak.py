import discord
import logging
import os
import random

from constants import (
    AUTO_SEND_CHANNEL,
    MESSAGES,
    NOT_FOUND_MAX_RETRIES,
    NOT_FOUND_MSG,
)
from exceptions import NotFound
from utils import (
    get_unsent_catgirl,
    get_random_catgirl,
    get_random_by_category,
    media_has_been_sent,
    upload_media,
)

logging.basicConfig(level=logging.INFO)


class Izsak:
    def __init__(
            self,
            discord_token=os.environ.get("IZSAK_DISCORD_TOKEN"),
            guild_id=os.environ.get("IZSAK_GUILD_ID"),
            can_dm=os.environ.get("IZSAK_CAN_DM"),
    ):
        self.client = discord.Client()
        self.token = discord_token
        self.guild_id = int(guild_id)
        self.can_dm = can_dm.split(",")

    def start(self):
        self.client.run(self.token)

    def guild(self):
        return self.client.get_guild(self.guild_id)

    def auto_send_channel(self):
        return self.guild().get_channel(AUTO_SEND_CHANNEL)

    async def handle_message(self, message):
        if message.channel.type == discord.ChannelType.private and str(message.author.id) in self.can_dm:
            await self._parse_args(message)
            return

        if message.channel.type != discord.ChannelType.private \
                and (message.author == self.client.user or message.guild.id != self.guild_id):
            return

        await self._parse_args(message)

    async def wtf(self, channel, args):
        wtf_msgs = MESSAGES.get("wtf")
        role = self._get_mentionable_role(" ".join(args[1:]))
        wtf_msgs[2] = wtf_msgs[2].format(replace_with=role)

        for msg in wtf_msgs:
            await channel.send(msg)

    async def love(self, channel):
        love_choice = random.choice(MESSAGES.get("love", ["ok"]))
        if love_choice[0] == ":":
            love_choice = self._get_emoji(love_choice.replace(":", ""))

        await channel.send(f"{love_choice}")

    async def catgirl(self, channel, sent_ok=True):
        catgirl = None
        attempts = 0
        while not catgirl and attempts < NOT_FOUND_MAX_RETRIES:
            try:
                catgirl = get_random_catgirl(has_been_sent_ok=sent_ok)
            except NotFound as e:
                print(str(e))
            finally:
                attempts += 1

        if catgirl:
            image = catgirl.get('url')
            if catgirl.get('nsfw'):
                image = f"<||{image}||>"

            print(f"Sending {image} to {channel.id}...")
            await channel.send(image)
            await channel.send(f"Artist: {catgirl.get('author', 'Unknown')}")

            if not sent_ok:
                media_has_been_sent(id)
        else:
            await channel.send(
                f"Oh no! I couldn't find a catgirl {self._get_emoji('pensivecowboy')}, if this persists ping grotto"
            )

    async def send_random_catgirl(self):
        catgirl = None
        attempts = 0
        channel = self.auto_send_channel()
        while not catgirl and attempts < NOT_FOUND_MAX_RETRIES:
            try:
                catgirl = get_unsent_catgirl()
            except NotFound as e:
                print(str(e))
            finally:
                attempts += 1

        if catgirl:
            image = catgirl.get("url")
            if catgirl.get("nsfw"):
                image = f"<||{image}||>"

            print(f"Sending {image} to {channel.id}...")
            await channel.send(image)
            await channel.send(f"Artist: {catgirl.get('author', 'Unknown')}")
            media_has_been_sent(catgirl.get('id'))
        else:
            await channel.send(
                (f"Oh no! I couldn't find a catgirl {self._get_emoji('pensivecowboy')}\nThis "
                 f"probably means the database needs to be updated. In the meantime, you can "
                 f"manually run `!izsak catgirl` to get your fix.")
            )

    # TODO: sanitize input
    async def upload(self, channel, args):
        if channel.type != discord.ChannelType.private:
            return

        try:
            upload_media(args)
            await channel.send("Upload successful!")
        except Exception as e:
            await channel.send(f"Exception occurred: `{str(e)}`")

    async def _parse_args(self, message):
        args = message.content.split(" ")

        if args[0] == "!wtf":
            await self.wtf(message.channel, args)
        elif args[0] == "!izsak":
            if " ".join(args[1:]).lower() == "i love you":
                await self.love(message.channel)
            elif args[1] == "upload":
                args.append(message.author.name)
                await self.upload(message.channel, args[2:])
            elif args[1] == "source":
                await message.channel.send("https://github.com/grahamhub/izsak")
            elif args[1] == "catgirl":
                await self.catgirl(message.channel)
            elif args[1] == "media":
                item = self._parse_media(args[2])
                image = item.get("image", False)
                if image:
                    await message.channel.send(image)
                    await message.channel.send(item.get("artist"))
                else:
                    await message.channel.send(NOT_FOUND_MSG)


    def _get_mentionable_role(self, name):
        guild = self.guild()
        print(guild)
        role = discord.utils.get(guild.roles, name=name)
        return f"<@&{role.id}>"

    def _get_mentionable_user(self, id):
        return f"<@{id}>"

    def _get_emoji(self, name):
        emoji = discord.utils.get(self.guild().emojis, name=name)
        return f"<:{name}:{emoji.id}>"

    def _parse_media(self, category):
        item = get_random_by_category(category)
        if item is None:
            return {}

        image = item.get("url")

        if item.get("nsfw"):
            image = f"||{image}||"

        return {
            "image": image,
            "artist": f"Artist: {item.get('author', 'Unknown')}",
        }
