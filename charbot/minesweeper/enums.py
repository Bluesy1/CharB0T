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
"""Enums for Minesweeper."""
from enum import Enum


class TileType(Enum):
    """
    Enum for the different types of tiles
    """

    EMPTY = 0
    MINE = 1
    FLAG = 2
    QUESTION = 3
    EXPLODED = 4
    COVERED = 5


class GameState(Enum):
    """
    Enum for the different states of the game
    """

    IN_PROGRESS = 0
    WON = 1
    LOST = 2


class Emoji(Enum):
    """
    Enum for the different emojis
    """

    FLAG = "🚩"
    QUESTION = "❓"
    CURSOR = "🔸"
    EXPLODED = "💥"
    MINE = "💣"
    COVERED = "🟨"
    EMPTY = "🟦"
    ZERO = "0\N{combining enclosing keycap}"
    ONE = "1\N{combining enclosing keycap}"
    TWO = "2\N{combining enclosing keycap}"
    THREE = "3\N{combining enclosing keycap}"
    FOUR = "4️\N{combining enclosing keycap}"
    FIVE = "5️\N{combining enclosing keycap}"
    SIX = "6️\N{combining enclosing keycap}"
    SEVEN = "7️\N{combining enclosing keycap}"
    EIGHT = "8️\N{combining enclosing keycap}"


class Coordinate(Enum):
    """
    Enum for the different coordinates
    """

    zero = 0
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5
    six = 6
    seven = 7
    eight = 8
    nine = 9
    ten = 10
    eleven = 11
    twelve = 12
