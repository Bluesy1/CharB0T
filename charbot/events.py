# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT
"""Event handling for Charbot."""
import pathlib
import re
from datetime import datetime, timedelta, timezone
from typing import cast, TYPE_CHECKING, Final

import discord
import orjson
from discord import Color, Embed
from discord.ext import tasks
from discord.ext.commands import Cog
from discord.utils import MISSING, utcnow
from urlextract import URLExtract

from . import CBot


if TYPE_CHECKING:  # pragma: no cover
    # noinspection PyUnresolvedReferences
    from .levels import Leveling


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
        timestamp=utcnow(),
    )
    embed.add_field(name="Words Found:", value=", ".join(used)[:1024], inline=True)
    embed.add_field(
        name="Author:",
        value=f"{message.author.display_name}: {message.author}",
        inline=True,
    )
    return embed.add_field(
        name="Message Link:",
        value=f"[Link]({message.jump_url})",
        inline=True,
    )


def time_string_from_seconds(delta: float) -> str:
    """Convert seconds to a string.

    Parameters
    ----------
    delta : float
        The number of seconds to convert to a string

    Returns
    -------
    delta: str
        The delta as a string
    """
    minutes, sec = divmod(delta, 60)
    hour, minutes = divmod(minutes, 60)
    day, hour = divmod(hour, 24)
    year, day = divmod(day, 365)
    return f"{year} Year(s), {day} Day(s), {hour} Hour(s), {minutes} Min(s), {sec:.2f} Sec(s)"


