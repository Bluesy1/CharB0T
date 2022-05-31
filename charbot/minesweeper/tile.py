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
"""Abstract Base Class for Minesweeper."""
from . import Emoji, TileType, errors


class Tile:
    """Tile"""

    def __init__(self, tile_type: TileType, value: int):
        """Init the tile"""
        self._tile_type = tile_type
        self._emoji = Emoji.COVERED
        self._value = value
        self._is_revealed = False
        self._is_flagged = False

    def __str__(self) -> str:
        """String representation of the tile"""
        return self.emoji.value

    def __repr__(self) -> str:
        """Repr of the tile"""
        return (
            f"<Tile type={self.tile_type.name}, revealed={self.is_revealed}, flagged={self.is_flagged}, "
            f"emoji={self.emoji.value}>"
        )

    @property
    def is_mine(self) -> bool:
        """Is the tile a mine"""
        return self._tile_type == TileType.MINE

    @property
    def is_revealed(self) -> bool:
        """Is the tile revealed"""
        return self._is_revealed

    @property
    def is_flagged(self) -> bool:
        """Is the tile flagged"""
        return self._is_flagged

    @property
    def tile_type(self) -> TileType:
        """Type of the tile"""
        return self._tile_type

    @property
    def emoji(self) -> Emoji:
        """Emoji of the tile"""
        return self._emoji

    @property
    def value(self) -> int:
        """Value of the tile, ie how many mines are around the tile"""
        return self._value

    def reveal(self) -> bool:
        """Reveal the tile

        Returns
        -------
        bool
            True if the tile is empty and flood fill is needed, False otherwise

        Raises
        ------
        MineExplodedError
            If the tile is a mine
        """
        if self.is_mine:
            raise errors.MineExplodedError()
        self._is_revealed = True
        if self._value == 0:
            self._emoji = Emoji.EMPTY
            return True
        else:
            self._emoji = Emoji(f"{self._value}\N{combining enclosing keycap}")
            return False
