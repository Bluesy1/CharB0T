"""Charbot discord bot."""

import datetime
import logging
from typing import Any, ClassVar, Final, Self, TypeVar, cast
from zoneinfo import ZoneInfo

import asyncpg
import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import MISSING

from . import EXTENSIONS, Config, errors


_VT = TypeVar("_VT")


class Holder(dict[str, Any]):
    """Holder for data."""

    def __getitem__(self, k: Any) -> Any:
        """Get item."""
        return MISSING if k not in self else super().__getitem__(k)

    def __delitem__(self, key: Any) -> None:
        """Delete item."""
        if key not in self:
            return
        super().__delitem__(key)

    def pop(self, __key: Any, default: _VT = MISSING) -> _VT:
        """Pop item."""
        return default if __key not in self else super().pop(__key)

    def get(self, __key: Any, default: _VT = MISSING) -> _VT:
        """Get item."""
        return default if __key not in self else super().get(__key, default)

    def setdefault(self, __key: Any, default: _VT = MISSING) -> _VT:
        """Set default."""
        if __key not in self:
            self[__key] = default
        return self[__key]


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
        Whether the commands should be case-insensitive. Defaults to ``False``. This
        attribute does not carry over to groups. You must set it to every group if
        you require group commands to be case-insensitive as well.
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
    tree_cls: type[:class:`~discord.app_commands.CommandTree`]
        The type of application command tree to use. Defaults to :class:`~discord.app_commands.CommandTree`.
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
        """Return the current day reset time in the bot's timezone.

        Returns
        -------
        datetime.datetime
            The current day reset time in the bot's timezone.
        """
        return (
            datetime.datetime.now(cls.ZONEINFO).replace(microsecond=0, second=0, minute=0, hour=9)
            if datetime.datetime.now(cls.ZONEINFO).replace(microsecond=0, second=0, minute=0, hour=9)
            <= datetime.datetime.now(cls.ZONEINFO)
            else datetime.datetime.now(cls.ZONEINFO).replace(microsecond=0, second=0, minute=0, hour=9)
            - datetime.timedelta(days=1)
        )

    def __init__(
        self, *args: Any, strip_after_prefix: bool = True, tree_cls: type["Tree"], **kwargs: Any
    ) -> None:  # pragma: no cover
        super().__init__(*args, strip_after_prefix=strip_after_prefix, tree_cls=tree_cls, **kwargs)
        self.pool: asyncpg.Pool = MISSING
        self.program_logs: discord.Webhook = MISSING
        self.error_logs: discord.Webhook = MISSING
        self.holder: Holder = Holder()
        self.no_dms: set[int] = set()

    async def setup_hook(self):  # pragma: no cover
        """Initialize hook for the bot.

        This is called when the bot is logged in but before connecting to the websocket.
        It provides an opportunity to perform some initialization before the websocket is connected.
        Also loads the cogs, and prints who the bot is logged in as
        """
        print("Setup started")
        webhooks = Config["discord"]["webhooks"]
        self.program_logs = await self.fetch_webhook(webhooks["program_logs"])
        self.error_logs = await self.fetch_webhook(webhooks["error"])
        print("Webhooks Fetched")
        await self.load_extension("jishaku")
        for extension in EXTENSIONS:
            await self.load_extension(extension)
        print("Extensions loaded")
        print(f"Logged in: {self.user}")

    async def give_game_points(self, member: discord.Member | discord.User, points: int, bonus: int = 0) -> int:
        """Give the user points.

        Parameters
        ----------
        member: discord.Member
            The member to give points to.
        points : int
            The amount of points to give.
        bonus : int, optional
            The amount of points to add to the user's total points.

        Returns
        -------
        gained: int
            The points gained
        """
        user = await self.pool.fetchrow(
            "SELECT users.id as id, points, dp.last_claim as daily, dp.last_particip_dt as "
            "particip_dt, dp.particip as particip, dp.won as won "
            "FROM users JOIN daily_points dp on users.id = dp.id WHERE users.id = $1",
            member.id,
        )
        if user is None:
            return await self.first_time_game_gain(member.id, points, bonus)
        if user["particip_dt"] < self.TIME():
            return await self.first_of_day_game_gain(member.id, points, bonus)
        if user["particip_dt"] == self.TIME():
            return await self.fallback_game_gain(member.id, user["particip"], points, bonus)
        return 0

    async def fallback_game_gain(self, user: int, previous: int, points: int, bonus: int, /) -> int:
        """Fallback game gain.

        Parameters
        ----------
        user : int
            The user ID to give points to.
        previous: int
            The user's previous amount of participation points.
        points : int
            The amount of points to give.
        bonus : int
            The amount of bonus points to give.

        Returns
        -------
        gained: int
            The amount of points gained.
        """
        if previous + points > 10:  # pragma: no branch
            real_points = 10 - previous
            bonus = -(-(real_points * bonus) // points)
            points = real_points
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE daily_points SET particip = particip + $1, won = won + $2 WHERE id = $3",
                points,
                bonus,
                user,
            )
            await conn.execute("UPDATE users SET points = points + $1 WHERE id = $2", points + bonus, user)
        return points + bonus

    async def first_of_day_game_gain(self, user: int, points: int, bonus: int, /) -> int:
        """Give the user points for the first time of the day.

        Parameters
        ----------
        user : int
            The user to give points to.
        points : int
            The amount of points to give.
        bonus : int
            The amount of bonus points to give.

        Returns
        -------
        gained: int
            The points gained.
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE daily_points SET last_particip_dt = $1, particip = $2, won = $3 WHERE id = $4",
                self.TIME(),
                points,
                bonus,
                user,
            )
            await conn.execute("UPDATE users SET points = points + $1 WHERE id = $2", points + bonus, user)
        return points + bonus

    async def first_time_game_gain(self, user: int, points: int, bonus: int, /) -> int:
        """Give the user points for the first time.

        Parameters
        ----------
        user : int
            The user id to give points to.
        points : int
            The amount of points to give.
        bonus : int
            The amount of bonus points to give.

        Returns
        -------
        gained: int
            The points gained
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO users (id, points) VALUES ($1, $2)",
                user,
                points + bonus,
            )
            await conn.execute(
                "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won)"
                " VALUES ($1, $2, $3, $4, $5)",
                user,
                self.TIME() - datetime.timedelta(days=1),
                self.TIME(),
                points,
                bonus,
            )
            return points + bonus

    # for some reason deepsource doesn't like this, so i'm skipcq'ing the definition header
    async def on_command_error(
        self, ctx: commands.Context[Self], exception: commands.CommandError, /
    ) -> None:  # skipcq: PYL-W0221  # pragma: no cover
        """Event triggered when an error is raised while invoking a command.

        Parameters
        ----------
        ctx: commands.Context
            The context used for command invocation.
        exception: commands.CommandError
            The Exception raised.
        """
        if isinstance(exception, commands.CommandNotFound):
            return  # We want to return immediately because ctx.command won't exist if the command is not found
        command = ctx.command
        assert isinstance(command, commands.Command)  # skipcq: BAN-B101
        if hasattr(ctx.command, "on_error"):
            return  # Don't mess with local overrides

        cog = ctx.cog
        if cog is not None and cog._get_overridden_method(cog.cog_command_error) is not None:  # skipcq: PYL-W0212
            return  # Local cog overrides take precedence

        ignored = (commands.CommandNotFound,)

        # Discord.py wraps exceptions that are not inherited from CommandInvokeError in a CommandInvokeError for type
        # safety. We want to catch the actual exception, not the wrapped one.
        exception = getattr(exception, "original", exception)

        # if the exception is one to ignore, we don't want to do anything
        if isinstance(exception, ignored):
            return

        # if owner only, or missing perms/roles we want to say missing permissions
        elif isinstance(
            exception, (commands.NotOwner, commands.MissingAnyRole, commands.MissingRole, commands.MissingPermissions)
        ):
            if cast(commands.Command, ctx.command).name == "calendar":
                return
            await ctx.send(f"You are missing permissions to use {command.name}")

        # if the command is disabled, we want to tell the user that
        if isinstance(exception, commands.DisabledCommand):
            await ctx.send(f"{command.name} is disabled.")

        # if the command is guild only and the user is not in a guild, we want to tell the user that
        elif isinstance(exception, commands.NoPrivateMessage):
            if ctx.author.id not in self.no_dms:
                try:
                    await ctx.author.send(f"{command.name} can only be used in a guild.")
                except discord.HTTPException:
                    self.no_dms.add(ctx.author.id)
                    # user has DMs off or blocked the bot, don't try to DM them anymore

        # if the argument(s) are invalid, we want to tell the user that
        elif isinstance(exception, commands.BadArgument):
            await ctx.send(f"Bad argument for command {command.name}.")

        else:
            await ctx.send(f"An error occurred while running {command.name}, Bluesy has been notified.")
            # All other Errors not returned come here. And we can just print the default TraceBack.
            await self.error_logs.send(f"{command.name} raised an error: {exception}")
            logging.getLogger("charbot.commands").error("Ignoring exception in command %s", command, exc_info=exception)

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
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
        logging.getLogger("charbot").exception("Ignoring exception in %s", event_method)


