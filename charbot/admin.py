"""Admin commands for charbot."""

import pathlib
from time import perf_counter
from typing import cast

import discord
from discord import PermissionOverwrite, Permissions
from discord.ext import commands

from . import CBot


class Admin(commands.Cog):
    """Admin Cog."""

    def __init__(self, bot: CBot):
        self.bot = bot
        self.settings: pathlib.Path = pathlib.Path(__file__).parent / "sensitive_settings.json"
        self.base_overrides = {}

    async def cog_load(self) -> None:  # pragma: no cover
        """Make sure the guild stuff is loaded."""
        guild = cast(
            discord.Guild, self.bot.get_guild(225345178955808768) or await self.bot.fetch_guild(225345178955808768)
        )
        self.base_overrides = {
            cast(discord.Role, guild.get_role(338173415527677954)): PermissionOverwrite.from_pair(
                Permissions(139586817088), Permissions.none()
            ),
            guild.default_role: PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False),
        }

    def cog_check(self, ctx: commands.Context) -> bool:
        """Check to make sure runner is a moderator.

        Parameters
        ----------
        self : Admin
            The Admin cog object.
        ctx : Context
            The context of the command.

        Returns
        -------
        bool
            True if the user is a moderator, False otherwise.

        Raises
        ------
        commands.CheckFailure
            If the user is not a moderator.
        """
        if ctx.guild is None:
            return False
        author = ctx.author
        assert isinstance(author, discord.Member)  # skipcq: BAN-B101
        return any(role.id in (338173415527677954, 253752685357039617, 225413350874546176) for role in author.roles)

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Ping Command TO Check Bot Is Alive.

        This command is used to check if the bot is alive.

        Parameters
        ----------
        self : Admin
            The Admin cog object.
        ctx : Context
            The context of the command.
        """
        start = perf_counter()
        await ctx.typing()
        end = perf_counter()
        typing = end - start
        start = perf_counter()
        await self.bot.pool.fetchrow("SELECT * FROM users WHERE id = $1", ctx.author.id)
        end = perf_counter()
        database = end - start
        start = perf_counter()
        message = await ctx.send("Ping ...")
        end = perf_counter()
        await message.edit(
            content=f"Pong!\n\nPing: {(end - start) * 100:.2f}ms\nTyping: {typing * 1000:.2f}ms\nDatabase: "
            f"{database * 1000:.2f}ms\nWebsocket: {self.bot.latency * 1000:.2f}ms"
        )


async def setup(bot: CBot):
    """Add the Admin cog to the bot.

    Parameters
    ----------
    bot : commands.Bot
        The bot object.
    """
    await bot.add_cog(Admin(bot))
