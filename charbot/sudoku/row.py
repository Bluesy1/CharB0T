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
"""Row class."""

from . import Cell


class Row:
    """Represents a row of cells in the sudoku board.

    Parameters
    ----------
    cells : list[Cell]
        The cells in the row.

    Attributes
    ----------
    cells : list[Cell]
    solved : bool

    Methods
    -------
    clear()
        Resets the row.
    """

    def __init__(self, cells: list[Cell]):
        if len(cells) != 9:
            raise ValueError("Row must have exactly 9 cells.")
        self._cells = cells

    def __repr__(self):
        """Return a string representation of the row."""
        return f"<Row cells={self.cells}>"

    def __eq__(self, other):
        """Two rows are equal if they have the same cells."""
        return [cell.id for cell in self.cells] == [cell.id for cell in other.cells]

    def __getitem__(self, item):
        """Get cell(s) in the row."""
        return self.cells[item]

    @property
    def cells(self) -> list[Cell]:
        """Cells in the row."""
        return self._cells

    @property
    def solved(self) -> bool:
        """Whether the row is solved."""
        return all(cell.value != 0 for cell in self.cells) and len({cell.value for cell in self.cells}) == 9

    def clear(self) -> None:
        """Reset the row."""
        for cell in self.cells:
            if cell.editable:
                cell.clear()
