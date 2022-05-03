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
"""Tictactoe cog."""
import abc
import math
from enum import Enum
from io import BytesIO
from typing import NamedTuple, Final

import discord
from discord import ui, ButtonStyle, app_commands
from discord.ext import commands
from discord.utils import utcnow
from PIL import Image

from main import CBot


ALLOWED_ROLES: Final = (
    337743478190637077,
    685331877057658888,
    969629622453039104,
    969629628249563166,
    969629632028614699,
    969628342733119518,
    969627321239760967,
)

CHANNEL_ID: Final[int] = 969972085445238784


class PilOffsets(Enum):
    """Enum for PIL Offsets."""

    TOP_LEFT = (0, 0)
    TOP_MIDDLE = (179, 0)
    TOP_RIGHT = (355, 0)
    MIDDLE_LEFT = (0, 179)
    MIDDLE_MIDDLE = (179, 179)
    MIDDLE_RIGHT = (355, 179)
    BOTTOM_LEFT = (0, 357)
    BOTTOM_MIDDLE = (179, 357)
    BOTTOM_RIGHT = (355, 357)


class GridPositions(Enum):
    """Enum for Grid Positions."""

    TOP_LEFT = "(0, 0)"
    TOP_MIDDLE = "(0, 1)"
    TOP_RIGHT = "(0, 2)"
    MIDDLE_LEFT = "(1, 0)"
    MIDDLE_MIDDLE = "(1, 1)"
    MIDDLE_RIGHT = "(1, 2)"
    BOTTOM_LEFT = "(2, 0)"
    BOTTOM_MIDDLE = "(2, 1)"
    BOTTOM_RIGHT = "(2, 2)"


class Points(NamedTuple):
    """NamedTuple for Points."""

    participation: int
    bonus: int


class TicTacABC(abc.ABC):
    """Abstract class for TicTac.

    Methods
    -------
    display()
        Render the board as a discord.File object.
    move(x: int, y: int)
        Parse a player's move.
    check_win()
        Check if the game has been won.
    next()
        Make an AI move.
    """

    @property
    @abc.abstractmethod
    def letter(self) -> str:
        """Return the letter of the player."""

    @property
    @abc.abstractmethod
    def points(self) -> Points:
        """Return the points of the player."""

    @abc.abstractmethod
    def display(self) -> discord.File:
        """Return an image of the board.

        Returns
        -------
        discord.File
            The image of the board, represented as a discord.File object.
        """

    @abc.abstractmethod
    def move(self, x: int, y: int) -> bool:
        """Record a move.

        Parameters
        ----------
        x : int
            The x position of the move.
        y : int
            The y position of the move.
        """

    @abc.abstractmethod
    def check_win(self) -> int:
        """Check if the player has won.

        Returns
        -------
        int
            0 if no one has won.
            1 if the player has won.
            -1 if the computer has won.
        """

    @abc.abstractmethod
    def next(self) -> tuple[int, int]:
        """Make a move, and return the cell that was played.

        Returns
        -------
        tuple[int, int]
            The x and y position of the move.
        """


