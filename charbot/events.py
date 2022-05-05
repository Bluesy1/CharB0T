# -*- coding: utf-8 -*-
#  ----------------------------------------------------------------------------
#  MIT License
#
# Copyright (c) 2022 Bluesy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#  ----------------------------------------------------------------------------
"""Event handling for Charbot."""
import json
import re
import sys
import traceback
from datetime import datetime, timedelta, timezone

import discord
from discord import Embed, Color
from discord.ext import commands
from discord.ext.commands import Cog

from main import CBot


class Events(Cog):
    """Event Cog.

    This cog handles all events that occur in the server.

    Parameters
    ----------
    bot : CBot
        The bot instance.

    Attributes
    ----------
    bot : CBot
        The bot instance.
    last_sensitive_logged : dict
        A dictionary of the last time sensitive messages were logged.
    """

    def __init__(self, bot: CBot):
        self.bot = bot
        self.last_sensitive_logged = {}

    async def sensitive_scan(self, message: discord.Message) -> None:
        """Check and take action if a message contains sensitive content.

        It uses the list of words defined in the sensitive_settings.json file.

        Parameters
        ----------
        self : Events
            The Events cog.
        message : discord.Message
            The message to check.
        """
        with open("sensitive_settings.json", encoding="utf8") as json_dict:
            fulldict = json.load(json_dict)
        used_words = set()
        count_found = 0
        for word in fulldict["words"]:
            if word in message.content.lower():
                count_found += 1
                used_words.add(word)
        self.last_sensitive_logged.setdefault(message.author.id, datetime.now() - timedelta(days=1))
        if datetime.now() > (self.last_sensitive_logged[message.author.id] + timedelta(minutes=5)) and (
            (count_found >= 2 and 25 <= (len(message.content) - len("".join(used_words))) < 50)
            or (count_found > 2 and (len(message.content) - len("".join(used_words))) >= 50)
            or (count_found >= 1 and (len(message.content) - len("".join(used_words))) < 25)
        ):
            webhook = await self.bot.fetch_webhook(fulldict["webhook_id"])
            embed = Embed(
                title="Probable Sensitive Topic Detected",
                description=f"Content:\n {message.content}",
                color=Color.red(),
                timestamp=datetime.now(tz=timezone.utc),
            )
            embed.add_field(name="Words Found:", value=", ".join(used_words)[0:1024], inline=True)
            embed.add_field(
                name="Author:",
                value=f"{message.author.display_name}: " f"{message.author.name}#{message.author.discriminator}",
                inline=True,
            )
            embed.add_field(
                name="Message Link:",
                value=f"[Link]({message.jump_url})",
                inline=True,
            )
            if message.channel.id == 926532222398369812:
                await message.channel.send(embed=embed)
            channel = message.channel
            if isinstance(channel, discord.abc.GuildChannel):
                category = channel.category
                if category is not None and category.id in (360818916861280256, 942578610336837632):
                    return
            if message.channel.id == 837816311722803260:
                return
            bot_user = self.bot.user
            assert isinstance(bot_user, discord.ClientUser)
            await webhook.send(username=bot_user.name, avatar_url=bot_user.display_avatar.url, embed=embed)
            self.last_sensitive_logged[message.author.id] = datetime.now()

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Listen for messages sent that the bot can see.

        If the message is sent by a non-mod user, it will check for an unallowed ping
        and will delete the message if it is found, and log it.
        Scans guild messages for sensitive content
        If the message is a dm, it logs it in the dm_logs channel and redirects them to the new mod support method.

        Parameters
        ----------
        self : Events
            The Events cog.
        message : discord.Message
            The message sent to the websocket from discord.
        """
        if message.content is not None and not message.author.bot:
            await self.sensitive_scan(message)
            if message.guild is None:
                channel = await self.bot.fetch_channel(906578081496584242)
                assert isinstance(channel, discord.TextChannel)  # skipcq: BAN-B101
                mentions = discord.AllowedMentions(everyone=False, roles=False, users=False)
                await channel.send(message.author.mention, allowed_mentions=mentions)
                await channel.send(message.content, allowed_mentions=mentions)
                await message.channel.send(
                    "Hi! If this was an attempt to reach the mod team through modmail,"
                    " that has been removed, in favor of "
                    "mod support, which you can find in <#398949472840712192>"
                )
                return
            author = message.author
            assert isinstance(author, discord.Member)  # skipcq: BAN-B101
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
                for role in author.roles
            ) and any(item in message.content for item in [f"<@&{message.guild.id}>", "@everyone", "@here"]):
                await author.add_roles(
                    discord.Object(id=676250179929636886),
                    discord.Object(id=684936661745795088),
                )
                await message.delete()
                with open("sensitive_settings.json", encoding="utf8") as json_dict:
                    webhook = await self.bot.fetch_webhook(json.load(json_dict)["webhook_id"])
                embed = Embed(
                    description=message.content,
                    title="Mute: Everyone/Here Ping sent by non mod",
                    color=Color.red(),
                ).set_footer(
                    text=f"Sent by {message.author.display_name}-{message.author.id}",
                    icon_url=author.display_avatar.url,
                )
                bot_user = self.bot.user
                assert isinstance(bot_user, discord.ClientUser)
                await webhook.send(username=bot_user.name, avatar_url=bot_user.display_avatar.url, embed=embed)
            if message.author.bot or not message.content:
                return
            if re.search(r"~~:.|:;~~", message.content, re.MULTILINE | re.IGNORECASE) or re.search(
                r"tilde tilde colon dot vertical bar colon semicolon tilde tilde",
                message.content,
                re.MULTILINE | re.IGNORECASE,
            ):
                await message.delete()

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        """Trigger when an error is raised while invoking a command.

        Parameters
        ----------
        self : Events
            The Events cog.
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
        if cog and (
            # skipcq: PYL-W0212
            cog._get_overridden_method(cog.cog_command_error)
            is not None
        ):
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
                await ctx.author.send(f"{ctx.command} can not be used in Private Messages.")
            except discord.HTTPException:
                pass

        # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Bad Argument.")

        else:
            # All other Errors not returned come here.
            # And we can just print the default TraceBack.
            assert error is not None  # skipcq: BAN-B101
            print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


async def setup(bot: CBot):
    """Load the event handler for the bot.

    Parameters
    ----------
    bot : CBot
        The bot to load the event handler for.
    """
    await bot.add_cog(Events(bot))
