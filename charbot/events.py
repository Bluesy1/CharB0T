"""Event handling for Charbot."""

import re
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, cast

import discord
from discord import Color, ui
from discord.ext import tasks
from discord.ext.commands import Cog
from discord.utils import format_dt, utcnow
from urlextract import URLExtract

from . import CBot, constants


if TYPE_CHECKING:  # pragma: no cover
    from .levels import Leveling


class UnTimeoutView(ui.LayoutView):
    def __init__(self, member: discord.Member, at: datetime | None = None) -> None:
        super().__init__()
        self.add_item(
            ui.Container(
                ui.TextDisplay(f"## [UNTIMEOUT] {member}"),  # cspell: disable-line
                ui.TextDisplay(f"### User\n{member.mention}"),
                ui.TextDisplay(f"### Ended\n{format_dt(at or utcnow())}"),
                ui.Separator(),
                ui.TextDisplay(f"-# \n{member.id}"),
                accent_color=Color.green(),
            )
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
        and channel.parent_id == constants.GAMES_FORUM_ID
        and (
            any(tag.id == constants.GAME_SUGGESTIONS_TAG_ID for tag in channel.applied_tags)
            or channel.message_count < 2
            or channel.id == channel.last_message_id
            or channel.id == getattr(channel.starter_message, "id", None)
        )
    ):
        # if the parent is this, then the channel is the games channel and if the channel has the
        # suggestions tag, then it's a game thread, and we want to allow urls in it
        # OR the message is the starter message for a thread in the channel, and we want to allow it
        return True
    if channel.category_id in constants.SPECIAL_CATEGORIES:
        # if the channel is in an admin or info category, we want to allow urls
        return True
    if channel.id in constants.LINK_ALLOWED_CHANNELS:
        # the channel is allowed to have links, but they may not embed
        return True
    # If so far the url hasn't been allowed, test if the author has a role that allows it
    return any(role.id in constants.LINK_ALLOWED_ROLES for role in roles)


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
    """

    __slots__ = (
        "bot",
        "timeouts",
        "members",
        "webhook",
        "tilde_regex",
        "extractor",
    )

    def __init__(self, bot: CBot):
        self.bot = bot
        self.timeouts: dict[int, datetime] = {}
        self.members: dict[int, datetime] = {}
        self.tilde_regex = re.compile(
            r"~~:\.\|:;~~|tilde tilde colon dot vertical bar colon semicolon tilde tilde", re.MULTILINE | re.IGNORECASE
        )
        self.extractor = URLExtract()

    async def cog_load(self) -> None:  # pragma: no cover
        """Cog load function.

        This is called when the cog is loaded, and initializes the
        log_un-timeout task and the members cache
        """
        self.webhook = await self.bot.fetch_webhook(945514428047167578)
        self.log_untimeout.start()
        self.members.update(
            {
                user.id: user.joined_at
                async for user in cast(
                    discord.Guild,
                    self.bot.get_guild(constants.GUILD_ID) or await self.bot.fetch_guild(constants.GUILD_ID),
                ).fetch_members(limit=None)
                if user.joined_at is not None
            }
        )

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236  # pragma: no cover
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
        until = cast(datetime, after.timed_out_until)
        time_delta = until + timedelta(seconds=1) - utcnow()
        time_string = ""
        if time_delta.days // 7 != 0:  # pragma: no branch
            time_string += f"{time_delta.days // 7} Week{'s' if time_delta.days // 7 > 1 else ''}"
        if time_delta.days % 7 != 0:  # pragma: no branch
            time_string += f"{', ' if bool(time_string) else ''}{time_delta.days % 7} Day(s) "
        if time_delta.seconds // 3600 > 0:  # pragma: no branch
            time_string += f"{', ' if bool(time_string) else ''}{time_delta.seconds // 3600} Hour(s) "
        if (time_delta.seconds % 3600) // 60 != 0:  # pragma: no branch
            time_string += f"{', ' if bool(time_string) else ''}{(time_delta.seconds % 3600) // 60} Minute(s) "
        if (time_delta.seconds % 3600) % 60 != 0:  # pragma: no branch
            time_string += f"{', ' if bool(time_string) else ''}{(time_delta.seconds % 3600) % 60} Second(s) "
        view = ui.LayoutView()
        view.add_item(
            ui.Container(
                ui.TextDisplay(f"## [TIMEOUT] {after}"),
                ui.TextDisplay(f"### User\n{after.mention}"),
                ui.TextDisplay(f"### Duration\n{time_string}"),
                ui.TextDisplay(f"### Until\n{format_dt(until)}"),
                ui.Separator(),
                ui.TextDisplay(f"-# \n{after.id}"),
                accent_color=Color.red(),
            )
        )
        bot = self.bot.user
        await self.webhook.send(view=view, username=bot.name, avatar_url=bot.display_avatar.url)
        self.timeouts.update({after.id: until})

    @tasks.loop(seconds=30)
    async def log_untimeout(self) -> None:  # pragma: no cover
        """Un-timeout Report Task.

        This task runs every 30 seconds and checks if any users that have been timed out have had their timeouts
        expired. If they have, it will send a message to the mod channel.
        """
        removable = []
        for i, j in self.timeouts.copy().items():
            if j < datetime.now(tz=UTC):
                guild = self.bot.get_guild(constants.GUILD_ID)
                if guild is None:
                    guild = await self.bot.fetch_guild(constants.GUILD_ID)
                member = await guild.fetch_member(i)
                if not member.is_timed_out():
                    bot = self.bot.user
                    await self.webhook.send(
                        view=UnTimeoutView(member, j), username=bot.name, avatar_url=bot.display_avatar.url
                    )
                    removable.append(i)
                elif member.is_timed_out():
                    self.timeouts.update({i: cast(datetime, member.timed_out_until)})
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
        if member.guild.id == constants.GUILD_ID:  # pragma: no branch
            self.members.update({member.id: utcnow()})

    @Cog.listener()
    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent) -> None:  # pragma: no cover
        """Process when a member leaves the server and removes them from the members cache.

        Parameters
        ----------
        payload : discord.RawMemberRemoveEvent
            The payload of the member leaving the server
        """
        if payload.guild_id == constants.GUILD_ID:
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
            channel = cast(
                discord.TextChannel,
                self.bot.get_channel(430197357100138497) or await self.bot.fetch_channel(430197357100138497),
            )
            await channel.send(f"**{user}** has left the server. ID:{user.id}. Time on Server: {time_string}")

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
        try:  # pragma: no cover
            if after.timed_out_until != before.timed_out_until:
                if after.is_timed_out():
                    await self.parse_timeout(after)
                else:
                    bot = self.bot.user
                    await self.webhook.send(
                        view=UnTimeoutView(after), username=bot.name, avatar_url=bot.display_avatar.url
                    )
                    self.timeouts.pop(after.id)
        except Exception:  # skipcq: PYL-W0703  # pragma: no cover
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
        if not isinstance(thread.parent, discord.ForumChannel):  # pragma: no cover
            return

        message = thread.get_partial_message(thread.id)
        try:
            await message.pin()
            msg = await message.fetch()
            if (
                thread.parent_id == constants.GAMES_FORUM_ID
                and any(tag.id == constants.GAME_SUGGESTIONS_TAG_ID for tag in thread.applied_tags)
                and not self.extractor.has_urls(msg.content)
            ):  # pragma: no cover
                # If the parent is this, then the channel is the games channel and if the thread has the
                #  suggestions tag, then it's a game thread, and if it doesn't have a url in the first message
                #  we want to remind them to add one
                await thread.send(
                    f"Hi <@{msg.author.id}>, thanks for your suggestion, unfortunately, "
                    "it appears you didn't add a link to a game suggestion! "
                    "Please edit your initial post to include a link, or send a new message with a link, thanks!"
                    "\n*This is an automated message, please ignore if it was sent in error.*"
                )
        except discord.HTTPException:  # pragma: no cover
            # We don't care about the exception, we just don't want this error to propagate, because it can be caused
            # by a known race condition between on_thread_create and message_create, depending on which gets sent first
            # by the gateway.
            pass

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Listen for messages sent that the bot can see.

        If the message is sent by a non-mod user, it will check for a disallowed ping
        and will delete the message if it is found, and log it.
        Scans guild messages for prohibited content
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
            mentions = discord.AllowedMentions.none()
            await channel.send(message.author.mention, allowed_mentions=mentions)
            view = ui.LayoutView()
            if message.content:
                view.add_item(ui.Container(ui.TextDisplay(f"```md\n{message.content[:3950]}\n```")))
            else:  # pragma: no cover
                view.add_item(ui.Container(ui.TextDisplay(f"Message Contained no text Content:```\n{message!r}\n```")))
            await channel.send(view=view, allowed_mentions=mentions)
            await message.channel.send(
                "Hi! If this was an attempt to reach the mod team through modmail,"
                " that has been removed, in favor of "
                "mod support, which you can find in <#398949472840712192>"
            )
            return
        author = cast(discord.Member, message.author)
        if all(role.id not in constants.EVERYONE_PING_ALLOWED_ROLES for role in author.roles) and any(
            item in message.content for item in [f"<@&{message.guild.id}>", "@everyone", "@here"]
        ):
            try:
                await message.delete()
            finally:
                await author.add_roles(
                    discord.Object(id=676250179929636886),
                    discord.Object(id=684936661745795088),
                )
                view = ui.LayoutView()
                view.add_item(
                    ui.Container(
                        ui.TextDisplay("## Mute: Everyone/Here Ping sent by non mod"),
                        ui.TextDisplay(f"```md\n{message.content[:3950]}\n```"),
                        ui.Separator(),
                        ui.TextDisplay(f"-# Sent by {message.author.display_name}-{message.author.id}"),
                        accent_color=Color.red(),
                    )
                )
                bot = self.bot.user
                await self.webhook.send(view=view, username=bot.name, avatar_url=bot.display_avatar.url)
                return  # skipcq: PYL-W0150
        if self.tilde_regex.search(message.content):  # pragma: no cover
            await message.delete()
            return
        if any(
            "discord.com/channels/225345178955808768" not in url for url in self.extractor.gen_urls(message.content)
        ) and not url_posting_allowed(
            cast(discord.TextChannel | discord.VoiceChannel | discord.Thread, message.channel), author.roles
        ):
            try:
                # if the url still isn't allowed, delete the message
                await message.delete()
            finally:
                try:
                    await message.author.send(f"You need to be at least level 2 to post links in {message.guild.name}!")
                finally:
                    return  # skipcq: PYL-W0150
        # at this point, all checks for bad messages have passed, and we can let the levels cog assess XP gain
        levels_cog = cast("Leveling | None", self.bot.get_cog("Leveling"))  # pragma: no cover
        if levels_cog is not None:  # pragma: no cover
            await levels_cog.proc_xp(message)


async def setup(bot: CBot):  # pragma: no cover
    """Load the event handler for the bot.

    Parameters
    ----------
    bot : CBot
        The bot to load the event handler for.
    """
    await bot.add_cog(Events(bot))
