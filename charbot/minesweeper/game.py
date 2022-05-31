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
import random
from typing import Callable

import numpy as np

from . import Coordinate, MineSweeperBoard, MineSweeperRow, Tile, TileType, errors


class Minesweeper:
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
