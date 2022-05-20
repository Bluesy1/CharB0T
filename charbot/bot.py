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
"""Charbot discord bot."""
import datetime
import os
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, ClassVar, Final, Type
from zoneinfo import ZoneInfo

import asyncpg
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import CommandError
from discord.utils import MISSING

from . import errors


class CBot(commands.Bot):
    """Custom bot class. extends discord.ext.commands.Bot.

    This class is used to create the bot instance.

    Parameters
    ----------
    command_prefix
        The command prefix is what the message content must contain initially
        to have a command invoked. This prefix could either be a string to
        indicate what the prefix should be, or a callable that takes in the bot
        as its first parameter and :class:`discord.Message` as its second
        parameter and returns the prefix. This is to facilitate "dynamic"
        command prefixes. This callable can be either a regular function or
        a coroutine.

        An empty string as the prefix always matches, enabling prefix-less
        command invocation. While this may be useful in DMs it should be avoided
        in servers, as it's likely to cause performance issues and unintended
        command invocations.

        The command prefix could also be an iterable of strings indicating that
        multiple checks for the prefix should be used and the first one to
        match will be the invocation prefix. You can get this prefix via
        :attr:`.Context.prefix`.

        .. note::

            When passing multiple prefixes be careful to not pass a prefix
            that matches a longer prefix occurring later in the sequence.  For
            example, if the command prefix is ``('!', '!?')``  the ``'!?'``
            prefix will never be matched to any message as the previous one
            matches messages starting with ``!?``. This is especially important
            when passing an empty string, it should always be last as no prefix
            after it will be matched.
    case_insensitive: :class:`bool`
        Whether the commands should be case insensitive. Defaults to ``False``. This
        attribute does not carry over to groups. You must set it to every group if
        you require group commands to be case insensitive as well.
    description: :class:`str`
        The content prefixed into the default help message.
    help_command: Optional[:class:`.HelpCommand`]
        The help command implementation to use. This can be dynamically
        set at runtime. To remove the help command pass ``None``. For more
        information on implementing a help command, see :ref:`ext_commands_help_command`.
    owner_id: Optional[:class:`int`]
        The user ID that owns the bot. If this is not set and is then queried via
        :meth:`.is_owner` then it is fetched automatically using
        :meth:`~.Bot.application_info`.
    owner_ids: Optional[Collection[:class:`int`]]
        The user IDs that owns the bot. This is similar to :attr:`owner_id`.
        If this is not set and the application is team based, then it is
        fetched automatically using :meth:`~.Bot.application_info`.
        For performance reasons it is recommended to use a :class:`set`
        for the collection. You cannot set both ``owner_id`` and ``owner_ids``.
    strip_after_prefix: :class:`bool`
        Whether to strip whitespace characters after encountering the command
        prefix. This allows for ``!   hello`` and ``!hello`` to both work if
        the ``command_prefix`` is set to ``!``. Defaults to ``False``.
    tree_cls: Type[:class:`~discord.app_commands.CommandTree`]
        The type of application command tree to use. Defaults to :class:`~discord.app_commands.CommandTree`.

    Attributes
    ----------
    executor : ThreadPoolExecutor
        The executor used to run IO tasks in the background, must be set after opening bot in an async manager,
         before connecting to the websocket.
    process_pool : ProcessPoolExecutor
        The executor used to run CPU tasks in the background, must be set after opening bot in an async manager,
         before connecting to the websocket.
    pool : asyncpg.Pool
        The connection pool to the database.
    program_logs : discord.Webhook
        The webhook to send program logs to.
    """

    ZONEINFO: ClassVar[ZoneInfo] = ZoneInfo("America/Detroit")
    ALLOWED_ROLES: Final[list[int | str]] = [
        337743478190637077,
        685331877057658888,
        969629622453039104,
        969629628249563166,
        969629632028614699,
        969628342733119518,
        969627321239760967,
        969626979353632790,
    ]
    CHANNEL_ID: ClassVar[int] = 969972085445238784

    @classmethod
    def TIME(cls) -> datetime.datetime:
        """Return the current giveaway time in the bot's timezone.

        Returns
        -------
        datetime.datetime
            The current giveaway time in the bot's timezone.
        """
        return (
            datetime.datetime.now(cls.ZONEINFO).replace(microsecond=0, second=0, minute=0, hour=9)
            if datetime.datetime.now(cls.ZONEINFO).replace(microsecond=0, second=0, minute=0, hour=9)
            <= datetime.datetime.now(cls.ZONEINFO)
            else datetime.datetime.now(cls.ZONEINFO).replace(microsecond=0, second=0, minute=0, hour=9)
            - datetime.timedelta(days=1)
        )  # noqa: E731

    def __init__(self, *args, strip_after_prefix: bool = True, tree_cls: Type[app_commands.CommandTree], **kwargs):
        super().__init__(*args, strip_after_prefix=strip_after_prefix, tree_cls=tree_cls, **kwargs)
        self.executor: ThreadPoolExecutor = MISSING
        self.process_pool: ProcessPoolExecutor = MISSING
        self.pool: asyncpg.Pool = MISSING
        self.program_logs: discord.Webhook = MISSING
        self.error_logs: discord.Webhook = MISSING
        self.giveaway_webhook: discord.Webhook = MISSING

    async def setup_hook(self):
        """Initialize hook for the bot.

        This is called when the bot is logged in but before connecting to the websocket.
        It provides an opportunity to perform some initialisation before the websocket is connected.
        Also loads the cogs, and prints who the bot is logged in as
        """
        print("Setup started")
        log_webhook = os.getenv("LOG_WEBHOOK")
        error_webhook = os.getenv("ERROR_WEBHOOK")
        giveaway_webhook = os.getenv("GIVEAWAY_WEBHOOK")
        assert isinstance(log_webhook, str)  # skipcq: BAN-B101
        assert isinstance(error_webhook, str)  # skipcq: BAN-B101
        assert isinstance(giveaway_webhook, str)  # skipcq: BAN-B101
        self.program_logs = await self.fetch_webhook(int(log_webhook))
        self.error_logs = await self.fetch_webhook(int(error_webhook))
        self.giveaway_webhook = await self.fetch_webhook(int(giveaway_webhook))
        print("Webhooks loaded")
        await self.load_extension("jishaku")
        await self.load_extension("admin")
        await self.load_extension("dice")
        await self.load_extension("events")
        await self.load_extension("gcal")
        await self.load_extension("giveaway")
        await self.load_extension("mod_support")
        await self.load_extension("query")
        await self.load_extension("shrugman")
        await self.load_extension("sudoku")
        await self.load_extension("tictactoe")
        print("Extensions loaded")
        user = self.user
        assert isinstance(user, discord.ClientUser)  # skipcq: BAN-B101
        print(f"Logged in: {user.name}#{user.discriminator}")

    async def giveaway_user(self, user: int) -> None | asyncpg.Record:
        """Return an asyncpg entry for the user, joined on all 3 tables for tthe giveaway.

        Parameters
        ----------
        user : int
            The user id.

        Returns
        -------
        asyncpg.Record, optional
            The user record, or None if the user isn't in the DB.
        """
        return await self.pool.fetchrow(
            "SELECT users.id as id, points, b.bid as bid, dp.last_claim as daily, dp.last_particip_dt as "
            "particip_dt, dp.particip as particip, dp.won as won "
            "FROM users join bids b on users.id = b.id join daily_points dp on users.id = dp.id WHERE users.id = $1",
            user,
        )

    async def give_game_points(
        self, member: discord.Member | discord.User, game: str, points: int, bonus: int = 0
    ) -> int:
        """Give the user points.

        Parameters
        ----------
        member: discord.Member
            The member to give points to.
        game: str
            The game/program that was played.
        points : int
            The amount of points to give.
        bonus : int, optional
            The amount of points to add to the user's total points.

        Returns
        -------
        int
            The points gained
        """
        user_id = member.id
        clientuser = self.user
        assert isinstance(clientuser, discord.ClientUser)  # skipcq: BAN-B101
        user = await self.giveaway_user(user_id)
        if user is None:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO users (id, points) VALUES ($1, $2)",
                    user_id,
                    points + bonus,
                )
                await conn.execute("INSERT INTO bids (id, bid) VALUES ($1, 0)", user_id)
                await conn.execute(
                    "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won)"
                    " VALUES ($1, $2, $3, $4, $5)",
                    user_id,
                    self.TIME() - datetime.timedelta(days=1),
                    self.TIME(),
                    points,
                    bonus,
                )
                await conn.execute("INSERT INTO bids (id, bid) VALUES ($1, 0)", user_id)
                await self.program_logs.send(
                    f"[NEW PARTICIPANT] {member.mention} gained {points + bonus} points for"
                    f" {game}, as {points} participated and {bonus} bonus points.",
                    username=clientuser.name,
                    avatar_url=clientuser.display_avatar.url,
                    allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False),
                )
                return points + bonus
        elif user["particip_dt"] < self.TIME():
            async with self.pool.acquire() as conn:
                await conn.execute(
                    "UPDATE daily_points SET last_particip_dt = $1, particip = $2, won = $3 WHERE id = $4",
                    self.TIME(),
                    points,
                    bonus,
                    user_id,
                )
                await conn.execute("UPDATE users SET points = points + $1 WHERE id = $2", points + bonus, user_id)
                await self.program_logs.send(
                    f"[FIRST OF DAY] {member.mention} gained {points + bonus} points for"
                    f" {game}, as {points} participated and {bonus} bonus points.",
                    username=clientuser.name,
                    avatar_url=clientuser.display_avatar.url,
                    allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False),
                )
        elif user["particip_dt"] == self.TIME():
            _points: int = MISSING
            _bonus: int = MISSING
            if user["particip"] + points > 10:
                real_points = 10 - user["particip"]
                _bonus = bonus
                _points = points
                bonus = -(-(real_points * bonus) // points)
                points = real_points
            async with self.pool.acquire() as conn:
                await conn.execute(
                    "UPDATE daily_points SET particip = particip + $1, won = won + $2 WHERE id = $3",
                    points,
                    bonus,
                    user_id,
                )
                await conn.execute("UPDATE users SET points = points + $1 WHERE id = $2", points + bonus, user_id)
                extra = (
                    f" out of a possible {_points + _bonus} points as {_points} participation and {_bonus} bonus points"
                    if _points is not MISSING
                    else ""
                )
                await self.program_logs.send(
                    f"{'[HIT CAP] ' if _points is not MISSING else ''}{member.mention} gained {points + bonus} points"
                    f" for {game}, as {points} participated and {bonus} bonus points"
                    f"{extra}.",
                    username=clientuser.name,
                    avatar_url=clientuser.display_avatar.url,
                    allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False),
                )
        else:
            await self.program_logs.send(
                f"[ERROR] {member.mention} gained 0 instead of {points + bonus} points for"
                f" {game}, as {points} participated and {bonus} bonus points because something went wrong.",
                username=clientuser.name,
                avatar_url=clientuser.display_avatar.url,
                allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False),
            )
            return 0
        return points + bonus

    # for some reason deepsource doesn't like this, so i'm skipcq'ing the definition header
    async def on_command_error(self, ctx: commands.Context, exception: CommandError, /) -> None:  # skipcq: PYL-W0221
        """Event triggered when an error is raised while invoking a command.

        Parameters
        ----------
        ctx: commands.Context
            The context used for command invocation.
        exception: commands.CommandError
            The Exception raised.
        """
        command = ctx.command
        assert isinstance(command, commands.Command)  # skipcq: BAN-B101
        if hasattr(ctx.command, "on_error"):
            return  # Don't mess with local overrides

        cog = ctx.cog
        # noinspection PyProtectedMember
        if cog is not None and cog._get_overridden_method(cog.cog_command_error) is not None:  # skipcq: PYL-W0212
            return  # Local cog overrides take precedence

        ignored = (commands.CommandNotFound,)

        # Discordpy wraps exceptuions that are not inherited from CommandInvokeError in a CommandInvokeError for type
        # safety. We want to catch the actual exception, not the wrapped one.
        exception = getattr(exception, "original", exception)

        # if the exception is one to ignore, we don't want to do anything
        if isinstance(exception, ignored):
            return

        # if the command is disabled, we want to tell the user that
        if isinstance(exception, commands.DisabledCommand):
            await ctx.send(f"{command.name} is disabled.")

        # if the command is guild only and the user is not in a guild, we want to tell the user that
        elif isinstance(exception, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f"{command.name} can only be used in a guild.")
            except discord.HTTPException:
                pass  # user has DMs off or blocked the bot

        # if the argument(s) are invalid, we want to tell the user that
        elif isinstance(exception, commands.BadArgument):
            await ctx.send(f"Bad argument for command {command.name}.")

        else:
            await ctx.send(f"An error occurred while running {command.name}.")
            # All other Errors not returned come here. And we can just print the default TraceBack.
            await self.error_logs.send(f"{command.name} raised an error: {exception}")
            print("Ignoring exception in command {}:".format(command), file=sys.stderr)
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        """Event triggered when an error is raised.

        Parameters
        ----------
        event_method: str
            The name of the event that raised the error.
        args: Any
            The arguments passed to the event.
        kwargs: Any
            The keyword arguments passed to the event.
        """
        await self.error_logs.send(f"{event_method} raised an error: {args} {kwargs}")
        print(f"Ignoring exception in {event_method}", file=sys.stderr)
        traceback.print_exc()


