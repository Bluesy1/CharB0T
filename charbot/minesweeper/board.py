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
"""Minesweeper game tuples."""
from dataclasses import dataclass
from typing import overload

from . import Coordinate, Tile


@dataclass
class MineSweeperRow:
    """
    A row of the mine sweeper board
    """

    zero: Tile
    one: Tile
    two: Tile
    three: Tile
    four: Tile
    five: Tile
    six: Tile
    seven: Tile
    eight: Tile
    nine: Tile
    ten: Tile
    eleven: Tile
    twelve: Tile

    def __getitem__(self, item: Coordinate) -> Tile:
        return getattr(self, item.name)


@dataclass
class MineSweeperBoard:
    """
    The mine sweeper board
    """

    zero: MineSweeperRow
    one: MineSweeperRow
    two: MineSweeperRow
    three: MineSweeperRow
    four: MineSweeperRow
    five: MineSweeperRow
    six: MineSweeperRow
    seven: MineSweeperRow
    eight: MineSweeperRow
    nine: MineSweeperRow
    ten: MineSweeperRow
    eleven: MineSweeperRow
    twelve: MineSweeperRow

    @overload
    def __getitem__(self, item: Coordinate) -> MineSweeperRow:
        ...

    @overload
    def __getitem__(self, item: tuple[Coordinate, Coordinate]) -> Tile:
        ...

    @overload
    def __getitem__(self, item: int) -> MineSweeperRow:
        ...

    @overload
    def __getitem__(self, item: tuple[int, int]) -> Tile:
        ...

    def __getitem__(
        self, item: Coordinate | int | tuple[Coordinate, Coordinate] | tuple[int, int]
    ) -> MineSweeperRow | Tile:
        if isinstance(item, Coordinate):
            return getattr(self, item.name)
        elif isinstance(item, int):
            return getattr(self, Coordinate(item).name)
        elif isinstance(item, tuple):
            row, col = item
            if isinstance(row, Coordinate) and isinstance(col, Coordinate):
                return getattr(self, row.name)[col.name]
            elif isinstance(row, int) and isinstance(col, int):
                return getattr(self, Coordinate(row).name)[Coordinate(col).name]
        else:
            raise TypeError(f"Invalid type for item: {type(item)}")
