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
from datetime import datetime, timedelta, timezone
from time import perf_counter

import discord
import orjson
from discord import Color, Embed, app_commands
from discord.ext import commands

from . import CBot


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
        with open("charbot/sensitive_settings.json", "rb") as json_dict:
            fulldict = orjson.loads(json_dict.read())
        if word.lower() not in fulldict["words"]:
            fulldict["words"].append(word.lower()).sort()
            with open("charbot/sensitive_settings.json", "wb") as json_dict:
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
        with open("charbot/sensitive_settings.json", "rb") as file:
            fulldict = orjson.loads(file.read())
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
            with open("charbot/sensitive_settings.json", "wb") as file:
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
        with open("charbot/sensitive_settings.json", "rb") as json_dict:
            fulldict = orjson.loads(json_dict.read())
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
        time: app_commands.Range[int, 1, 30] = 6,
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
            self.bot.TIME() + timedelta(days=time),
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
