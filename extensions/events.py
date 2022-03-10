# coding=utf-8
import json
import re
import sys
import traceback
from datetime import datetime, timedelta, timezone

import discord
from discord import Embed, Color
from discord.ext import commands
from discord.ext.commands import Cog


class Events(Cog):
    """Events Cog"""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.last_sensitive_logged = {}

    async def sensitive_scan(self, message: discord.Message) -> None:
        """Scans for sensitive topics"""
        with open("sensitive_settings.json", encoding="utf8") as json_dict:
            fulldict = json.load(json_dict)
        used_words = set()
        count_found = 0
        for word in fulldict["words"]:
            if word in message.content.lower():
                count_found += 1
                used_words.add(word)
        self.last_sensitive_logged.setdefault(
            message.author.id, datetime.now() - timedelta(days=1)
        )
        if datetime.now() > (
            self.last_sensitive_logged[message.author.id] + timedelta(minutes=5)
        ) and (
            (
                count_found >= 2
                and 25 <= (len(message.content) - len("".join(used_words))) < 50
            )
            or (
                count_found > 2
                and (len(message.content) - len("".join(used_words))) >= 50
            )
            or (
                count_found >= 1
                and (len(message.content) - len("".join(used_words))) < 25
            )
        ):
            webhook = await self.bot.fetch_webhook(fulldict["webhook_id"])
            bot_user = await self.bot.fetch_user(406885177281871902)
            embed = Embed(
                title="Probable Sensitive Topic Detected",
                description=f"Content:\n {message.content}",
                color=Color.red(),
                timestamp=datetime.now(tz=timezone.utc),
            )
            embed.add_field(
                name="Words Found:", value=", ".join(used_words)[0:1024], inline=True
            )
            embed.add_field(
                name="Author:",
                value=f"{message.author.display_name}: "
                f"{message.author.name}#{message.author.discriminator}",
                inline=True,
            )
            embed.add_field(
                name="Message Link:",
                value=f"[Link]({message.message.make_link(message.guild_id)})",
                inline=True,
            )
            if message.message.channel_id == 926532222398369812:
                await message.channel.send(embed=embed)
            if message.channel.category.category_id in (
                360818916861280256,
                942578610336837632,
            ):
                return
            if message.channel.id == 837816311722803260:
                return
            await webhook.send(
                username=bot_user.name, avatar_url=bot_user.avatar.url, embed=embed
            )
            self.last_sensitive_logged[message.author.id] = datetime.now()

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Guild Message Create Handler ***DO NOT CALL MANUALLY***"""
        if message.content is not None and not message.author.bot:
            await self.sensitive_scan(message)
            if message.guild is None:
                channel = await self.bot.fetch_channel(906578081496584242)
                await channel.send(
                    message.author.mention,
                    allowed_mentions=discord.AllowedMentions(
                        everyone=False, roles=False, users=False
                    ),
                )
                await channel.send(
                    message.content,
                    allowed_mentions=discord.AllowedMentions(
                        everyone=False, roles=False, users=False
                    ),
                )
                return
            if not any(
                role.id
                in [
                    338173415527677954,
                    253752685357039617,
                    225413350874546176,
                    387037912782471179,
                    406690402956083210,
                    729368484211064944,
                ]
                for role in message.author.roles
            ) and any(
                item in message.content
                for item in [f"<@&{message.guild.id}>", "@everyone", "@here"]
            ):
                await message.author.add_roles(
                    discord.Object(id=676250179929636886),
                    discord.Object(id=684936661745795088),
                )
                await message.delete()
                channel = await self.bot.fetch_channel(426016300439961601)
                embed = Embed(
                    description=message.content,
                    title="Mute: Everyone/Here Ping sent by non mod",
                    color=Color.red(),
                ).set_footer(
                    text=f"Sent by {message.author.display_name}-{message.author.id}",
                    icon_url=message.author.avatar.url,
                )
                await channel.send(embed=embed)
            if message.author.bot or not message.content:
                return
            if re.search(
                r"~~:.|:;~~", message.content, re.MULTILINE | re.IGNORECASE
            ) or re.search(
                r"tilde tilde colon dot vertical bar colon semicolon tilde tilde",
                message.content,
                re.MULTILINE | re.IGNORECASE,
            ):
                await message.delete()

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """
        # This prevents any commands with local handlers being
        # handled here in on_command_error.
        if hasattr(ctx.command, "on_error"):
            return

        # This prevents any cogs with an overwritten
        # cog_command_error being handled here.
        cog: Cog = ctx.cog
        if (
                cog and
                (cog._get_overridden_method(cog.cog_command_error)
                 is not None)):  # skipcq: PYL-W0212
            return

        ignored = (commands.CommandNotFound,)

        # Allows us to check for original exceptions
        # raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, "original", error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f"{ctx.command} has been disabled.")

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(
                    f"{ctx.command} can not be used in Private Messages."
                )
            except discord.HTTPException:
                pass

        # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Bad Argument.")

        else:
            # All other Errors not returned come here.
            # And we can just print the default TraceBack.
            print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )


def setup(bot: commands.Bot):
    """Loads Plugin"""
    bot.add_cog(Events(bot))
