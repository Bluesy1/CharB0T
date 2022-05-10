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
"""Tic-tac-toe common classes."""
import abc
from enum import Enum
from typing import NamedTuple

import discord


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
