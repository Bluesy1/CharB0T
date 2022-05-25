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
"""Tic-tac-toe easy class."""
import math
from io import BytesIO

import discord
from PIL import Image

from . import GridPositions, PilOffsets, Points, TicTacABC


class TicTacEasy(TicTacABC):
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
    :class:`TicTacHard`
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
            return Points(participation=1, bonus=1)
        if win_state == 0:
            return Points(participation=0, bonus=0)
        return Points(participation=1, bonus=0)

    def _check_row_and_cols(self) -> int:
        """Check if there is a winner in the rows and columns.

        Returns
        -------
        int
            -1 if no one has won.
            1 if the player has won.
            0 if the computer has won.
        """
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
        return -1

    def _check_diagonals(self) -> int:
        """Check if there is a winner in the diagonals.

        Returns
        -------
        int
            -1 if no one has won.
            1 if the player has won.
            0 if the computer has won.
        """
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
        rows = self._check_row_and_cols()
        if rows != -1:
            return rows
        return self._check_diagonals()

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
        grid = Image.open("charbot/media/tictactoe/grid.png", "r").convert("RGBA")
        cross = Image.open("charbot/media/tictactoe/X.png", "r")
        circle = Image.open("charbot/media/tictactoe/O.png", "r")
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
