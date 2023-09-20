# -*- coding: utf-8 -*-
"""Column class."""

from . import Cell


class Column:
    """Represents a column of cells in the sudoku board.

    Parameters
    ----------
    cells : list[Cell]
        The cells in the column.

    Attributes
    ----------
    cells : list[Cell]
    solved : bool

    Methods
    -------
    clear()
        Resets the column.
    """

    __slots__ = ("_cells",)

    def __init__(self, cells: list[Cell]):
        if len(cells) != 9:
            raise ValueError("Column must have exactly 9 cells.")
        self._cells = cells

    def __repr__(self):
        """Return a string representation of the column."""
        return f"<Column cells={self.cells}>"

    def __getitem__(self, item):
        """Get cell(s) in the column."""
        return self.cells[item]

    def __eq__(self, other):
        """Two columns are equal if they have the same cells."""
        return [cell.id for cell in self.cells] == [cell.id for cell in other.cells]

    @property
    def cells(self) -> list[Cell]:
        """Cells in the column."""
        return self._cells

    @property
    def solved(self) -> bool:
        """Whether the column is solved."""
        return all(cell.value != 0 for cell in self.cells) and len({cell.value for cell in self.cells}) == 9

    def clear(self) -> None:
        """Reset the column."""
        for cell in self.cells:
            if cell.editable:
                cell.clear()
