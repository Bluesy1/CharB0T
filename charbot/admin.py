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
"""Admin commands for charbot."""
import json
from datetime import datetime, timedelta, timezone
from typing import Optional

import discord
from discord import AppCommandOptionType, Color, Embed, app_commands
from discord.ext import commands

from . import CBot


class IntToTimeDelta(app_commands.Transformer):
    """Transformer that converts an integer to a timedelta.

    This is used to convert the time limit to a timedelta. for app_commands, as discord doesn't support any time based
    arguments.

    Methods
    -------
    type
        Returns the type of the argument.
    min_value
        Returns the minimum value of the argument.
    max_value
        Returns the maximum value of the argument.
    transform
        Transforms an integer to a timedelta.
    autocomplete
        Autocompletes the argument.
    """

    @classmethod
    def type(cls) -> AppCommandOptionType:
        """Return the type of the argument.

        Returns
        -------
        AppCommandOptionType
            The type of the argument.
        """
        return AppCommandOptionType.integer

    @classmethod
    def min_value(cls) -> int:
        """Return the minimum value of the argument.

        Returns
        -------
        int
            The minimum value of the argument.
        """
        return 1

    @classmethod
    def max_value(cls) -> int:
        """Return the maximum value of the argument.

        Returns
        -------
        int
            The maximum value of the argument.
        """
        return 60

    @classmethod
    async def transform(
        cls, interaction: discord.Interaction, value: str | int | float  # skipcq: PYL-W0613
    ) -> timedelta:
        """Transform an integer to a timedelta.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction to transform.
        value : int
            The value to transform.

        Returns
        -------
        datetime.timedelta
            The transformed value.
        """
        if value is None:
            return timedelta(days=6)
        return timedelta(days=int(value))

    @classmethod
    async def autocomplete(
        cls, interaction: discord.Interaction, value: str | int | float  # skipcq: PYL-W0613
    ) -> list[app_commands.Choice[int]]:
        """Autocompletes the argument.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction to autocomplete.
        value : int
            The value to autocomplete.

        Returns
        -------
        list[app_commands.Choice[int]]
            The autocompleted value.
        """
        try:
            _value = int(value)
        except ValueError:
            return [app_commands.Choice(value=i, name=f"{i} days") for i in range(1, 26)]
        else:
            if _value <= 13:
                return [app_commands.Choice(value=i, name=f"{i} days") for i in range(1, 26)]
            if _value > 47:
                return [app_commands.Choice(value=i, name=f"{i} days") for i in range(36, 61)]
            return [app_commands.Choice(value=i, name=f"{i} days") for i in range(_value - 12, _value + 13)]


class Admin(commands.Cog):
    """Admin Cog."""

    def __init__(self, bot: CBot):
        self.bot = bot

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
        await ctx.send(f"Pong! Latency: {self.bot.latency * 1000:.2f}ms")

    @commands.hybrid_group(name="sensitive")
    @app_commands.guilds(225345178955808768)
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
        with open("sensitive_settings.json", encoding="utf8") as json_dict:
            fulldict = json.load(json_dict)
        if word.lower() not in fulldict["words"]:
            fulldict["words"].append(word.lower()).sort()
            with open("sensitive_settings.json", "w", encoding="utf8") as json_dict:
                json.dump(fulldict, json_dict)
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
        with open("sensitive_settings.json", encoding="utf8") as file:
            fulldict = json.load(file)
        if word.lower() in fulldict["words"]:
            fulldict["words"].remove(word.lower()).sort()
            await ctx.send(
                embed=Embed(
                    title="New list of words defined as sensitive",
                    description=", ".join(fulldict["words"]),
                    color=Color.green(),
                    timestamp=datetime.now(tz=timezone.utc),
                )
            )
            with open("sensitive_settings.json", "w", encoding="utf8") as file:
                json.dump(fulldict, file)
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
        with open("sensitive_settings.json", encoding="utf8") as json_dict:
            fulldict = json.load(json_dict)
        await ctx.send(
            embed=Embed(
                title="List of words defined as sensitive",
                description=", ".join(sorted(fulldict["words"])),
                color=Color.blue(),
                timestamp=datetime.now(tz=timezone.utc),
            )
        )

    @app_commands.command(name="confirm", description="[Charlie only] confirm a winner")
    @app_commands.guilds(225345178955808768)
    async def confirm(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        time: Optional[app_commands.Transform[timedelta, IntToTimeDelta]] = None,
    ) -> None:
        """Confirm a winner.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction of the command invocation.
        user : discord.Member
            The user to confirm as a winner.
        time : Optional[IntToTimeDeltaTransformer] = None
            [OPTIONAL, Default 6] How many days should the winner be blocked from bidding again?"
        """
        if interaction.user.id != 225344348903047168:
            await interaction.response.send_message("Only Charlie can confirm a winner.", ephemeral=True)
            return
        await self.bot.pool.execute(
            "INSERT INTO winners (id, expiry) VALUES ($1, $2) ON CONFLICT (id) DO UPDATE SET expiry = $2",
            user.id,
            self.bot.TIME() + (time or timedelta(days=6)),
        )
        await interaction.response.send_message("Confirmed.", ephemeral=True)


async def setup(bot: CBot):
    """Add the Admin cog to the bot.

    Parameters
    ----------
    bot : commands.Bot
        The bot object.
    """
    await bot.add_cog(Admin(bot), guild=discord.Object(id=225345178955808768))
