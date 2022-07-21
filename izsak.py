import discord
import logging
import os
import random

from constants import MESSAGES

logging.basicConfig(level=logging.INFO)


class Izsak:
    def __init__(self, discord_token=os.environ.get("IZSAK_DISCORD_TOKEN"), guild_id=os.environ.get("GUILD_ID")):
        self.client = discord.Client()
        self.token = discord_token
        self.guild_id = int(guild_id)

    def start(self):
        self.client.run(self.token)

    def guild(self):
        return self.client.get_guild(self.guild_id)

    async def handle_message(self, message):
        if message.author == self.client.user:
            return

        await self._parse_args(message)

    async def wtf(self, channel, args):
        wtf_msgs = MESSAGES.get("wtf")
        role = self._get_mentionable_role(" ".join(args[1:]))
        wtf_msgs[2] = wtf_msgs[2].format(replace_with=role)

        for msg in wtf_msgs:
            await channel.send(msg)

    async def love(self, channel, user):
        love_choice = random.choice(MESSAGES.get("love", ["ok"]))
        if love_choice[0] == ":":
            love_choice = self._get_emoji(love_choice.replace(":", ""))

        await channel.send(f"{love_choice}")

    async def _parse_args(self, message):
        args = message.content.split(" ")

        if args[0] == "!wtf":
            await self.wtf(message.channel, args)
        elif args[0] == "!izsak":
            if " ".join(args[1:]).lower() == "i love you":
                await self.love(message.channel, message.author.id)

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
