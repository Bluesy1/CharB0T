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
"""Cell class for Sudoku."""
from uuid import uuid4


class Cell:
    """Represents a cell in the sudoku board.

    Parameters
    ----------
    value : int
        The value of the cell.
    editable : bool
        Whether the cell is editable.

    Attributes
    ----------
    value : int
    editable : bool
    possible_values : set[int]

    Methods
    -------
    clear()
        Clears the cell.
    """

    def __init__(self, value: int, editable: bool):
        if value > 9 or value < 0:
            raise ValueError("Value must be between 0 and 9.")
        self._value = value
        self._editable = editable
        self._possible_values: set[int] = set(range(1, 10)) if editable else {value}
        self._selected = False
        self.id = uuid4()

    def __repr__(self):
        """Return a string representation of the cell."""
        return f"<Cell value={self.value} possible_values={self.possible_values} id={self.id}>"

    def __eq__(self, other):
        """Two cells are equal if they have the same value, and editibility."""
        return self.value == other.value and self.editable == other.editable

    def __hash__(self):
        """Return the hash of the cell."""
        return hash(f"{self.value}{self.editable}")

    @property
    def value(self) -> int:
        """Calue of the cell."""
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        """Set the value of the cell.

        Parameters
        ----------
        value : int
            The value to set the cell to.

        Raises
        ------
        ValueError
            If the value is not between 0 and 9, or if the cell is not editable.
        """
        if not self._editable:
            raise ValueError("Cannot set value of non-editable cell.")
        if value > 9 or value < 0:
            raise ValueError("Value must be between 0 and 9.")
        self._value = value
        self._possible_values = {value}

    @property
    def possible_values(self) -> set[int]:
        """Possible values for the cell, as thought by the user."""
        return self._possible_values if self._editable else set()

    @possible_values.setter
    def possible_values(self, values: set[int]) -> None:
        """Set the possible values for the cell.

        Parameters
        ----------
        values : set[int]
            The possible values for the cell.

        Raises
        ------
        ValueError
            If the cell is not editable.
        """
        if not self._editable:
            raise ValueError("Cannot set possible values of non-editable cell.")
        self._possible_values = values.intersection(set(range(1, 10)))

    @property
    def editable(self) -> bool:
        """Whether the cell is editable."""
        return self._editable

    @property
    def selected(self) -> bool:
        """Whether the cell is selected."""
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        """Set the selected state of the cell.

        Parameters
        ----------
        value : bool
            Whether the cell is selected.
        """
        if not isinstance(value, bool):
            raise TypeError("Selected must be a bool.")
        self._selected = value

    def clear(self) -> None:
        """Clear the cell.

        Raises
        ------
        ValueError
            If the cell is not editable.
        """
        if not self.editable:
            raise ValueError("Cannot clear non-editable cell.")
        self.value = 0
        self.possible_values = set(range(1, 10))
