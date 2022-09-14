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
"""Program classes and functions."""
import asyncio
import datetime
import random
import re
from typing import Final, Literal, TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from . import shrugman, sudoku, tictactoe
from .. import errors, GuildInteraction as Interaction
from .minesweeper import Minesweeper
from charbot_rust.minesweeper import Game as MinesweeperGame  # pyright: ignore[reportGeneralTypeIssues]

if TYPE_CHECKING:
    from .. import CBot


MESSAGE: Final = "You must be at least level 1 to participate in the giveaways system and be in <#969972085445238784>."


class Reputation(commands.Cog, name="Programs"):
    """Programs."""

    def __init__(self, bot: "CBot"):
        self.bot = bot
        self.sudoku_regex = re.compile(r"(\d{81}).*([01]{81})")

    async def interaction_check(self, interaction: Interaction):  # skipcq: PYL-W0221
        """Check if the user is allowed to use the cog."""
        if interaction.guild is None:
            raise app_commands.NoPrivateMessage("Programs can't be used in direct messages.")
        if interaction.guild.id != 225345178955808768:
            raise app_commands.NoPrivateMessage("Programs can't be used in this server.")
        channel = interaction.channel
        assert isinstance(channel, discord.abc.GuildChannel)  # skipcq: BAN-B101
        if channel.id == 839690221083820032:
            return True
        if channel.id != self.bot.CHANNEL_ID:
            raise errors.WrongChannelError(self.bot.CHANNEL_ID, interaction.locale)
        user = interaction.user
        assert isinstance(user, discord.Member)  # skipcq: BAN-B101
        if not any(role.id in self.bot.ALLOWED_ROLES for role in user.roles):
            raise errors.MissingProgramRole(self.bot.ALLOWED_ROLES, interaction.locale)
        return True

    programs = app_commands.Group(name="programs", description="Programs to gain you rep.", guild_only=True)
    beta = app_commands.Group(name="beta", description="Beta programs..", parent=programs)

    @programs.command(name="sudoku", description="Play a Sudoku puzzle")  # pyright: ignore[reportGeneralTypeIssues]
    async def sudoku(self, interaction: Interaction["CBot"], mobile: bool):
        """Generate a sudoku puzzle.

        Parameters
        ----------
        interaction: Interaction[CBot]
            The interaction of the command.
        mobile: bool
            Whether to turn off formatting that only works on desktop.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.session.get("https://nine.websudoku.com/?level=2") as response:
            match = self.sudoku_regex.search(str(await response.content.read()))
            if match is None:
                await interaction.followup.send("Couldn't find a puzzle.")
                return
            vals, hidden = match.group(1, 2)
        board: list[list[int]] = [[] for _ in range(9)]
        for i, num in enumerate(vals):
            board[i // 9].append(int(num) if int(hidden[i]) == 0 else 0)
        user = interaction.user
        assert isinstance(user, discord.Member)  # skipcq: BAN-B101
        view = sudoku.Sudoku(sudoku.Puzzle(board, mobile), user, self.bot)
        await interaction.followup.send(embed=view.block_choose_embed(), view=view)

    @programs.command(
        name="tictactoe", description="Play a game of Tic Tac Toe!"
    )  # pyright: ignore[reportGeneralTypeIssues]
    async def tictactoe(self, interaction: Interaction["CBot"], difficulty: tictactoe.Difficulty):
        """Play a game of Tic Tac Toe! Now built with rust.

        Parameters
        ----------
        interaction: Interaction[CBot]
            The interaction of the command.
        difficulty: tictactoe.Difficulty
            The difficulty of the game.
        """
        await interaction.response.defer(ephemeral=True)
        view = tictactoe.TicTacToe(difficulty)
        embed = discord.Embed(title="TicTacToe").set_image(url="attachment://tictactoe.png")
        embed.set_footer(text="Play by typing /programs tictactoe")
        image = await asyncio.to_thread(view.display)
        await interaction.followup.send(embed=embed, view=view, file=image)

    @programs.command(
        name="shrugman", description="Play the shrugman minigame. (Hangman clone)"
    )  # pyright: ignore[reportGeneralTypeIssues]
    async def shrugman(self, interaction: Interaction["CBot"]) -> None:
        """Play a game of Shrugman.

        This game is a hangman-like game.

        The game is played by guessing letters.

        The game ends when the word is guessed or the player runs out of guesses.

        The game is won by guessing the word.

        The game is lost by running out of guesses.

        Parameters
        ----------
        interaction: Interaction[CBot]
            The interaction of the command.
        """
        await interaction.response.defer(ephemeral=True)
        word = random.choice(shrugman.words)
        embed = discord.Embed(
            title="Shrugman",
            description=f"Guess the word: `{''.join(['-' for _ in word])}`",
            color=discord.Color.dark_purple(),
        )
        embed.set_footer(text="Play by typing /programs shrugman")
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        view = shrugman.Shrugman(self.bot, word)
        await interaction.followup.send(embed=embed, view=view)

    @beta.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def minesweeper(
        self,
        interaction: Interaction["CBot"],
        difficulty: Literal["Beginner", "Intermediate", "Expert", "Super Expert"],
    ):
        """[BETA] Play a game of Minesweeper.

        Parameters
        ----------
        interaction: Interaction[CBot]
            The interaction of the command.
        difficulty: {"Beginner", "Intermediate", "Expert", "Super Expert"}
            The difficulty of the game.
        """
        await interaction.response.defer(ephemeral=True)
        if difficulty == "Beginner":
            game = MinesweeperGame.beginner()
        elif difficulty == "Intermediate":
            game = MinesweeperGame.intermediate()
        elif difficulty == "Expert":
            game = MinesweeperGame.expert()
        else:
            game = MinesweeperGame.super_expert()
        view = Minesweeper(game)
        file = await view.draw(await interaction.client.translate("minesweeper-lose-title", interaction.locale))
        embed = discord.Embed(title="Minesweeper", color=discord.Color.dark_purple())
        embed.set_footer(text="Play by typing /programs minesweeper")
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_image(url="attachment://minesweeper.png")
        await interaction.followup.send(embed=embed, view=view, file=file)

    # noinspection SpellCheckingInspection
    @app_commands.command()  # pyright: ignore[reportGeneralTypeIssues]
    @app_commands.guild_only()
    async def rollcall(self, interaction: Interaction["CBot"]):
        """Claim your daily reputation bonus.

        Parameters
        ----------
        interaction: Interaction[CBot]
            The interaction of the command invocation.
        """
        clientuser = self.bot.user
        assert isinstance(clientuser, discord.ClientUser)  # skipcq: BAN-B101
        await interaction.response.defer(ephemeral=True)
        giveaway_user = await self.bot.giveaway_user(interaction.user.id)
        if giveaway_user is None:
            async with self.bot.pool.acquire() as conn:
                await conn.execute("INSERT INTO users (id, points) VALUES ($1, 20)", interaction.user.id)
                await conn.execute(
                    "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won) VALUES "
                    "($1, $2, $3, 0, 0)",
                    interaction.user.id,
                    self.bot.TIME(),
                    self.bot.TIME() - datetime.timedelta(days=1),
                )
                await conn.execute("INSERT INTO bids (id, bid) VALUES ($1, 0)", interaction.user.id)
                await interaction.followup.send("You got some Rep today, inmate")
                await self.bot.program_logs.send(
                    f"{interaction.user.mention} has claimed their daily reputation bonus.",
                    allowed_mentions=discord.AllowedMentions(users=False),
                    username=clientuser.name,
                    avatar_url=clientuser.display_avatar.url,
                )
            return
        if giveaway_user["daily"] >= self.bot.TIME():
            await interaction.followup.send("No more Rep for you yet, get back to your cell")
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE users SET points = points + 20 WHERE id = $1", interaction.user.id)
            await conn.execute(
                "UPDATE daily_points SET last_claim = $1 WHERE id = $2", self.bot.TIME(), interaction.user.id
            )
        await interaction.followup.send("You got some Rep today, inmate")
        await self.bot.program_logs.send(
            f"{interaction.user.mention} has claimed their daily reputation bonus.",
            allowed_mentions=discord.AllowedMentions(users=False),
            username=clientuser.name,
            avatar_url=clientuser.display_avatar.url,
        )

    @app_commands.command(
        name="reputation", description="Check your reputation"
    )  # pyright: ignore[reportGeneralTypeIssues]
    @app_commands.guild_only()
    async def query_points(self, interaction: Interaction["CBot"]):
        """Query your reputation.

        Parameters
        ----------
        interaction: Interaction[CBot]
            The interaction of the command invocation.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            points = await conn.fetchval("SELECT points from users where id = $1", interaction.user.id) or 0
            # noinspection SpellCheckingInspection
            limits = await conn.fetchrow("SELECT * from daily_points where id = $1", interaction.user.id) or {
                "last_claim": 0,
                "last_particip_dt": 0,
                "particip": 0,
            }
            wins = await conn.fetchval("SELECT wins FROM winners WHERE id = $1", interaction.user.id) or 0
        claim = "have" if limits["last_claim"] == self.bot.TIME() else "haven't"
        # noinspection SpellCheckingInspection
        particip = (
            "have" if (limits["last_particip_dt"] == self.bot.TIME()) and (limits["particip"] >= 10) else "haven't"
        )
        await interaction.followup.send(
            f"You have {points} reputation, you {claim} claimed your daily bonus, and you {particip} hit"
            f" your daily program cap, and have {wins}/3 wins in the last month.",
            ephemeral=True,
        )


async def setup(bot: "CBot"):
    """Load the cog.

    Parameters
    ----------
    bot : CBot
    """
    await bot.add_cog(Reputation(bot), override=True)


async def teardown(bot: "CBot"):
    """Unload the cog.

    Parameters
    ----------
    bot : CBot
    """
    await bot.remove_cog("Programs")
