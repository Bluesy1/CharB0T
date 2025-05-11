"""Program classes and functions."""

import asyncio
import random
import re
from itertools import count
from typing import Final, Literal, cast

import discord
import niquests
from discord import Interaction, app_commands
from discord.ext import commands

from .. import CBot, constants  # , errors
from . import shrugman, sudoku
from .minesweeper.game import Game as MinesweeperGame
from .minesweeper.view import Minesweeper
from .tictactoe import Difficulty, TicTacToe


class Reputation(commands.Cog, name="Programs"):
    """Programs."""

    SUDOKU_REGEX: Final = re.compile(
        r"VALUE=\"(?P<solution>\d{81})\">.*VALUE=\"(?P<mask>[01]{81})\">",
        re.RegexFlag.MULTILINE | re.RegexFlag.DOTALL | re.RegexFlag.IGNORECASE,
    )

    async def interaction_check(self, interaction: Interaction[CBot]):  # skipcq: PYL-W0221
        """Check if the user is allowed to use the cog."""
        return interaction.channel_id == 839690221083820032
        # if interaction.guild is None:
        #     raise app_commands.NoPrivateMessage("Programs can't be used in direct messages.")
        # if interaction.guild.id != constants.GUILD_ID:
        #     raise app_commands.NoPrivateMessage("Programs can't be used in this server.")
        # channel = cast(discord.abc.GuildChannel, interaction.channel)
        # if channel.id == 839690221083820032:  # pragma: no cover
        #     return True
        # # fmt: off
        # if (
        #     channel.id != interaction.client.CHANNEL_ID
        #     and interaction.command.name != self.query_points.name
        # ):
        #     raise errors.WrongChannelError(interaction.client.CHANNEL_ID)
        # # fmt: on
        # return True

    default_permissions = discord.Permissions.none()
    default_permissions.move_members = True
    programs = app_commands.Group(
        name="programs",
        description="Programs to gain you rep.",
        guild_ids=constants.GUILD_IDS,
        default_permissions=default_permissions,
    )
    # beta = app_commands.Group(name="beta", description="Beta programs..", parent=programs)

    async def _get_sudoku(self) -> str:  # pragma: no cover
        async with await niquests.aget("https://nine.websudoku.com/?level=2") as response:
            return response.text or ""

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
        match = self.SUDOKU_REGEX.search(await self._get_sudoku())
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
    async def tictactoe(self, interaction: Interaction[CBot], difficulty: Difficulty):
        """Play a game of Tic Tac Toe!

        Parameters
        ----------
        interaction: Interaction[CBot]
            The interaction of the command.
        difficulty: tictactoe.Difficulty
            The difficulty of the game.
        """
        await interaction.response.defer(ephemeral=True)
        view = TicTacToe(difficulty)
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
        file = await view.draw("You lost!")
        embed = discord.Embed(title="Minesweeper", color=discord.Color.dark_purple())
        embed.set_footer(text="Play by typing /programs minesweeper")
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_image(url="attachment://minesweeper.png")
        await interaction.followup.send(embed=embed, view=view, file=file)

    # @app_commands.command()
    # @app_commands.guilds(constants.GUILD_ID)
    # async def rollcall(self, interaction: Interaction[CBot]):
    #     """Claim your daily reputation bonus.

    #     Parameters
    #     ----------
    #     interaction: Interaction[CBot]
    #         The interaction of the command invocation.
    #     """
    #     await interaction.response.defer(ephemeral=True)

    #     async with interaction.client.pool.acquire() as conn:
    #         result_user = await conn.fetchrow(
    #             "SELECT id, points, particip, won, last_claim as daily, last_particip_dt as particip_dt "
    #             "FROM users WHERE id = $1",
    #             interaction.user.id,
    #         )
    #         current_time = interaction.client.TIME()
    #         if result_user is None:
    #             await conn.execute(
    #                 "INSERT INTO users (id, points, last_claim, last_particip_dt, particip, won) "
    #                 "VALUES ($1, 20, $2, $3, 0, 0)",
    #                 interaction.user.id,
    #                 current_time,
    #                 current_time - datetime.timedelta(days=1),
    #             )
    #             await interaction.followup.send("You got some Rep today, inmate")
    #             return
    #         if result_user["daily"] >= current_time:
    #             await interaction.followup.send("No more Rep for you yet, get back to your cell")
    #             return
    #         await conn.execute(
    #             "UPDATE users SET points = points + 20, last_claim = $2 WHERE id = $1",
    #             interaction.user.id,
    #             current_time,
    #         )
    #         await interaction.followup.send("You got some Rep today, inmate")

    # @app_commands.command(name="reputation", description="Check your reputation")
    # @app_commands.guilds(constants.GUILD_ID)
    # async def query_points(self, interaction: Interaction[CBot]):
    #     """Query your reputation.

    #     Parameters
    #     ----------
    #     interaction: Interaction[CBot]
    #         The interaction of the command invocation.
    #     """
    #     await interaction.response.defer(ephemeral=True)
    #     async with interaction.client.pool.acquire() as conn:
    #         results = await conn.fetchrow(
    #             "SELECT points, last_claim, last_particip_dt, particip, wins FROM users WHERE id = $1",
    #             interaction.user.id,
    #         ) or {
    #             "points": 0,
    #             "last_claim": 0,
    #             "last_particip_dt": 0,
    #             "particip": 0,
    #             "wins": 0,
    #         }
    #     current_time = interaction.client.TIME()
    #     claim = "have" if results["last_claim"] == current_time else "haven't"
    #     particip = (
    #         "have" if (results["last_particip_dt"] == current_time) and (results["particip"] >= 10) else "haven't"
    #     )
    #     await interaction.followup.send(
    #         f"You have {results['points']} reputation, you {claim} claimed your daily bonus, and you {particip} hit"
    #         f" your daily program cap, and have {results['wins']}/3 wins in the last month.",
    #         ephemeral=True,
    #     )
