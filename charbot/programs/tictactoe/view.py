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
"""Tic-tac-toe game view."""
from typing import TYPE_CHECKING

import discord
from discord import ButtonStyle, Interaction, ui
from discord.utils import utcnow

from . import TicTacABC, TicTacEasy, TicTacHard


if TYPE_CHECKING:
    from ...types.bot import CBot


class TicTacView(ui.View):
    """Tic Tac Toe View.

    This is the view that is shown to the user.

    Parameters
    ----------
    bot: CBot
        The bot instance.
    letter: str (default: "X")
        The letter that the user will be playing with.
    easy: bool (default: True)
        Whether the user is playing easy mode.

    Attributes
    ----------
    bot: CBot
        The bot instance.
    letter: str
        The letter that the user will be playing with.
    puzzle: TicTacABC
        The puzzle instance.
    time: datetime.datetime
        The time when the game started.
    """

    def __init__(self, bot: "CBot", letter: str = "X", easy: bool = True):
        super(TicTacView, self).__init__(timeout=300)
        self.letter = letter
        self.puzzle: TicTacABC = TicTacEasy(self.letter) if easy else TicTacHard(self.letter)
        self.bot = bot
        self.time = utcnow()
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

    async def move(self, interaction: discord.Interaction, button: ui.Button, x: int, y: int) -> None:
        """Call this to handle a move button press.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered this event
        button : ui.Button
            The button that was pressed
        x : int
            The x coordinate of the button
        y : int
            The y coordinate of the button
        """
        await interaction.response.edit_message(view=None)
        self.puzzle.move(x, y)
        button.disabled = True
        if self.puzzle.check_win() == 1:
            points = self.puzzle.points
            member = interaction.user
            assert isinstance(member, discord.Member)  # skipcq: BAN-B101
            gained_points = await self.bot.give_game_points(member, "tictactoe", points.participation, points.bonus)
            max_points = points.participation + points.bonus
            embed = discord.Embed(
                title="You Won!",
                description=f"You won the game in "
                f"{utcnow().replace(microsecond=0) - self.time.replace(microsecond=0)} seconds! "
                f"You gained {gained_points} reputation. "
                f"{'(Daily Cap Reached)' if gained_points != max_points else ''}",
                color=discord.Color.green(),
            ).set_image(url="attachment://tictactoe.png")
            embed.set_footer(text="Start playing by typing /programs tictactoe")
            self.disable()
            image = await self.bot.loop.run_in_executor(None, self.puzzle.display)
            await interaction.edit_original_message(attachments=[image], embed=embed, view=self)
            return
        move = await self.bot.loop.run_in_executor(None, self.puzzle.next)
        self._buttons[move[0] * 3 + move[1]].disabled = True
        if self.puzzle.board[move[0]][move[1]] == "blur":
            self.puzzle.board[move[0]][move[1]] = "O" if self.letter == "X" else "X"
        image = await self.bot.loop.run_in_executor(None, self.puzzle.display)
        if self.puzzle.check_win() == -1 and all(button.disabled for button in self._buttons):
            points = self.puzzle.points
            member = interaction.user
            assert isinstance(member, discord.Member)  # skipcq: BAN-B101
            gained_points = await self.bot.give_game_points(member, "tictactoe", points.participation, points.bonus)
            max_points = points.participation + points.bonus
            embed = discord.Embed(
                title="Draw!",
                description=f"The game ended in a draw in "
                f"{utcnow().replace(microsecond=0) - self.time.replace(microsecond=0)} seconds! "
                f"You gained {gained_points} reputation. "
                f"{'(Daily Cap Reached)' if gained_points != max_points else ''}",
                color=discord.Color.gold(),
            ).set_image(url="attachment://tictactoe.png")
            embed.set_footer(text="Start playing by typing /programs tictactoe")
            self.disable()
            await interaction.edit_original_message(attachments=[image], embed=embed, view=self)
            return
        if self.puzzle.check_win() == 0:
            points = self.puzzle.points
            member = interaction.user
            assert isinstance(member, discord.Member)  # skipcq: BAN-B101
            gained_points = await self.bot.give_game_points(member, "tictactoe", points.participation, points.bonus)
            max_points = points.participation + points.bonus
            embed = discord.Embed(
                title="You Lost!",
                description=f"You lost the game in "
                f"{utcnow().replace(microsecond=0) - self.time.replace(microsecond=0)} seconds!"
                f" You gained {gained_points} reputation. "
                f"{'(Daily Cap Reached)' if gained_points != max_points else ''}",
                color=discord.Color.red(),
            ).set_image(url="attachment://tictactoe.png")
            embed.set_footer(text="Start playing by typing /programs tictactoe")
            self.disable()
            await interaction.edit_original_message(attachments=[image], embed=embed, view=self)
            return
        await interaction.edit_original_message(attachments=[image], view=self)

    @ui.button(style=ButtonStyle.green, emoji="✅")
    async def top_left(self, interaction: Interaction, button: ui.Button):
        """Call when top left button is pressed.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 0, 0)

    @ui.button(style=ButtonStyle.green, emoji="✅")
    async def top_mid(self, interaction: Interaction, button: ui.Button):
        """Call when top middle button is pressed.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 0, 1)

    @ui.button(style=ButtonStyle.green, emoji="✅")
    async def top_right(self, interaction: Interaction, button: ui.Button):
        """Call when top right button is pressed.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 0, 2)

    # noinspection PyUnusedLocal
    @ui.button(label="Cancel", style=ButtonStyle.danger)
    async def cancel(self, interaction: Interaction, button: ui.Button):  # skipcq: PYL-W0613
        """Call when cancel button is pressed.

        Parameters
        ----------
        interaction : discord.Interaction
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

    @ui.button(style=ButtonStyle.green, emoji="✅", row=1)
    async def mid_left(self, interaction: Interaction, button: ui.Button):
        """Call when middle left button is pressed.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 1, 0)

    @ui.button(style=ButtonStyle.green, emoji="✅", row=1)
    async def mid_mid(self, interaction: Interaction, button: ui.Button):
        """Call when middle_middle button is pressed.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 1, 1)

    @ui.button(style=ButtonStyle.green, emoji="✅", row=1)
    async def mid_right(self, interaction: Interaction, button: ui.Button):
        """Call when middle right button is pressed.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 1, 2)

    @ui.button(style=ButtonStyle.green, emoji="✅", row=2)
    async def bot_left(self, interaction: Interaction, button: ui.Button):
        """Call when bottom left button is pressed.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 2, 0)

    @ui.button(style=ButtonStyle.green, emoji="✅", row=2)
    async def bot_mid(self, interaction: Interaction, button: ui.Button):
        """Call when bottom middle button is pressed.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 2, 1)

    @ui.button(style=ButtonStyle.green, emoji="✅", row=2)
    async def bot_right(self, interaction: Interaction, button: ui.Button):
        """Call when bottom right button is pressed.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 2, 2)
