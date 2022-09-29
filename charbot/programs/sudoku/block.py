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
"""Block class."""

from . import Cell


class Block:
    """Represents a block of cells in the sudoku board.

    Parameters
    ----------
    cells : list[Cell]
        The cells in the block.

    Attributes
    ----------
    cells : list[Cell]
    solved : bool

    Methods
    -------
    clear()
        Resets the block.
    """

    def __init__(self, cells: list[Cell]):
        if len(cells) != 9:
            raise ValueError("Block must have exactly 9 cells.")
        self._row1 = cells[:3]
        self._row2 = cells[3:6]
        self._row3 = cells[6:9]

    def __getitem__(self, item):
        """Get cell(s) in the block."""
        return self.cells[item]

    def __repr__(self):
        """Represent the block as a string."""
        return f"<Block cells={self.cells}>"

    def __eq__(self, other):
        """Two blocks are equal if they have the same cells."""
        return [cell.id for cell in self.cells] == [cell.id for cell in other.cells]

    @property
    def cells(self) -> list[Cell]:
        """Cells in the block."""
        return self._row1 + self._row2 + self._row3

    @property
    def solved(self) -> bool:
        """Whether the block is solved."""
        return all(cell.value != 0 for cell in self.cells) and len({cell.value for cell in self.cells}) == 9

    @property
    def selected(self) -> bool:
        """Whether the block is selected."""
        return all(n.selected for n in self.cells)

    @selected.setter
    def selected(self, value: bool) -> None:
        """Set the selected state of the block.

        Parameters
        ----------
        value : bool
            Whether the block is selected.
        """
        if not isinstance(value, bool):
            raise TypeError("Selected must be a bool.")
        for cell in self.cells:
            cell.selected = value

    def clear(self) -> None:
        """Reset the block."""
        for cell in self.cells:
            if cell.editable:
                cell.clear()
