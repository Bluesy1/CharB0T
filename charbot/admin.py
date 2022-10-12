# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT
"""Admin commands for charbot."""
import pathlib
from datetime import datetime, timezone
from time import perf_counter

import discord
import orjson
from discord import Color, Embed, app_commands
from discord.ext import commands

from . import CBot, GuildInteraction


class Admin(commands.Cog):
    """Admin Cog."""

    def __init__(self, bot: CBot):
        self.bot = bot
        self.settings: pathlib.Path = pathlib.Path(__file__).parent / "sensitive_settings.json"

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

    @commands.hybrid_group(name="sensitive")
    @app_commands.guild_only()
    async def sensitive(self, ctx: commands.Context):
        """Command group for configuring the sensitive words filter.

        Parameters
        ----------
        self : Admin
            The Admin cog object.
        ctx : Context
            The context of the command.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(
                "Invoked Sensitive words group - use `add` to add a word, `remove`"
                " to remove a word, or `query` to get all words on the list."
            )

    @sensitive.command(name="add")
    async def add(self, ctx: commands.Context, *, word: str):
        """Add a word to the sensitive words filter.

        Parameters
        ----------
        self : Admin
            The Admin cog object.
        ctx : Context
            The context of the command.
        word : str
            The word to add to the filter.
        """
        with open(self.settings, "rb") as json_dict:
            fulldict = orjson.loads(json_dict.read())
        if word.lower() not in fulldict["words"]:
            fulldict["words"].append(word.lower())
            fulldict["words"].sort()
            with open(self.settings, "wb") as json_dict:
                json_dict.write(orjson.dumps(fulldict))
            await ctx.send(
                embed=Embed(
                    title="New list of words defined as sensitive",
                    description=", ".join(fulldict["words"]),
                    color=Color.green(),
                    timestamp=datetime.now(tz=timezone.utc),
                )
            )
        else:
            await ctx.send(
                embed=Embed(
                    title="Word already in list of words defined as sensitive",
                    description=", ".join(fulldict["words"]),
                    color=Color.blue(),
                    timestamp=datetime.now(tz=timezone.utc),
                )
            )

    @sensitive.command(name="remove")
    async def remove(self, ctx: commands.Context, *, word: str):
        """Remove a word from the sensitive words filter.

        Parameters
        ----------
        self : Admin
            The Admin cog object.
        ctx : Context
            The context of the command.
        word : str
            The word to remove from the filter.
        """
        with open(self.settings, "rb") as file:
            fulldict = orjson.loads(file.read())
        if word.lower() in fulldict["words"]:
            fulldict["words"].remove(word.lower())
            fulldict["words"].sort()
            await ctx.send(
                embed=Embed(
                    title="New list of words defined as sensitive",
                    description=", ".join(fulldict["words"]),
                    color=Color.green(),
                    timestamp=datetime.now(tz=timezone.utc),
                )
            )
            with open(self.settings, "wb") as file:
                file.write(orjson.dumps(fulldict))
        else:
            await ctx.send(
                embed=Embed(
                    title="Word not in list of words defined as sensitive",
                    description=", ".join(fulldict["words"]),
                    color=Color.blue(),
                    timestamp=datetime.now(tz=timezone.utc),
                )
            )

    @sensitive.command(name="query")
    async def query(self, ctx: commands.Context):
        """Retrieve the list of words defined as sensitive.

        Parameters
        ----------
        self : Admin
            The Admin cog object.
        ctx : Context
            The context of the command.
        """
        with open(self.settings, "rb") as json_dict:
            fulldict = orjson.loads(json_dict.read())
        await ctx.send(
            embed=Embed(
                title="List of words defined as sensitive",
                description=", ".join(sorted(fulldict["words"])),
                color=Color.blue(),
                timestamp=datetime.now(tz=timezone.utc),
            )
        )

    @app_commands.command(
        name="confirm", description="[Charlie only] confirm a winner"
    )  # pyright: ignore[reportGeneralTypeIssues]
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 3600, key=lambda i: i.namespace.member)
    async def confirm(self, interaction: GuildInteraction[CBot], member: discord.Member) -> None:
        """Confirm a winner.

        Parameters
        ----------
        interaction: charbot.GuildInteraction[CBot]
            The interaction of the command invocation. At runtime, this is a discord.Interaction object, buy for
             typechecking, it's a charbot.GuildInteraction object to help infer the properties of the object.
        member : discord.Member
            The user to confirm as a winner.
        """
        if interaction.user.id != 225344348903047168:
            await interaction.response.send_message("Only Charlie can confirm a winner.", ephemeral=True)
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO winners (id, wins) VALUES ($1, 1) ON CONFLICT (id) DO UPDATE SET wins = winners.wins + 1",
                member.id,
            )
            wins = await conn.fetchrow("SELECT wins FROM winners WHERE id = $1", member.id)
        await interaction.response.send_message(
            f"Confirmed {member.name}#{member.discriminator} (ID: {member.id}) as having won a giveaway,"
            f" ({wins}/3 this month for them)",
            ephemeral=True,
        )


async def setup(bot: CBot):
    """Add the Admin cog to the bot.

    Parameters
    ----------
    bot : commands.Bot
        The bot object.
    """
    await bot.add_cog(Admin(bot))
