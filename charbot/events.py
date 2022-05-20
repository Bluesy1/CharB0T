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
from datetime import datetime, timedelta, timezone

import discord
from discord import Color, Embed
from discord.ext import tasks
from discord.ext.commands import Cog
from discord.utils import utcnow

from bot import CBot


def sensitive_embed(message: discord.Message, used: set[str]) -> discord.Embed:
    """Create an embed with the message content.

    Parameters
    ----------
    message : discord.Message
        The message to create the embed from.
    used : set[str]
        The set of sensitive words used in the message.
    """
    embed = Embed(
        title="Probable Sensitive Topic Detected",
        description=f"Content:\n {message.content}",
        color=Color.red(),
        timestamp=datetime.now(tz=timezone.utc),
    )
    embed.add_field(name="Words Found:", value=", ".join(used)[0:1024], inline=True)
    embed.add_field(
        name="Author:",
        value=f"{message.author.display_name}: " f"{message.author.name}#{message.author.discriminator}",
        inline=True,
    )
    return embed.add_field(
        name="Message Link:",
        value=f"[Link]({message.jump_url})",
        inline=True,
    )


async def time_string_from_seconds(delta: float) -> str:
    """Convert seconds to a string.

    Parameters
    ----------
    delta : float
        The number of seconds to convert to a string
    """
    minutes, sec = divmod(delta, 60)
    hour, minutes = divmod(minutes, 60)
    day, hour = divmod(hour, 24)
    year, day = divmod(day, 365)
    return f"{year} Year(s), {day} Day(s), {hour} Hour(s)," f" {minutes} Min(s), {sec:.2f} Sec(s)"


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
        self.timeouts = {}
        self.members: dict[int, datetime] = {}

    async def cog_load(self) -> None:
        """Cog load function.

        This is called when the cog is loaded, and initializes the
        log_untimeout task and the members cache

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        """
        self.log_untimeout.start()
        guild = await self.bot.fetch_guild(225345178955808768)
        generator = guild.fetch_members(limit=None)
        self.members.update({user.id: user.joined_at async for user in generator if user.joined_at is not None})

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Call when cog is unloaded.

        This stops the log_untimeout task

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        """
        self.log_untimeout.cancel()

    async def parse_timeout(self, after: discord.Member):
        """Parse the timeout and logs it to the mod log.

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        after : discord.Member
            The member after the update
        """
        until = after.timed_out_until
        assert isinstance(until, datetime)  # skipcq: BAN-B101
        time_delta = until + timedelta(seconds=1) - datetime.now(tz=timezone.utc)
        time_string = ""
        if time_delta.days // 7 != 0:
            time_string += f"{time_delta.days // 7} Week{'s' if time_delta.days // 7 > 1 else ''}"
        if time_delta.days % 7 != 0:
            time_string += f"{', ' if bool(time_string) else ''}{time_delta.days % 7} Day(s) "
        if time_delta.seconds // 3600 > 0:
            time_string += f"{', ' if bool(time_string) else ''}" f"{time_delta.seconds // 3600} Hour(s) "
        if (time_delta.seconds % 3600) // 60 != 0:
            time_string += f"{', ' if bool(time_string) else ''}" f"{(time_delta.seconds % 3600) // 60} Minute(s) "
        if (time_delta.seconds % 3600) % 60 != 0:
            time_string += f"{', ' if bool(time_string) else ''}" f"{(time_delta.seconds % 3600) % 60} Second(s) "
        embed = Embed(color=Color.red())
        embed.set_author(name=f"[TIMEOUT] {after.name}#{after.discriminator}")
        embed.add_field(name="User", value=after.mention, inline=True)
        embed.add_field(name="Duration", value=time_string, inline=True)
        with open("sensitive_settings.json", encoding="utf8") as json_dict:
            webhook = await self.bot.fetch_webhook(json.load(json_dict)["webhook_id"])
        bot_user = self.bot.user
        assert isinstance(bot_user, discord.ClientUser)  # skipcq: BAN-B101
        await webhook.send(username=bot_user.name, avatar_url=bot_user.display_avatar.url, embed=embed)
        self.timeouts.update({after.id: after.timed_out_until})

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
        if message.guild is not None and message.guild.id == 225345178955808768:
            channel = message.channel
            assert isinstance(channel, discord.abc.GuildChannel)  # skipcq: BAN-B101
            with open("sensitive_settings.json", encoding="utf8") as json_dict:
                fulldict = json.load(json_dict)
            used_words = set()
            count_found = 0
            for word in fulldict["words"]:
                if word in message.content.lower():
                    count_found += 1
                    used_words.add(word)
            self.last_sensitive_logged.setdefault(message.author.id, datetime.now() - timedelta(days=1))
            if datetime.now() > (self.last_sensitive_logged[message.author.id] + timedelta(minutes=5)) and any(
                [
                    (count_found >= 2 and 25 <= (len(message.content) - len("".join(used_words))) < 50),
                    (count_found > 2 and (len(message.content) - len("".join(used_words))) >= 50),
                    (count_found >= 1 and (len(message.content) - len("".join(used_words))) < 25),
                ]
            ):
                webhook = await self.bot.fetch_webhook(fulldict["webhook_id"])
                category = channel.category
                if channel.id in (837816311722803260, 926532222398369812) or (
                    category is not None and category.id in (360818916861280256, 942578610336837632)
                ):
                    return
                bot_user = self.bot.user
                assert isinstance(bot_user, discord.ClientUser)  # skipcq: BAN-B101
                await webhook.send(
                    username=bot_user.name,
                    avatar_url=bot_user.display_avatar.url,
                    embed=sensitive_embed(message, used_words),
                )
                self.last_sensitive_logged[message.author.id] = datetime.now()

    # noinspection DuplicatedCode
    @tasks.loop(seconds=30)
    async def log_untimeout(self) -> None:
        """Untimeout Report Task.

        This task runs every 30 seconds and checks if any users that have been timed out have had their timeouts
        expired. If they have, it will send a message to the mod channel.

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        """
        removeable = []
        for i, j in self.timeouts.copy().items():
            if j < datetime.now(tz=timezone.utc):
                member = await (await self.bot.fetch_guild(225345178955808768)).fetch_member(i)
                if not member.is_timed_out():
                    embed = Embed(color=Color.green())
                    embed.set_author(name=f"[UNTIMEOUT] {member.name}#{member.discriminator}")
                    embed.add_field(name="User", value=member.mention, inline=True)
                    with open("sensitive_settings.json", encoding="utf8") as json_dict:
                        webhook = await self.bot.fetch_webhook(json.load(json_dict)["webhook_id"])
                    bot_user = self.bot.user
                    assert isinstance(bot_user, discord.ClientUser)  # skipcq: BAN-B101
                    await webhook.send(username=bot_user.name, avatar_url=bot_user.display_avatar.url, embed=embed)
                    removeable.append(i)
                elif member.is_timed_out():
                    self.timeouts.update({i: member.timed_out_until})
        for i in removeable:
            self.timeouts.pop(i)

    @Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Process when a member joins the server and adds them to the members cache.

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        member : discord.Member
            The member that joined the server
        """
        if member.guild.id == 225345178955808768:
            self.members.update({member.id: utcnow()})

    @Cog.listener()
    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent) -> None:
        """Process when a member leaves the server and removes them from the members cache.

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        payload : discord.RawMemberRemoveEvent
            The payload of the member leaving the server
        """
        if payload.guild_id == 225345178955808768:
            user = payload.user
            if isinstance(user, discord.Member):
                self.members.pop(user.id, None)
                time_string = await time_string_from_seconds(abs(utcnow() - self.members[user.id]).total_seconds())
            elif isinstance(user, discord.User) and user.id in self.members:
                time_string = await time_string_from_seconds(abs(utcnow() - self.members.pop(user.id)).total_seconds())
            else:
                time_string = "Unknown"
            channel = await self.bot.fetch_channel(430197357100138497)
            assert isinstance(channel, discord.TextChannel)  # skipcq: BAN-B101
            await channel.send(
                f"**{user.name}#{user.discriminator}** has left the server. "
                f"ID:{user.id}. Time on Server: {time_string}"
            )

    # noinspection PyBroadException,DuplicatedCode
    @Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Process when a member is timed out or untimed out.

        If the member is timed out, it adds them to the timeouts cache
        If the member is untimed out, it removes them from the timeouts cache
        In both cases, it logs the action to the mod log

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        before : discord.Member
            The member before the update
        after : discord.Member
            The member after the update
        """
        try:
            if after.timed_out_until != before.timed_out_until:
                if after.is_timed_out():
                    await self.parse_timeout(after)
                else:
                    embed = Embed(color=Color.green())
                    embed.set_author(name=f"[UNTIMEOUT] {after.name}#{after.discriminator}")
                    embed.add_field(name="User", value=after.mention, inline=True)
                    with open("sensitive_settings.json", encoding="utf8") as json_dict:
                        webhook = await self.bot.fetch_webhook(json.load(json_dict)["webhook_id"])
                    bot_user = self.bot.user
                    assert isinstance(bot_user, discord.ClientUser)  # skipcq: BAN-B101
                    await webhook.send(username=bot_user.name, avatar_url=bot_user.display_avatar.url, embed=embed)
                    self.timeouts.pop(after.id)
        except Exception:  # skipcq: PYL-W0703
            if after.is_timed_out():
                await self.parse_timeout(after)

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
                assert isinstance(bot_user, discord.ClientUser)  # skipcq: BAN-B101
                await webhook.send(username=bot_user.name, avatar_url=bot_user.display_avatar.url, embed=embed)
            if message.author.bot or not message.content:
                return
            if re.search(r"~~:.|:;~~", message.content, re.MULTILINE | re.IGNORECASE) or re.search(
                r"tilde tilde colon dot vertical bar colon semicolon tilde tilde",
                message.content,
                re.MULTILINE | re.IGNORECASE,
            ):
                await message.delete()


async def setup(bot: CBot):
    """Load the event handler for the bot.

    Parameters
    ----------
    bot : CBot
        The bot to load the event handler for.
    """
    await bot.add_cog(Events(bot))
