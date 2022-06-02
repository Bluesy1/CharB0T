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
"""MineSweeper game."""
import asyncio
import random
from typing import Callable, Final

import numpy as np

from . import Coordinate, MineSweeperBoard, MineSweeperRow, Tile, TileType, errors


class Minesweeper:

    __indicator_emojis__: Final[list[str]] = [
        "0\N{combining enclosing keycap}",
        "1\N{combining enclosing keycap}",
        "2\N{combining enclosing keycap}",
        "3\N{combining enclosing keycap}",
        "4\N{combining enclosing keycap}",
        "5\N{combining enclosing keycap}",
        "6\N{combining enclosing keycap}",
        "7\N{combining enclosing keycap}",
        "8\N{combining enclosing keycap}",
        "9\N{combining enclosing keycap}",
        "\N{keycap ten}",
        ":regional_indicator_a:",
        ":regional_indicator_b:",
    ]

    def __init__(self, initial_row: Coordinate, initial_col: Coordinate):
        invalid = True
        while invalid:
            try:
                mines: int = random.randint(45, 12**2)
                mine_tiles = random.sample(range(0, 13**2), mines)
                _: Callable[[Coordinate, Coordinate], int] = lambda _row, _col: (_row.value * 13) + _col.value
                _board = np.array(
                    [
                        [TileType.MINE if _(row, col) in mine_tiles else TileType.EMPTY for row in Coordinate]
                        for col in Coordinate
                    ]
                )

                value: Callable[[np.ndarray, int, int], int] = lambda x, y, z: (
                    sum(
                        [
                            1
                            # fmt: off
                            for q in list(map(list, x[max(0, y - 1):min(12, y + 2), max(0, z - 1):min(12, z + 2)]))[0]
                            # fmt: on
                            if q == TileType.MINE
                        ],
                    )
                    - (1 if _board[y, z] == TileType.MINE else 0)
                )

                self.board: MineSweeperBoard = MineSweeperBoard(
                    *[
                        MineSweeperRow(
                            *[
                                Tile(_board[row.value, col.value], value(_board, row.value, col.value))
                                for col in Coordinate
                            ]
                        )
                        for row in Coordinate
                    ]
                )
                self.board[initial_row, initial_col].reveal()
            except errors.MineExplodedError:
                pass
            else:
                invalid = False

    def __str__(self) -> str:
        text = "⏹️" + "".join(self.__indicator_emojis__) + "\n"
        for i, row in enumerate(self.board):  # type: int, MineSweeperRow
            text += self.__indicator_emojis__[i]
            for tile in row:
                text += tile.emoji.value
            text += "\n"
        return text

    @staticmethod
    def floodfill(row: Coordinate, col: Coordinate) -> list[tuple[Coordinate, Coordinate]]:
        """Floodfill coordinate generator.

        Parameters
        ----------
        row : Coordinate
            Row of the tile to center the floodfill on
        col : Coordinate
            Column of the tile to center the floodfill on

        Returns
        -------
        list[tuple[Coordinate, Coordinate]]
            List of tiles to reveal
        """
        return [
            (Coordinate(row.value + x), Coordinate(col.value + y))
            for x in range(-1, 2)
            for y in range(-1, 2)
            if x != 0 and y != 0 and 0 <= row.value + x <= 12 and 0 <= col.value + y <= 12
        ]

    async def reveal(self, row: Coordinate, col: Coordinate) -> None:
        """Reveal a tile, and floodfill if appropriate.

        Parameters
        ----------
        row : Coordinate
            Row of the tile to reveal
        col : Coordinate
            Column of the tile to reveal

        Raises
        ------
        errors.MineExplodedError
            If the tile is a mine
        """
        if self.board[row, col].is_revealed:
            return
        floodfill = self.board[row, col].reveal()
        if floodfill:
            await asyncio.gather(*[self.reveal(*tile) for tile in self.floodfill(row, col)])

    def flag(self, row: Coordinate, col: Coordinate) -> bool:
        """Flag a tile.

        Parameters
        ----------
        row : Coordinate
            Row of the tile to flag
        col : Coordinate
            Column of the tile to flag

        Returns
        -------
        bool
            True if the tile was flagged, False if it was unflagged

        Raises
        ------
        errors.InvalidMoveError
            If the tile is revealed
        """
        return self.board[row, col].flag()

    def explode(self) -> None:
        """Explode the game."""
        for row in self.board:
            for tile in row:
                if tile.tile_type == TileType.MINE:
                    tile.explode()
