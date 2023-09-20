# -*- coding: utf-8 -*-
"""Program classes and functions."""
import asyncio
import datetime
import random
import re
from itertools import count
from typing import Final, Literal, cast

import discord
from discord import Interaction, app_commands
from discord.ext import commands

from .. import CBot, errors
from . import sudoku, tictactoe, shrugman
from .minesweeper import Minesweeper
from charbot_rust.minesweeper import Game as MinesweeperGame  # pyright: ignore[reportGeneralTypeIssues]

MESSAGE: Final = "You must be at least level 1 to participate in the giveaways system and be in <#969972085445238784>."


class Reputation(commands.Cog, name="Programs"):
    """Programs."""

    SUDOKU_REGEX: Final = re.compile(
        r"VALUE=\"(?P<solution>\d{81})\">.*VALUE=\"(?P<mask>[01]{81})\">",
        re.RegexFlag.MULTILINE | re.RegexFlag.DOTALL | re.RegexFlag.IGNORECASE,
    )

    async def interaction_check(self, interaction: Interaction[CBot]):  # skipcq: PYL-W0221
        """Check if the user is allowed to use the cog."""
        if interaction.guild is None:
            raise app_commands.NoPrivateMessage("Programs can't be used in direct messages.")
        if interaction.guild.id != 225345178955808768:
            raise app_commands.NoPrivateMessage("Programs can't be used in this server.")
        channel = cast(discord.abc.GuildChannel, interaction.channel)
        if channel.id == 839690221083820032:  # pragma: no cover
            return True
        if (
            channel.id != interaction.client.CHANNEL_ID
            and interaction.command.name != self.query_points.name  # pyright: ignore[reportOptionalMemberAccess]
        ):
            raise errors.WrongChannelError(interaction.client.CHANNEL_ID, interaction.locale)
        if all(
            role.id not in interaction.client.ALLOWED_ROLES for role in cast(discord.Member, interaction.user).roles
        ):
            raise errors.MissingProgramRole(interaction.client.ALLOWED_ROLES, interaction.locale)
        return True

    programs = app_commands.Group(name="programs", description="Programs to gain you rep.", guild_only=True)
    beta = app_commands.Group(name="beta", description="Beta programs..", parent=programs)

    @programs.command(name="sudoku", description="Play a Sudoku puzzle")
    async def sudoku(self, interaction: Interaction[CBot], mobile: bool):
        """Generate a sudoku puzzle.

        Parameters
        ----------
        interaction: Interaction[CBot]
            The interaction of the command.
        mobile: bool
            Whether to turn off formatting that only works on desktop.
        """
        await interaction.response.defer(ephemeral=True)
        async with interaction.client.session.get("https://nine.websudoku.com/?level=2") as response:
            match = self.SUDOKU_REGEX.search(str(await response.content.read()))
            if match is None:
                await interaction.followup.send("Couldn't find a puzzle.")
                return
            vals, hidden = match.group("solution", "mask")
        board: list[list[int]] = [[] for _ in range(9)]
        for i, num, hidden_bit in zip(count(), vals, hidden):
            board[i // 9].append(int(num) if int(hidden_bit) == 0 else 0)
        view = sudoku.Sudoku(sudoku.Puzzle(board, mobile), cast(discord.Member, interaction.user), interaction.client)
        await interaction.followup.send(embed=view.block_choose_embed(), view=view)

    @programs.command(name="tictactoe", description="Play a game of Tic Tac Toe!")
    async def tictactoe(self, interaction: Interaction[CBot], difficulty: tictactoe.Difficulty):
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

    @programs.command(name="shrugman", description="Play the shrugman minigame. (Hangman clone)")
    async def shrugman(self, interaction: Interaction[CBot]) -> None:
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
        view = shrugman.Shrugman(interaction.client, word)
        await interaction.followup.send(embed=embed, view=view)

    @programs.command()
    async def minesweeper(
        self,
        interaction: Interaction[CBot],
        difficulty: Literal["Beginner", "Intermediate", "Expert", "Super Expert"],
    ):
        """Play a game of Minesweeper.

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
    @app_commands.command()
    @app_commands.guild_only()
    async def rollcall(self, interaction: Interaction[CBot]):
        """Claim your daily reputation bonus.

        Parameters
        ----------
        interaction: Interaction[CBot]
            The interaction of the command invocation.
        """
        await interaction.response.defer(ephemeral=True)
        giveaway_user = await interaction.client.pool.fetchrow(
            "SELECT users.id as id, points, b.bid as bid, dp.last_claim as daily, dp.last_particip_dt as "
            "particip_dt, dp.particip as particip, dp.won as won "
            "FROM users join bids b on users.id = b.id join daily_points dp on users.id = dp.id WHERE users.id = $1",
            interaction.user.id,
        )
        if giveaway_user is None:
            async with interaction.client.pool.acquire() as conn:
                await conn.execute("INSERT INTO users (id, points) VALUES ($1, 20)", interaction.user.id)
                await conn.execute(
                    "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won) VALUES "
                    "($1, $2, $3, 0, 0)",
                    interaction.user.id,
                    interaction.client.TIME(),
                    interaction.client.TIME() - datetime.timedelta(days=1),
                )
                await conn.execute("INSERT INTO bids (id, bid) VALUES ($1, 0)", interaction.user.id)
                await interaction.followup.send("You got some Rep today, inmate")
            return
        if giveaway_user["daily"] >= interaction.client.TIME():
            await interaction.followup.send("No more Rep for you yet, get back to your cell")
            return
        async with interaction.client.pool.acquire() as conn:
            await conn.execute("UPDATE users SET points = points + 20 WHERE id = $1", interaction.user.id)
            await conn.execute(
                "UPDATE daily_points SET last_claim = $1 WHERE id = $2", interaction.client.TIME(), interaction.user.id
            )
        await interaction.followup.send("You got some Rep today, inmate")

    @app_commands.command(name="reputation", description="Check your reputation")
    @app_commands.guild_only()
    async def query_points(self, interaction: Interaction[CBot]):
        """Query your reputation.

        Parameters
        ----------
        interaction: Interaction[CBot]
            The interaction of the command invocation.
        """
        await interaction.response.defer(ephemeral=True)
        async with interaction.client.pool.acquire() as conn:
            points = await conn.fetchval("SELECT points from users where id = $1", interaction.user.id) or 0
            # noinspection SpellCheckingInspection
            limits = await conn.fetchrow("SELECT * from daily_points where id = $1", interaction.user.id) or {
                "last_claim": 0,
                "last_particip_dt": 0,
                "particip": 0,
            }
            wins = await conn.fetchval("SELECT wins FROM winners WHERE id = $1", interaction.user.id) or 0
        claim = "have" if limits["last_claim"] == interaction.client.TIME() else "haven't"
        # noinspection SpellCheckingInspection
        particip = (
            "have"
            if (limits["last_particip_dt"] == interaction.client.TIME()) and (limits["particip"] >= 10)
            else "haven't"
        )
        await interaction.followup.send(
            f"You have {points} reputation, you {claim} claimed your daily bonus, and you {particip} hit"
            f" your daily program cap, and have {wins}/3 wins in the last month.",
            ephemeral=True,
        )