class Tree(app_commands.CommandTree):
    """Command tree for charbot."""

    def __init__(self, bot: CBot):
        """Initialize the command tree."""
        super().__init__(client=bot)
        self.client: CBot = bot

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        """Event triggered when an error is raised while invoking a command.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction that raised the error.

        error: discord.app_commands.AppCommandError
            The Exception raised.
        """
        command = interaction.command
        if isinstance(command, (app_commands.Command, app_commands.ContextMenu)):
            if isinstance(error, errors.MissingProgramRole):
                if interaction.response.is_done():
                    await interaction.followup.send(error.message)
                else:
                    await interaction.response.send_message(error.message, ephemeral=True)
            if isinstance(error, app_commands.MissingAnyRole):
                if interaction.response.is_done():
                    await interaction.followup.send(
                        f"{interaction.user.mention}, you don't have any of the required role(s) to use {command.name}."
                    )
                else:
                    await interaction.response.send_message(
                        f"{interaction.user.mention}, you don't have any of the required role(s) to use "
                        f"{command.name}.",
                        ephemeral=True,
                    )
            elif isinstance(error, errors.WrongChannelError):
                if interaction.response.is_done():
                    await interaction.followup.send(f"{interaction.user.mention}, {error}")
                else:
                    await interaction.response.send_message(f"{interaction.user.mention}, {error}", ephemeral=True)
            elif isinstance(error, app_commands.NoPrivateMessage):
                if interaction.response.is_done():
                    await interaction.followup.send(error.args[0])
                else:
                    await interaction.response.send_message(error.args[0], ephemeral=True)
            elif isinstance(error, app_commands.CheckFailure):
                if interaction.response.is_done():
                    await interaction.followup.send(f"{interaction.user.mention}, you can't use {command.name}.")
                else:
                    await interaction.response.send_message(
                        f"{interaction.user.mention}, you can't use {command.name}.", ephemeral=True
                    )
            elif isinstance(error, app_commands.CommandInvokeError):
                orig_error = error.original or error
                if interaction.response.is_done():
                    await interaction.followup.send(
                        f"{interaction.user.mention}, an error occurred while executing {command.name}"
                        f", Bluesy has been notified."
                    )
                else:
                    await interaction.response.send_message(
                        f"{interaction.user.mention}, an error occurred while executing {command.name}"
                        f", Bluesy has been notified.",
                        ephemeral=True,
                    )
                await self.client.error_logs.send(
                    f"{interaction.user.mention} tried to execute command {command.name!r} but an error "
                    f"occurred:\n{orig_error}"
                )
                print(f"Ignoring exception in command {command.name!r}", file=sys.stderr)
                traceback.print_exception(orig_error.__class__, orig_error, orig_error.__traceback__, file=sys.stderr)
        else:
            print(f"Ignoring exception in command tree: {error}", file=sys.stderr)
            await self.client.error_logs.send(f"Ignoring exception in command tree: {error}")
            traceback.print_exception(error.__class__, error, error.__traceback__, file=sys.stderr)
