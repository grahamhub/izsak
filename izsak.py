import discord
import os
import random

from constants import (
    AUTO_SEND_CHANNEL,
    MESSAGES,
    NOT_FOUND_MSG,
)
from discord import ApplicationContext
from clients.postgres import Postgres
from views import views


class Izsak:
    def __init__(
            self,
            discord_token=os.environ.get("IZSAK_DISCORD_TOKEN"),
            guild_id=os.environ.get("IZSAK_GUILD_ID"),
            can_upload=os.environ.get("IZSAK_CAN_UPLOAD"),
    ):
        self.client = discord.Bot()
        self.token = discord_token
        self.guild_id = int(guild_id)
        self.can_upload = can_upload.split(",")

    @staticmethod
    async def forbidden(ctx: ApplicationContext):
        await ctx.respond("You are not allowed to execute this command.")

    @staticmethod
    async def upload_modal(ctx: ApplicationContext):
        modal = views.UploadModal(title="Upload a new media item")
        await ctx.send_modal(modal)

    # TODO: sanitize input
    @staticmethod
    async def upload(interaction: discord.Interaction, *args):

        try:
            Postgres.upload_media(
                url=args[0],
                author=args[1],
                category=args[2].split(","),
                nsfw=args[3],
                submitted_by=str(interaction.user.id),
            )
            await interaction.response.send_message(
                content="Upload successful!",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                content=f"Exception occurred: `{str(e)}`",
                ephemeral=True,
            )

    def start(self):
        self.client.run(self.token)

    def guild(self):
        return self.client.get_guild(self.guild_id)

    def auto_send_channel(self):
        return self.guild().get_channel(AUTO_SEND_CHANNEL)

    async def wtf(self, ctx: ApplicationContext, role):
        wtf_msgs = MESSAGES.get("wtf")
        role = self._get_mentionable_role(role)
        wtf_msgs[2] = wtf_msgs[2].format(replace_with=role)

        await ctx.respond(wtf_msgs[0])
        for msg in wtf_msgs[1:]:
            await ctx.send(msg)

    async def love(self, ctx: ApplicationContext):
        love_choice = random.choice(MESSAGES.get("love", ["ok"]))
        if love_choice[0] == ":":
            try:
                love_choice = self._get_emoji(love_choice.replace(":", ""))
            except AttributeError:
                love_choice = "tch.."

        await ctx.respond(f"{love_choice}")

    async def send_random_catgirl(self, ctx: ApplicationContext):
        catgirl = Postgres.get_random_by_category("catgirl")
        image = catgirl.get("url")
        if catgirl.get("nsfw"):
            image = f"||{image}||"
        user = await self.get_user_metadata(int(catgirl.get("submitted_by")))
        print(f"Sending {image} to {ctx.channel.id}...")
        embed = views.ResponseEmbed(
            embed_title="random catgirl attack!",
            author=catgirl.get("author"),
            url=image,
            footer_text=f"{user.get('name')} on {catgirl.get('submitted_on').strftime('%m-%d-%Y')}",
            footer_icon_url=user.get("icon_url"),
        ).embed
        await ctx.send_response(embeds=[embed])

    async def send_scheduled_catgirl(self):
        catgirl = Postgres.get_random_by_category("catgirl", filter_key="has_been_sent", filter_val=False)
        channel = self.auto_send_channel()
        if not catgirl:
            await channel.send(
                (f"Oh no! I couldn't find a catgirl {self._get_emoji('pensivecowboy')}\nThis "
                 f"probably means the database needs to be updated. In the meantime, you can "
                 f"manually run `/catgirl` to get your fix.")
            )
        else:
            image = catgirl.get("url")
            if catgirl.get("nsfw"):
                image = f"||{image}||"

            print(f"Sending {image} to {channel.id}...")
            await channel.send(image)
            await channel.send(f"Artist: {catgirl.get('author', 'Unknown')}")

            Postgres.media_has_been_sent(catgirl.get('id'))

    async def send_media_by_category(self, ctx: ApplicationContext, category):
        item = self._parse_media(category)
        image = item.get("image", False)
        if image:
            await ctx.respond(image)
            await ctx.send(item.get("artist"))
        else:
            await ctx.respond(NOT_FOUND_MSG)

    async def get_user_metadata(self, id):
        user = await self.guild().fetch_member(id)
        return {
            "icon_url": user.display_avatar.url,
            "name": user.display_name,
        }

    def _get_mentionable_role(self, name):
        guild = self.guild()
        role = discord.utils.get(guild.roles, name=name)
        return f"<@&{role.id}>"

    def _get_mentionable_user(self, id):
        return f"<@{id}>"

    def _get_emoji(self, name):
        emoji = discord.utils.get(self.guild().emojis, name=name)
        return f"<:{name}:{emoji.id}>"

    def _parse_media(self, category):
        item = Postgres.get_random_by_category(category)
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
