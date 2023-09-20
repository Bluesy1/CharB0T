# -*- coding: utf-8 -*-
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

    __slots__ = ("_row1", "_row2", "_row3")

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
        return [*self._row1, *self._row2, *self._row3]

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