class TicTacHard(TicTacABC):
    """Hard AI implementation of TicTacToe.

    Parameters
    ----------
    pick : str
        The letter of the player.
    sz : int = 3
        The size of the board.

    Attributes
    ----------
    dim_sz : int
        The size of the board.
    board : list[list[str]]
        The board.
    pick : str
        The letter of the player.

    Methods
    -------
    display()
        Render the board as a discord.File object.
    move(x: int, y: int)
        Parse a player's move.
    check_win()
        Check if the game has been won.
    next()
        Make an AI move.

    See Also
    --------
    :class:`TicTacEasy`
        An implementation with an easier AI.
    :class:`TicTacABC`
        The abstract class for TicTac. All other implementations inherit from this class, or a subclass of it.
    """

    def __init__(self, pick, sz=3) -> None:
        self.pick = pick
        self.dim_sz = sz
        self.board = self.clear_board()

    def clear_board(self) -> list[list[str]]:
        """Clear the board.

        Returns
        -------
        list[list[str]]
            The cleared board.
        """
        board = [["blur" for _ in range(self.dim_sz)] for _ in range(self.dim_sz)]
        # made a 3x3 by-default board
        return board

    @property
    def letter(self) -> str:
        """Return the letter of the player.

        Returns
        -------
        str
            The letter of the player.
        """
        return self.pick

    @property
    def points(self) -> Points:
        """Return the points of the game.

        Returns
        -------
        Points
            The points of the game.
        """
        win_state = self.check_win()
        if win_state == 1:
            return Points(participation=1, bonus=3)
        if win_state == 0:
            return Points(participation=1, bonus=0)
        return Points(participation=1, bonus=2)

    # noinspection DuplicatedCode
    def check_win(self) -> int:
        """Check if a win state has been reached.

        Returns
        -------
        int
            -1 if no one has won.
            1 if the player has won.
            0 if the computer has won.
        """
        # 1 you won, 0 computer won, -1 tie
        # Flag syntax -> first player no. ,
        # User is Player#1 ;
        # Check set 1 -> row and '\' diagonal & Check set 2 -> col and '/' diagonal

        for i in range(0, self.dim_sz):  # Rows
            flag11 = True
            flag21 = True

            flag12 = True
            flag22 = True
            for j in range(0, self.dim_sz):

                ch2 = self.board[i][j]
                ch1 = self.board[j][i]
                # Row
                if ch1 == self.pick:  # if it's mine, computer didn't make it
                    flag21 = False
                elif ch1 == "blur":  # if it's blank no one made it
                    flag11 = False
                    flag21 = False
                else:
                    flag11 = False  # else I didn't make it

                if ch2 == self.pick:  # Same but for Col
                    flag22 = False
                elif ch2 == "blur":
                    flag12 = False
                    flag22 = False
                else:
                    flag12 = False

            if flag11 is True or flag12 is True:  # I won
                return 1
            if flag21 is True or flag22 is True:  # Computer Won
                return 0

        # Diagonals#
        flag11 = True
        flag21 = True

        flag12 = True
        flag22 = True
        for i in range(0, self.dim_sz):

            ch2 = self.board[i][i]
            ch1 = self.board[i][self.dim_sz - 1 - i]

            if ch1 == self.pick:
                flag21 = False
            elif ch1 == "blur":
                flag11 = False
                flag21 = False
            else:
                flag11 = False

            if ch2 == self.pick:
                flag22 = False
            elif ch2 == "blur":
                flag12 = False
                flag22 = False
            else:
                flag12 = False

        if flag11 or flag12:
            return 1
        if flag21 or flag22:
            return 0

        return -1

    def move(self, x: int, y: int) -> bool:
        """Record a move.

        Parameters
        ----------
        x : int
            The x position of the move.
        y : int
            The y position of the move.

        Returns
        -------
        bool
            True if the move was successful, False otherwise.
        """
        move = self._move_record(x, y)
        if isinstance(move, bool):
            return move
        return False

    def display(self) -> discord.File:
        """Return an image of the board.

        Returns
        -------
        :class:`discord.File`
            The image of the board, represented as a discord.File object.
        """
        grid = Image.open("media/tictactoe/grid.png", "r").convert("RGBA")
        cross = Image.open("media/tictactoe/X.png", "r")
        circle = Image.open("media/tictactoe/O.png", "r")
        for i in range(0, self.dim_sz):
            for j in range(0, self.dim_sz):
                if self.board[i][j] == "X":
                    grid.paste(cross, PilOffsets[GridPositions(f"({i}, {j})").name].value, cross)
                elif self.board[i][j] == "O":
                    grid.paste(circle, PilOffsets[GridPositions(f"({i}, {j})").name].value, circle)
        _bytes = BytesIO()
        grid.save(_bytes, format="PNG")
        _bytes.seek(0)
        return discord.File(_bytes, filename="tictactoe.png")

    def _move_record(self, r, c) -> str | bool:
        """Record a move.

        Parameters
        ----------
        r : int
            The x position of the move.
        c : int
            The y position of the move.

        Returns
        -------
        str | bool
            True on sucess, string error message on failure.
        """
        if r > self.dim_sz or c > self.dim_sz:
            return "Out of Bounds"
        if self.board[r][c] != "blur":
            return "Spot Pre-Occupied"
        self.board[r][c] = self.pick
        return True

    def next(self) -> tuple[int, int]:
        """Make a move, and return the cell that was played.

        Returns
        -------
        tuple[int, int]
            The x and y position of the move.
        """
        move = self._next_move("O" if self.letter == "X" else "X")
        if move["position"] is None:
            return -1, -1
        position = move["position"]
        assert isinstance(position, tuple)  # skipcq: BAN-B101
        self.board[position[0]][position[1]] = "O" if self.letter == "X" else "X"
        return position

    def _available_moves(self) -> list[tuple[int, int]]:
        """Return a list of available moves.

        Returns
        -------
        list[tuple[int, int]]
            A list of available moves.
        """
        available_moves = []
        for i in range(0, self.dim_sz):
            for j in range(0, self.dim_sz):
                if self.board[i][j] == "blur":
                    available_moves.append((i, j))
        return available_moves

    def _empty_squares(self) -> int:
        """Return the number of empty squares.

        Returns
        -------
        int
            The number of empty squares.
        """
        empty_squares = 0
        for i in range(0, self.dim_sz):
            for j in range(0, self.dim_sz):
                if self.board[i][j] == "blur":
                    empty_squares += 1
        return empty_squares

    # noinspection PyAssignmentToLoopOrWithParameter,DuplicatedCode
    def _next_move(self, player: str) -> dict[str, tuple[int, int] | int | float | None]:
        """Make a move, and return the cell that was played.

        Returns
        -------
        tuple[int, int] | tuple[list[int], list[int]]
            The cell that was played.
        """
        other_player = self.letter
        max_player = "O" if self.letter == "X" else "X"  # yourself

        # first we want to check if the previous move is a winner
        if self.check_win() == 1:
            return {
                "position": None,
                "score": 1 * (self._empty_squares() + 1)
                if other_player == max_player
                else -1 * (self._empty_squares() + 1),
            }
        if len(self._available_moves()) == 0:
            return {"position": None, "score": 0}

        if player == max_player:
            best = {"position": None, "score": -math.inf}  # each score should maximize
        else:
            best = {"position": None, "score": math.inf}  # each score should minimize
        for possible_move in self._available_moves():
            self.board[possible_move[0]][possible_move[1]] = player
            sim_score = self._next_move(other_player)  # simulate a game after making that move

            # undo move
            self.board[possible_move[0]][possible_move[1]] = "blur"
            sim_score["position"] = possible_move  # this represents the move optimal next move

            if player == max_player:  # X is max player
                sim_score_val = sim_score["score"]
                best_val = best["score"]
                assert isinstance(sim_score_val, (float, int))  # skipcq: BAN-B101
                assert isinstance(best_val, (float, int))  # skipcq: BAN-B101
                if sim_score_val > best_val:
                    best = sim_score
            else:
                sim_score_val = sim_score["score"]
                best_val = best["score"]
                assert isinstance(sim_score_val, (float, int))  # skipcq: BAN-B101
                assert isinstance(best_val, (float, int))  # skipcq: BAN-B101
                if sim_score_val < best_val:
                    best = sim_score
        return best


