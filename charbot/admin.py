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
from datetime import datetime, timezone

import discord
from discord import Embed, Color, app_commands
from discord.ext import commands
from discord.ext.commands import Cog, Context


class Admin(Cog):
    """Admin Cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        """Check to make sure runner is a moderator

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
        return any(
            role.id in (338173415527677954, 253752685357039617, 225413350874546176)
            for role in ctx.author.roles  # type: ignore
        )

    @commands.command()
    async def ping(self, ctx: Context):
        """Ping Command TO Check Bot Is Alive

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
    async def sensitive(self, ctx: Context):
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
    async def add(self, ctx: Context, *, word: str):
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
    async def remove(self, ctx: Context, *, word: str):
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
    async def query(self, ctx: Context):
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


async def setup(bot: commands.Bot):
    """Add the Admin cog to the bot.

    Parameters
    ----------
    bot : commands.Bot
        The bot object.
    """
    await bot.add_cog(Admin(bot), guild=discord.Object(id=225345178955808768))
