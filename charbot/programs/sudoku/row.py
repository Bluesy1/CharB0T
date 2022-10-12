# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
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