class TicTacEasy(TicTacHard):
    """Adaptation of TicTacHard to an easier version.

    See Also
    --------
    :class:`TicTacHard`
        For the full documentation and implementation.
    """

    def next(self) -> tuple[int, int]:
        """Make a move, and return the cell that was played.

        Returns
        -------
        tuple[int, int]
            The x and y position of the move.
        """
        move = self._next_move_easy()
        if isinstance(move[0], int):
            return move  # type: ignore #IDK what pyright's on here'
        _move = move[0]
        __move = move[1]
        assert isinstance(_move, list)  # skipcq: BAN-B101
        assert isinstance(__move, list)  # skipcq: BAN-B101
        return _move[0], __move[0]

    def _next_move_easy(self) -> tuple[int, int] | tuple[list[int], list[int]]:
        """Make a move, and return the cell that was played.

        Returns
        -------
        tuple[int, int] | tuple[list[int], list[int]]
            The cell that was played.
        """
        available_moves = []  # will carry all available moves
        player_win_spot = []  # if player (user Wins)
        comp_pick = "O"
        if self.pick == "O":
            comp_pick = "X"
        for i in range(0, self.dim_sz):
            for j in range(0, self.dim_sz):
                if self.board[i][j] == "blur":  # BLANK
                    t = (i, j)
                    available_moves.append(t)  # add it to available moves
                    self.board[i][j] = comp_pick  # Check if I (Computer can win)
                    if self.check_win() == 0:  # Best Case I(Computer) win!
                        return i, j
                    self.board[i][j] = self.pick
                    if self.check_win() == 1:  # Second Best Case, he (player) didn't won
                        player_win_spot.append(t)
                    self.board[i][j] = "blur"

        if self.board[0][0] == self.pick and self.board[2][2] == self.pick:
            if self.board[0][2] == "blur":
                self.board[0][2] = comp_pick
                return 0, 2
            if self.board[2][0] == "blur":
                self.board[2][0] = comp_pick
                return 2, 0
        if self.board[0][2] == self.pick and self.board[2][0] == self.pick:
            if self.board[0][0] == "blur":
                self.board[0][0] = comp_pick
                return 0, 0
            if self.board[2][2] == "blur":
                self.board[2][2] = comp_pick
                return 2, 2
        if len(player_win_spot) != 0:
            self.board[player_win_spot[0][0]][player_win_spot[0][1]] = comp_pick
            return player_win_spot[0][0], player_win_spot[0][1]
        if len(available_moves) == 1:
            self.board[available_moves[0][0]][available_moves[0][1]] = comp_pick
            return [available_moves[0][0]], [available_moves[0][1]]
        if len(available_moves) == 0:
            return -1, -1

        c1, c2 = self.dim_sz // 2, self.dim_sz // 2
        if (c1, c2) in available_moves:  # CENTER
            self.board[c1][c2] = comp_pick
            return c1, c2
        for i in range(c1 - 1, -1, -1):  # IN TO OUT
            gap = c1 - i
            # checking  - 4 possibilities at max
            # EDGES
            if (c1 - gap, c2 - gap) in available_moves:
                self.board[c1 - gap][c2 - gap] = comp_pick
                return c1 - gap, c2 - gap
            if (c1 - gap, c2 + gap) in available_moves:
                self.board[c1 - gap][c2 + gap] = comp_pick
                return c1 - gap, c2 + gap
            if (c1 + gap, c2 - gap) in available_moves:
                self.board[c1 + gap][c2 - gap] = comp_pick
                return c1 + gap, c2 - gap
            if (c1 + gap, c2 + gap) in available_moves:
                self.board[c1 + gap][c2 + gap] = comp_pick
                return c1 + gap, c2 + gap

            # Four Lines

            for j in range(0, gap):
                if (c1 - gap, c2 - gap + j) in available_moves:  # TOP LEFT TO TOP RIGHT
                    self.board[c1 - gap][c2 - gap + j] = comp_pick
                    return c1 - gap, c2 - gap + j
                if (
                    c1 + gap,
                    c2 - gap + j,
                ) in available_moves:  # BOTTOM LEFT TO BOTTOM RIGHT
                    self.board[c1 + gap][c2 - gap + j] = comp_pick
                    return c1 + gap, c2 - gap + j
                if (c1 - gap, c2 - gap) in available_moves:  # LEFT TOP TO LEFT BOTTOM
                    self.board[c1 - gap + j][c2 - gap] = comp_pick
                    return c1 - gap + j, c2 - gap
                if (
                    c1 - gap + j,
                    c2 + gap,
                ) in available_moves:  # RIGHT TOP TO RIGHT BOTTOM
                    self.board[c1 - gap + j][c2 + gap] = comp_pick
                    return c1 - gap + j, c2 + gap
        raise RuntimeError("No moves available")

    @property
    def points(self) -> Points:
        """Return the points of the game.

        Returns
        -------
        Points
            The points of the game.
        """
        win_state = self.check_win()
        if win_state == 1:
            return Points(participation=1, bonus=2)
        if win_state == 0:
            return Points(participation=1, bonus=0)
        return Points(participation=1, bonus=1)


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

    def __init__(self, bot: CBot, letter: str = "X", easy: bool = True):
        super(TicTacView, self).__init__(timeout=300)
        self.letter = letter
        self.puzzle: TicTacHard = TicTacEasy(self.letter) if easy else TicTacHard(self.letter)
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

    def display(self) -> None:
        """DOCSTRING."""
        line1 = ""
        for i in range(0, 3):
            for j in range(0, 2):
                if self.puzzle.board[i][j] == "blur":
                    line1 = line1 + "    |"
                else:
                    line1 = line1 + "  " + self.puzzle.board[i][j] + " |"
            if self.puzzle.board[i][3 - 1] == "blur":
                line1 = line1 + "    \n"
            else:
                line1 = line1 + "  " + self.puzzle.board[i][3 - 1] + " \n"
        print(line1, "\n\n")

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
        await interaction.response.defer()
        self.puzzle.move(x, y)
        print("Player:")
        self.display()
        button.disabled = True
        if self.puzzle.check_win() == 1:
            points = self.puzzle.points
            gained_points = await self.bot.give_game_points(interaction.user.id, points.participation, points.bonus)
            max_points = points.participation + points.bonus
            embed = discord.Embed(
                title="You Won!",
                description=f"You won the game in "
                f"{utcnow().replace(microsecond=0) - self.time.replace(microsecond=0)} seconds! "
                f"You gained {gained_points} reputation. "
                f"{'(Daily Cap Reached)' if gained_points != max_points else ''}",
                color=discord.Color.green(),
            )
            self.disable()
            image = await self.bot.loop.run_in_executor(self.bot.executor, self.puzzle.display)
            await interaction.edit_original_message(attachments=[])
            await interaction.edit_original_message(attachments=[image], embed=embed, view=self)
            return
        if isinstance(self.puzzle, TicTacEasy):
            move = self.puzzle.next()
        else:
            move = await self.bot.loop.run_in_executor(None, self.puzzle.next)
        print("Computer:")
        self.display()
        self._buttons[move[0] * 3 + move[1]].disabled = True
        image = await self.bot.loop.run_in_executor(self.bot.executor, self.puzzle.display)
        if self.puzzle.check_win() == -1 and all(button.disabled for button in self._buttons):
            points = self.puzzle.points
            gained_points = await self.bot.give_game_points(interaction.user.id, points.participation, points.bonus)
            max_points = points.participation + points.bonus
            embed = discord.Embed(
                title="Draw!",
                description=f"The game ended in a draw in "
                f"{utcnow().replace(microsecond=0) - self.time.replace(microsecond=0)} seconds! "
                f"You gained {gained_points} reputation. "
                f"{'(Daily Cap Reached)' if gained_points != max_points else ''}",
                color=discord.Color.gold(),
            )
            self.disable()
            await interaction.edit_original_message(attachments=[])
            await interaction.edit_original_message(attachments=[image], embed=embed, view=self)
            return
        if self.puzzle.check_win() == 0:
            points = self.puzzle.points
            gained_points = await self.bot.give_game_points(interaction.user.id, points.participation, points.bonus)
            max_points = points.participation + points.bonus
            embed = discord.Embed(
                title="You Lost!",
                description=f"You lost the game in "
                f"{utcnow().replace(microsecond=0) - self.time.replace(microsecond=0)} seconds!"
                f" You gained {gained_points} reputation. "
                f"{'(Daily Cap Reached)' if gained_points != max_points else ''}",
                color=discord.Color.red(),
            )
            self.disable()
            await interaction.edit_original_message(attachments=[])
            await interaction.edit_original_message(attachments=[image], embed=embed, view=self)
            return
        await interaction.edit_original_message(attachments=[], view=self)
        await interaction.edit_original_message(attachments=[image])

    @ui.button(style=ButtonStyle.green, emoji="✅")
    async def top_left(self, interaction: discord.Interaction, button: ui.Button):
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
    async def top_mid(self, interaction: discord.Interaction, button: ui.Button):
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
    async def top_right(self, interaction: discord.Interaction, button: ui.Button):
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
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):  # skipcq: PYL-W0613
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
            title="Tic Tac Toe",
            description=f"Cancelled, time taken: {utcnow().replace(microsecond=0) - self.time.replace(microsecond=0)}",
            color=discord.Color.red(),
        )
        await interaction.response.edit_message(embed=embed)

    @ui.button(style=ButtonStyle.green, emoji="✅", row=1)
    async def mid_left(self, interaction: discord.Interaction, button: ui.Button):
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
    async def mid_mid(self, interaction: discord.Interaction, button: ui.Button):
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
    async def mid_right(self, interaction: discord.Interaction, button: ui.Button):
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
    async def bot_left(self, interaction: discord.Interaction, button: ui.Button):
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
    async def bot_mid(self, interaction: discord.Interaction, button: ui.Button):
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
    async def bot_right(self, interaction: discord.Interaction, button: ui.Button):
        """Call when bottom right button is pressed.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.move(interaction, button, 2, 2)


class TicTacCog(commands.Cog):
    """Tic Tac Toe cog.

    Parameters
    ----------
    bot : CBot
        The bot instance.

    Attributes
    ----------
    bot : CBot
        The bot instance.
    """

    def __init__(self, bot: CBot):
        self.bot = bot

    @app_commands.command(name="tictactoe", description="Play a game of Tic Tac Toe!")
    @app_commands.describe(
        easy="Set this to false for a harder variant of the AI.", letter="Do you want to play as X or O?"
    )
    @app_commands.choices(
        letter=[
            app_commands.Choice(name="X", value="X"),
            app_commands.Choice(name="O", value="O"),
        ]
    )
    @app_commands.guilds(225345178955808768)
    async def tictaccommand(self, interaction: discord.Interaction, letter: app_commands.Choice[str], easy: bool):
        """Tic Tac Toe! command.

        This command is for playing a game of Tic Tac Toe.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object for the command.
        letter : app_commands.Choice[str]
            The letter to play as.
        hard : bool
            Whether to use the hard AI.
        """
        # noinspection DuplicatedCode
        channel = interaction.channel
        assert isinstance(channel, discord.TextChannel)  # skipcq: BAN-B101
        if (
            interaction.guild is None
            or not any(role.id in ALLOWED_ROLES for role in interaction.user.roles)  # type: ignore
            or not channel.id == CHANNEL_ID
        ):
            await interaction.response.send_message(
                "You must be at least level 5 to participate in the giveaways system and be in "
                "a thread of <#969972085445238784>.",
                ephemeral=True,
            )
            return
        await interaction.response.defer(ephemeral=True)
        game = TicTacView(self.bot, letter.value, easy)
        move = await self.bot.loop.run_in_executor(None, game.puzzle.next)
        # noinspection PyProtectedMember
        game._buttons[move[0] * 3 + move[1]].disabled = True  # skipcq: PYL-W0212
        image = await self.bot.loop.run_in_executor(None, game.puzzle.display)
        await interaction.followup.send(file=image, view=game)


async def setup(bot: CBot):
    """Initialize the cog.

    Parameters
    ----------
    bot: CBot
        The bot to attach the cog to.
    """
    await bot.add_cog(TicTacCog(bot), guild=discord.Object(id=225345178955808768), override=True)
