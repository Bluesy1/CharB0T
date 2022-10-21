# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

import asyncio
import datetime
import pathlib
from io import BytesIO
from typing import cast

from typing_extensions import Self

import discord
from PIL import Image
from discord import ButtonStyle, ui
from discord.utils import utcnow

from .. import GuildComponentInteraction as Interaction, CBot
from charbot_rust.tictactoe import Game, Difficulty, Piece  # pyright: ignore[reportGeneralTypeIssues]


class TicTacToe(ui.View):
    """Tic Tac Toe View.

    This is the view that is shown to the user.

    Parameters
    ----------
    difficulty : Difficulty
        The difficulty of the game.
    """

    __slots__ = (
        "bot",
        "game",
        "difficulty",
        "cancel",
        "top_left",
        "top_mid",
        "top_right",
        "mid_left",
        "mid_mid",
        "mid_right",
        "bot_left",
        "bot_mid",
        "bot_right",
    )

    def __init__(self, difficulty: Difficulty):
        super(TicTacToe, self).__init__(timeout=300)
        self.game: Game = Game(difficulty)
        self.time: datetime.datetime = utcnow()
        self._buttons = [
            self.top_left,
            self.top_mid,
            self.top_right,
            self.mid_left,
            self.mid_mid,
            self.mid_right,
            self.bot_left,
            self.bot_mid,
            self.bot_right,
        ]
        for i, item in enumerate(self.game.board):
            self._buttons[i].disabled = item.value != " "

    # noinspection DuplicatedCode
    def disable(self) -> None:
        """Disable all view buttons."""
        self.cancel.disabled = True
        self.top_left.disabled = True
        self.top_mid.disabled = True
        self.top_right.disabled = True
        self.mid_left.disabled = True
        self.mid_mid.disabled = True
        self.mid_right.disabled = True
        self.bot_left.disabled = True
        self.bot_mid.disabled = True
        self.bot_right.disabled = True
        self.stop()

    def display(self) -> discord.File:
        """Display the tictactoe game as an image.

        Returns
        -------
        discord.File
            The image of the tictactoe game.
        """
        grid = Image.open(pathlib.Path(__file__).parent.parent / "media/tictactoe/grid.png", "r").convert("RGBA")
        cross = Image.open(pathlib.Path(__file__).parent.parent / "media/tictactoe/X.png", "r")
        circle = Image.open(pathlib.Path(__file__).parent.parent / "media/tictactoe/O.png", "r")
        for command, display in self.game.display_commands():
            if display == Piece.Empty:
                continue
            if display == Piece.X:
                grid.paste(cross, command.value, cross)
            elif display == Piece.O:
                grid.paste(circle, command.value, circle)
        buffer = BytesIO()
        grid.save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(buffer, filename="tictactoe.png")

    async def move(self, interaction: Interaction[CBot], button: ui.Button[Self], pos: int) -> None:
        """Call this to handle a move button press.

        Parameters
        ----------
        interaction : Interaction
            The interaction that triggered this event
        button : ui.Button
            The button that was pressed
        pos: int
            The position of the button on the grid via list index.
        """
        await interaction.response.edit_message(view=None)
        comp_move = await asyncio.to_thread(self.game.play, pos)
        button.disabled = True
        if comp_move is not None:
            self._buttons[comp_move].disabled = True
        if self.game.has_player_won():
            points: tuple[int, int] = self.game.points()
            member = cast(discord.Member, interaction.user)
            gained_points = await interaction.client.give_game_points(member, "tictactoe", points[0], points[1])
            max_points = points[0] + points[1]
            embed = discord.Embed(
                title="You Won!",
                description=f"You won the game in "
                f"{utcnow().replace(microsecond=0) - self.time.replace(microsecond=0)} seconds! You gained "
                f"{gained_points} reputation. {'(Daily Cap Reached)' if gained_points != max_points else ''}",
                color=discord.Color.green(),
            ).set_image(url="attachment://tictactoe.png")
            embed.set_footer(text="Start playing by typing /programs tictactoe")
            self.disable()
            image = await asyncio.to_thread(self.display)
            await interaction.edit_original_response(attachments=[image], embed=embed, view=self)
        elif self.game.has_player_lost():
            points = self.game.points()
            member = cast(discord.Member, interaction.user)
            gained_points = await interaction.client.give_game_points(member, "tictactoe", points[0], points[1])
            max_points = points[0] + points[1]
            embed = discord.Embed(
                title="You Lost!",
                description=f"You lost the game in "
                f"{utcnow().replace(microsecond=0) - self.time.replace(microsecond=0)} seconds! You gained "
                f"{gained_points} reputation. {'(Daily Cap Reached)' if gained_points != max_points else ''}",
                color=discord.Color.red(),
            ).set_image(url="attachment://tictactoe.png")
            embed.set_footer(text="Start playing by typing /programs tictactoe")
            self.disable()
            image = await asyncio.to_thread(self.display)
            await interaction.edit_original_response(attachments=[image], embed=embed, view=self)
        elif self.game.is_draw():
            points = self.game.points()
            member = cast(discord.Member, interaction.user)
            gained_points = await interaction.client.give_game_points(member, "tictactoe", points[0], points[1])
            max_points = points[0] + points[1]
            embed = discord.Embed(
                title="Draw!",
                description=f"The game ended in a draw in "
                f"{utcnow().replace(microsecond=0) - self.time.replace(microsecond=0)} seconds! You gained "
                f"{gained_points} reputation. {'(Daily Cap Reached)' if gained_points != max_points else ''}",
                color=discord.Color.gold(),
            ).set_image(url="attachment://tictactoe.png")
            embed.set_footer(text="Start playing by typing /programs tictactoe")
            self.disable()
            image = await asyncio.to_thread(self.display)
            await interaction.edit_original_response(attachments=[image], embed=embed, view=self)
        else:
            image = await asyncio.to_thread(self.display)
            await interaction.edit_original_response(attachments=[image], view=self)

    @ui.button(style=ButtonStyle.green, emoji="✅")  # pyright: ignore[reportGeneralTypeIssues]
    async def top_left(self, interaction: Interaction[CBot], button: ui.Button):
        """Call when top left button is pressed.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 0)

    @ui.button(style=ButtonStyle.green, emoji="✅")  # pyright: ignore[reportGeneralTypeIssues]
    async def top_mid(self, interaction: Interaction[CBot], button: ui.Button):
        """Call when top middle button is pressed.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 1)

    @ui.button(style=ButtonStyle.green, emoji="✅")  # pyright: ignore[reportGeneralTypeIssues]
    async def top_right(self, interaction: Interaction[CBot], button: ui.Button):
        """Call when top right button is pressed.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 2)

    # noinspection PyUnusedLocal
    @ui.button(label="Cancel", style=ButtonStyle.danger)  # pyright: ignore[reportGeneralTypeIssues]
    async def cancel(self, interaction: Interaction[CBot], button: ui.Button):  # skipcq: PYL-W0613
        """Call when cancel button is pressed.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        self.disable()
        embed = discord.Embed(
            title="TicTacToe",
            description=f"Cancelled, time taken: {utcnow().replace(microsecond=0) - self.time.replace(microsecond=0)}",
            color=discord.Color.red(),
        ).set_image(url="attachment://tictactoe.png")
        embed.set_footer(text="Start playing by typing /programs tictactoe")
        await interaction.response.edit_message(embed=embed)

    @ui.button(style=ButtonStyle.green, emoji="✅", row=1)  # pyright: ignore[reportGeneralTypeIssues]
    async def mid_left(self, interaction: Interaction[CBot], button: ui.Button):
        """Call when middle left button is pressed.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 3)

    @ui.button(style=ButtonStyle.green, emoji="✅", row=1)  # pyright: ignore[reportGeneralTypeIssues]
    async def mid_mid(self, interaction: Interaction[CBot], button: ui.Button):
        """Call when middle_middle button is pressed.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 4)

    @ui.button(style=ButtonStyle.green, emoji="✅", row=1)  # pyright: ignore[reportGeneralTypeIssues]
    async def mid_right(self, interaction: Interaction[CBot], button: ui.Button):
        """Call when middle right button is pressed.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 5)

    @ui.button(style=ButtonStyle.green, emoji="✅", row=2)  # pyright: ignore[reportGeneralTypeIssues]
    async def bot_left(self, interaction: Interaction[CBot], button: ui.Button):
        """Call when bottom left button is pressed.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 6)

    @ui.button(style=ButtonStyle.green, emoji="✅", row=2)  # pyright: ignore[reportGeneralTypeIssues]
    async def bot_mid(self, interaction: Interaction[CBot], button: ui.Button):
        """Call when bottom middle button is pressed.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 7)

    @ui.button(style=ButtonStyle.green, emoji="✅", row=2)  # pyright: ignore[reportGeneralTypeIssues]
    async def bot_right(self, interaction: Interaction[CBot], button: ui.Button):
        """Call when bottom right button is pressed.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 8)