class Tree(app_commands.CommandTree[CBot]):
    """Command tree for charbot."""

    def __init__(self, bot: CBot):  # pragma: no cover
        """Initialize the command tree."""
        super().__init__(client=bot)
        self.client: CBot = bot
        self.logger = logging.getLogger("charbot.tree")

    async def on_error(
        self, interaction: discord.Interaction[CBot], error: app_commands.AppCommandError
    ) -> None:  # pragma: no cover
        """Event triggered when an error is raised while invoking a command.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction that raised the error.

        error: discord.app_commands.AppCommandError
            The Exception raised.
        """
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        command = interaction.command
        if isinstance(command, (app_commands.Command, app_commands.ContextMenu)):
            user = interaction.user.mention
            _command = command.qualified_name
            if isinstance(error, (errors.MissingProgramRole, errors.WrongChannelError)):
                message = error.message
            elif isinstance(error, app_commands.MissingAnyRole):
                message = f"{user}, you don't have any of the required role(s) to use {command}"
            elif isinstance(error, app_commands.NoPrivateMessage):
                message = error.args[0]
            elif isinstance(error, app_commands.CommandOnCooldown):
                after = discord.utils.format_dt(discord.utils.utcnow() + datetime.timedelta(seconds=error.retry_after))
                message = (
                    f"{user}, this command is on cooldown for "
                    + f"{error.retry_after:.2f} seconds you can retry after {after}"
                )
            elif isinstance(error, app_commands.CheckFailure):
                message = f"{user}, you can't use {_command}"
            elif isinstance(error, app_commands.CommandInvokeError):
                message = f"{user}, an error occurred while executing {_command}, Bluesy has been notified."
                self.logger.error("Ignoring exception in command %r", command.name, exc_info=error)
            else:
                message = "An error occurred while executing the command."
            await interaction.followup.send(message, ephemeral=True)
        else:
            await self.client.error_logs.send(f"Ignoring exception in command tree: {error}")
            self.logger.error("Ignoring exception in command tree", exc_info=error)