def url_posting_allowed(
    channel: discord.TextChannel | discord.VoiceChannel | discord.Thread, roles: list[discord.Role]
) -> bool:
    """Check if the combination of roles and channel allows for links to be posted.

    Parameters
    ----------
    channel: discord.TextChannel | discord.VoiceChannel | discord.Thread
        The channel the message was posted in
    roles: list[discord.Role]
        The roles the user has

    Returns
    -------
    allowed: bool
        Whether or not the combination is allowed
    """
    if (
        isinstance(channel, discord.Thread)
        and channel.parent_id == 1019647326601609338
        and any(tag.id == 1019691620741959730 for tag in channel.applied_tags)
    ):
        # if the parent is this, then the channel is the games-forums channel and if the channel has the
        # games-forums tag, then it's a game thread, and we want to allow urls in it
        return True
    if channel.category_id in {360814817457733635, 360818916861280256, 942578610336837632}:
        # if the channel is in an admin or info category, we want to allow urls
        return True
    if channel.id in {723653004301041745, 338894508894715904, 407185164200968203}:
        # the channel is allowed to have links, bit they may not embed
        return True
    # If so far the url hasn't been allowed, test if the author has a role that allows it
    return any(
        role.id
        in {
            337743478190637077,
            685331877057658888,
            969629622453039104,
            969629628249563166,
            969629632028614699,
            969628342733119518,
            969627321239760967,
            406690402956083210,
            387037912782471179,
            338173415527677954,
            725377514414932030,
            925956396057513985,
            253752685357039617,
            225413350874546176,
            729368484211064944,
        }
        for role in roles
    )


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
        self.webhook: discord.Webhook = MISSING
        self.tilde_regex = re.compile(
            r"~~:\.\|:;~~|tilde tilde colon dot vertical bar colon semicolon tilde tilde", re.MULTILINE | re.IGNORECASE
        )
        self.extractor = URLExtract()
        self.sensitive_settings_path: Final[pathlib.Path] = pathlib.Path(__file__).parent / "sensitive_settings.json"

    async def cog_load(self) -> None:
        """Cog load function.

        This is called when the cog is loaded, and initializes the
        log_un-timeout task and the members cache
        """
        self.log_untimeout.start()
        guild = self.bot.get_guild(225345178955808768)
        if guild is None:
            guild = await self.bot.fetch_guild(225345178955808768)
        generator = guild.fetch_members(limit=None)
        self.members.update({user.id: user.joined_at async for user in generator if user.joined_at is not None})
        with open(self.sensitive_settings_path, "rb") as json_dict:
            self.webhook = await self.bot.fetch_webhook(orjson.loads(json_dict.read())["webhook_id"])

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Call when cog is unloaded.

        This stops the log_untimeout task
        """
        self.log_untimeout.cancel()

    async def parse_timeout(self, after: discord.Member):
        """Parse the timeout and logs it to the mod log.

        Parameters
        ----------
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
        bot_user = self.bot.user
        assert isinstance(bot_user, discord.ClientUser)  # skipcq: BAN-B101
        await self.webhook.send(username=bot_user.name, avatar_url=bot_user.display_avatar.url, embed=embed)
        self.timeouts.update({after.id: after.timed_out_until})

    async def sensitive_scan(self, message: discord.Message) -> bool:
        """Check and take action if a message contains sensitive content.

        It uses the list of words defined in the sensitive_settings.json file.

        Parameters
        ----------
        message : discord.Message
            The message to check.

        Returns
        -------
        allowed: bool
            Whether the message is allowed or not.
        """
        if message.guild is not None and message.guild.id == 225345178955808768:
            channel = cast(discord.abc.GuildChannel | discord.Thread, message.channel)
            with open(self.sensitive_settings_path, "rb") as json_dict:
                fulldict = orjson.loads(json_dict.read())
            used_words = {
                word
                for word in fulldict["words"]
                if word in message.content.lower()
                and (word != "war" or any(word in fulldict["words"] for word in message.content.lower()))
            }
            self.last_sensitive_logged.setdefault(message.author.id, datetime.now() - timedelta(days=1))
            if datetime.now() > (self.last_sensitive_logged[message.author.id] + timedelta(minutes=5)) and any(
                [
                    (len(used_words) >= 2 and 25 <= (len(message.content) - len("".join(used_words))) < 50),
                    (len(used_words) > 2 and (len(message.content) - len("".join(used_words))) >= 50),
                    (len(used_words) >= 1 and (len(message.content) - len("".join(used_words))) < 25),
                ]
            ):
                if channel.id in (837816311722803260, 926532222398369812) or (
                    channel.category_id in (360818916861280256, 942578610336837632)
                ):
                    return True
                bot_user = cast(discord.ClientUser, self.bot.user)
                await self.webhook.send(
                    username=bot_user.name,
                    avatar_url=bot_user.display_avatar.url,
                    embed=sensitive_embed(message, used_words),
                )
                self.last_sensitive_logged[message.author.id] = datetime.now()
                return False
        return True

    # noinspection DuplicatedCode
    @tasks.loop(seconds=30)
    async def log_untimeout(self) -> None:
        """Un-timeout Report Task.

        This task runs every 30 seconds and checks if any users that have been timed out have had their timeouts
        expired. If they have, it will send a message to the mod channel.
        """
        removable = []
        for i, j in self.timeouts.copy().items():
            if j < datetime.now(tz=timezone.utc):
                guild = self.bot.get_guild(225345178955808768)
                if guild is None:
                    guild = await self.bot.fetch_guild(225345178955808768)
                member = await guild.fetch_member(i)
                if not member.is_timed_out():
                    embed = Embed(color=Color.green())
                    embed.set_author(name=f"[UNTIMEOUT] {member.name}#{member.discriminator}")
                    embed.add_field(name="User", value=member.mention, inline=True)
                    bot_user = self.bot.user
                    assert isinstance(bot_user, discord.ClientUser)  # skipcq: BAN-B101
                    await self.webhook.send(username=bot_user.name, avatar_url=bot_user.display_avatar.url, embed=embed)
                    removable.append(i)
                elif member.is_timed_out():
                    self.timeouts.update({i: member.timed_out_until})
        for i in removable:
            self.timeouts.pop(i)

    @Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Process when a member joins the server and adds them to the members cache.

        Parameters
        ----------
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
        payload : discord.RawMemberRemoveEvent
            The payload of the member leaving the server
        """
        if payload.guild_id == 225345178955808768:
            user = payload.user
            if isinstance(user, discord.Member):
                _time = self.members.pop(user.id, user.joined_at) or utcnow() - timedelta(hours=1)
                time_string = time_string_from_seconds(abs(utcnow() - _time).total_seconds())
            elif isinstance(user, discord.User) and user.id in self.members:
                time_string = time_string_from_seconds(
                    abs(utcnow() - self.members.pop(user.id, utcnow() - timedelta(hours=1))).total_seconds()
                )
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
                    bot_user = self.bot.user
                    assert isinstance(bot_user, discord.ClientUser)  # skipcq: BAN-B101
                    await self.webhook.send(username=bot_user.name, avatar_url=bot_user.display_avatar.url, embed=embed)
                    self.timeouts.pop(after.id)
        except Exception:  # skipcq: PYL-W0703
            if after.is_timed_out():
                await self.parse_timeout(after)

    @Cog.listener()
    async def on_thread_create(self, thread: discord.Thread) -> None:
        """When a thread (post) is created in a forum channel, pin it.

        Parameters
        ----------
        thread : discord.Thread
            The thread that was created
        """
        if not isinstance(thread.parent, discord.ForumChannel):
            return

        message = thread.get_partial_message(thread.id)
        try:
            await message.pin()
        except discord.HTTPException:
            pass

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Listen for messages sent that the bot can see.

        If the message is sent by a non-mod user, it will check for a disallowed ping
        and will delete the message if it is found, and log it.
        Scans guild messages for sensitive content
        If the message is a dm, it logs it in the dm_logs channel and redirects them to the new mod support method.

        Parameters
        ----------
        message : discord.Message
            The message sent to the websocket from discord.
        """
        if message.content is None or message.author.bot:
            return
        if message.guild is None:
            channel = cast(
                discord.TextChannel,
                self.bot.get_channel(906578081496584242) or await self.bot.fetch_channel(906578081496584242),
            )
            mentions = discord.AllowedMentions(everyone=False, roles=False, users=False)
            await channel.send(message.author.mention, allowed_mentions=mentions)
            await channel.send(message.content, allowed_mentions=mentions)
            await message.channel.send(
                "Hi! If this was an attempt to reach the mod team through modmail,"
                " that has been removed, in favor of "
                "mod support, which you can find in <#398949472840712192>"
            )
            return
        if not await self.sensitive_scan(message):
            return
        author = cast(discord.Member, message.author)
          if all(
            role.id
            not in {
                338173415527677954,
                253752685357039617,
                225413350874546176,
                387037912782471179,
                406690402956083210,
                729368484211064944,
            }
            for role in author.roles
        ) and any(item in message.content for item in [f"<@&{message.guild.id}>", "@everyone", "@here"]):
            await author.add_roles(
                discord.Object(id=676250179929636886),
                discord.Object(id=684936661745795088),
            )
            try:
                await message.delete()
            except discord.DiscordException:  # pragma: no cover
                # if the message can't be deleted, ignore that and move on
                pass
            finally:
                embed = Embed(
                    description=message.content,
                    title="Mute: Everyone/Here Ping sent by non mod",
                    color=Color.red(),
                ).set_footer(
                    text=f"Sent by {message.author.display_name}-{message.author.id}",
                    icon_url=author.display_avatar.url,
                )
                bot_user = cast(discord.ClientUser, self.bot.user)
                await self.webhook.send(username=bot_user.name, avatar_url=bot_user.display_avatar.url, embed=embed)
                return
            if self.tilde_regex.search(message.content):
                await message.delete()
                return
            if self.extractor.has_urls(message.content) and not url_posting_allowed(
                cast(discord.TextChannel | discord.VoiceChannel | discord.Thread, message.channel), author.roles
            ):
            try:
                # if the url still isn't allowed, delete the message
                await message.delete()
            except discord.DiscordException:  # pragma: no cover
                # if the message can't be deleted, ignore that and move on
                pass
            finally:
                try:
                    await message.author.send(f"You need to be at least level 5 to post links in {message.guild.name}!")
                except discord.Forbidden:  # pragma: no cover
                    pass
                finally:
                    # at this point, all checks for bad messages have passed, and we can let the levels cog assess XP gain
                    levels_cog = cast("Leveling | None", self.bot.get_cog("Leveling"))  # pragma: no cover
                    if levels_cog is not None:  # pragma: no cover
                        await levels_cog.proc_xp(message)
                    return

async def setup(bot: CBot):
    """Load the event handler for the bot.

    Parameters
    ----------
    bot : CBot
        The bot to load the event handler for.
    """
    await bot.add_cog(Events(bot))
