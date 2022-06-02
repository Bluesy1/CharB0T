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
"""Minesweeper game board."""
from dataclasses import dataclass
from typing import Generator, overload

from . import Coordinate, Tile


__all__ = ("MineSweeperBoard", "MineSweeperRow")


@dataclass
class MineSweeperRow:
    """A row of the mine sweeper board."""

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

    def __iter__(self) -> Generator[Tile, None, None]:
        """Iterate over all tiles in the row."""
        yield self.zero
        yield self.one
        yield self.two
        yield self.three
        yield self.four
        yield self.five
        yield self.six
        yield self.seven
        yield self.eight
        yield self.nine
        yield self.ten
        yield self.eleven
        yield self.twelve

    def __getitem__(self, item: Coordinate) -> Tile:
        """Get the tile at the given coordinate."""
        return getattr(self, item.name)


@dataclass
class MineSweeperBoard:
    """The mine sweeper board."""

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

    def __iter__(self) -> Generator[MineSweeperRow, None, None]:
        """Iterate over the rows of the board."""
        yield self.zero
        yield self.one
        yield self.two
        yield self.three
        yield self.four
        yield self.five
        yield self.six
        yield self.seven
        yield self.eight
        yield self.nine
        yield self.ten
        yield self.eleven
        yield self.twelve

    @overload
    def __getitem__(self, item: Coordinate) -> MineSweeperRow:  # noqa: D105
        ...

    @overload
    def __getitem__(self, item: tuple[Coordinate, Coordinate]) -> Tile:  # noqa: D105
        ...

    @overload
    def __getitem__(self, item: int) -> MineSweeperRow:  # noqa: D105
        ...

    @overload
    def __getitem__(self, item: tuple[int, int]) -> Tile:  # noqa: D105
        ...

    def __getitem__(
        self, item: Coordinate | int | tuple[Coordinate, Coordinate] | tuple[int, int]
    ) -> MineSweeperRow | Tile:
        """Get a row or tile of the board."""
        if isinstance(item, Coordinate):
            _item = getattr(self, item.name)
        elif isinstance(item, int):
            _item = getattr(self, Coordinate(item).name)
        elif isinstance(item, tuple):
            row, col = item
            if isinstance(row, Coordinate) and isinstance(col, Coordinate):
                _item = getattr(self, row.name)[col.name]
            elif isinstance(row, int) and isinstance(col, int):
                _item = getattr(self, Coordinate(row).name)[Coordinate(col).name]
            else:
                raise TypeError(f"Invalid tuple: {item}")
        else:
            raise TypeError(f"Invalid type for item: {type(item)}")
        if _item is not None:
            return _item
        raise KeyError(f"Invalid key: {item}")
