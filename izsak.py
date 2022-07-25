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
from time import sleep
from utils import (
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
        self.client = discord.Bot()
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

    async def send_random_catgirl(self, channel, sent_before=True):
        catgirl = get_random_by_category("catgirl")
        if catgirl.get("has_been_sent") and not sent_before:
            await channel.send(
                (f"Oh no! I couldn't find a catgirl {self._get_emoji('pensivecowboy')}\nThis "
                 f"probably means the database needs to be updated. In the meantime, you can "
                 f"manually run `!izsak catgirl` to get your fix.")
            )
        else:
            image = catgirl.get("url")
            if catgirl.get("nsfw"):
                image = f"||{image}||"

            print(f"Sending {image} to {channel.id}...")
            await channel.send(image)
            await channel.send(f"Artist: {catgirl.get('author', 'Unknown')}")

            if not sent_before and not catgirl.get("has_been_sent"):
                media_has_been_sent(catgirl.get('id'))

    # TODO: sanitize input
    async def upload(self, channel, args, silent=False):
        if channel.type != discord.ChannelType.private:
            return

        try:
            upload_media(args)
            if not silent:
                await channel.send("Upload successful!")
        except Exception as e:
            if not silent:
                await channel.send(f"Exception occurred: `{str(e)}`")

    async def _parse_args(self, message, silent=False):
        args = message.content.split(" ")

        if args[0] == "!wtf":
            await self.wtf(message.channel, args)
        elif args[0] == "!izsak":
            if " ".join(args[1:]).lower() == "i love you":
                await self.love(message.channel)
            elif args[1] == "upload":
                args.append(message.author.name)
                await self.upload(message.channel, args[2:], silent=silent)
            elif args[1] == "source":
                await message.channel.send("https://github.com/grahamhub/izsak")
            elif args[1] == "catgirl":
                await self.send_random_catgirl(message.channel)
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

    async def _get_all_messages(self, channel, needle):
        msgs = []
        if channel:
            async for message in channel.history(oldest_first=True):
                if message.author != self.client.user and needle in message.content:
                    msgs.append(message)
        return msgs
