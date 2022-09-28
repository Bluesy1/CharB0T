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
"""Puzzle Class."""
from typing import Any, Callable, Generator

from . import Block, Cell, Column, Row


# noinspection PyUnresolvedReferences
class Puzzle:
    """Represents a sudoku board.

    Parameters
    ----------
    puzzle : list[list[int]]
        The sudoku board represented as a list of lists of ints.

    Attributes
    ----------
    rows : list[Row]
    columns : list[Column]
    blocks : list[Block]
    is_solved : bool
    solution : Puzzle

    Methods
    -------
    from_rows(rows: list[Row])
        Creates a puzzle from a list of rows. .. note:: This is a class method.
    from_columns(columns: list[Column])
        Creates a puzzle from a list of columns. .. note:: This is a class method.
    new()
        Creates a new puzzle randomly. .. note:: This is a class method.
    shortSudokuSolve(board: list[list[int]])
        Generator for solutions to a sudoku puzzle. .. note:: This is a static method.
    location_of_cell(cell: Cell)
        Returns the location of a cell in the puzzle.
    row_of_cell(cell: Cell)
        Returns the row of a cell in the puzzle.
    column_of_cell(cell: Cell)
        Returns the column of a cell in the puzzle.
    block_of_cell(cell: Cell)
        Returns the block of a cell in the puzzle.
    block_index(block: Block)
        Returns the index of a block in the puzzle.
    as_list()
        Returns the puzzle as a list of lists of ints.
    reset()
        Resets the puzzle.
    """

    def __init__(self, puzzle: list[list[int]], mobile: bool = False):
        self._rows = [Row([Cell(cell, editable=(cell == 0)) for cell in cells]) for cells in puzzle]
        self._columns = [Column([row.cells[i] for row in self.rows]) for i in range(9)]
        self._blocks = [
            Block([self.rows[(i * 3) + k].cells[(j * 3) + p] for k in range(3) for p in range(3)])
            for i in range(3)
            for j in range(3)
        ]
        self._mobile = mobile
        self._initial_puzzle = puzzle

    def __str__(self):
        """Return the puzzle as a string."""
        base = 3
        side = base**2
        expand_line: Callable[[str], str] = lambda x: x[0] + x[5:9].join([x[1:5] * (base - 1)] * base) + x[9:13]

        line0 = expand_line("╔═══╤═══╦═══╗")
        line1 = expand_line("║ . │ . ║ . ║")
        line2 = expand_line("╟───┼───╫───╢")
        line3 = expand_line("╠═══╪═══╬═══╣")
        line4 = expand_line("╚═══╧═══╩═══╝")

        symbol = " 1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        static = "" if self._mobile else "\u001b[1;37m"
        selected = "" if self._mobile else "\u001b[4;40m"
        clear = "" if self._mobile else "\u001b[0m"
        symbols = [
            [""]
            + [
                f"{'' if n.editable else static}{selected if n.selected else ''}"
                f"{symbol[n.value]}{clear if not n.editable or n.selected else ''}"
                for n in row
            ]
            for row in self.rows
        ]
        string = line0
        for r in range(1, side + 1):
            string += "\n" + "".join(n + s for n, s in zip(symbols[r - 1], line1.split(".")))
            string += "\n" + [line2, line3, line4][(r % side == 0) + (r % base == 0)]
        return string

    def __repr__(self):
        """Return a string representation of the puzzle."""
        return f"<Puzzle rows={self.rows} columns={self.columns} blocks={self.blocks}>"

    def __eq__(self, other):
        """Two puzzles are equal if they have the same rows, columns, and blocks."""
        return self.rows == other.rows and self.columns == other.columns and self.blocks == other.blocks

    @property
    def rows(self) -> list[Row]:
        """Rows of the puzzle."""
        return self._rows

    @property
    def columns(self) -> list[Column]:
        """Columns of the puzzle."""
        return self._columns

    @property
    def blocks(self) -> list[Block]:
        """Blocks of the puzzle."""
        return self._blocks

    @property
    def is_solved(self) -> bool:
        """Whether the puzzle is solved."""
        return (
            all(row.solved for row in self.rows)
            and all(column.solved for column in self.columns)
            and all(block.solved for block in self.blocks)
        )

    @property
    def solution(self):
        """Solution to the puzzle."""
        solutions = self.shortSudokuSolve(self.as_list())
        solution = next(solutions, None)
        if solution is None:
            _solutions = self.shortSudokuSolve(self._initial_puzzle)
            solution = next(_solutions, None)
        if solution is None:
            raise AttributeError("No solution found.")
        return Puzzle(solution, self._mobile)

    @classmethod
    def from_rows(cls, rows: list[Row]):
        """Create a puzzle from a list of rows.

        Parameters
        ----------
        rows: list[Row]
            The rows of the puzzle.

        Returns
        -------
        Puzzle
            The puzzle created from the rows.
        """
        return cls([[cell.value for cell in row] for row in rows])

    @classmethod
    def from_columns(cls, columns: list[Column]):
        """Create a puzzle from a list of columns.

        Parameters
        ----------
        columns: list[Column]
            The columns of the puzzle.

        Returns
        -------
        Puzzle
            The puzzle created from the columns.
        """
        rows = []
        for i in range(9):
            row = [column.cells[i].value for column in columns]
            rows.append(row)
        return cls(rows)

    @staticmethod
    def shortSudokuSolve(_board: list[list[int]]) -> Generator[list[list[int]], Any, None]:
        """Solutions to a sudoku puzzle.

        Parameters
        ----------
        _board: list[list[int]]
            The board to solve as a list of lists of ints.

        Yields
        ------
        list[list[int]]
            A solution to the puzzle as a list of lists of ints.

        """
        size = len(_board)
        block = int(size**0.5)
        board = [n for row in _board for n in row]
        span = {
            (n, k): {
                (g, n)
                for g in (n > 0)
                * [
                    k // size,
                    size + k % size,
                    2 * size + k % size // block + k // size // block * block,
                ]
            }
            for k in range(size**2)
            for n in range(size + 1)
        }

        _empties = [i for i, n in enumerate(board) if n == 0]
        used = set().union(*(span[n, _p] for _p, n in enumerate(board) if n))
        empty = 0
        while 0 <= empty < len(_empties):
            pos = _empties[empty]
            used -= span[board[pos], pos]
            board[pos] = next((n for n in range(board[pos] + 1, size + 1) if not span[n, pos] & used), 0)
            used |= span[board[pos], pos]
            empty += 1 if board[pos] else -1
            if empty == len(_empties):
                yield [board[r:r + size] for r in range(0, size**2, size)]
                empty -= 1

    def location_of_cell(self, cell: Cell) -> str:
        """Return the location of a cell in the puzzle.

        Parameters
        ----------
        cell: Cell
            The cell to find the location of.

        Returns
        -------
        str
            The location of the cell.

        Raises
        ------
        ValueError
            If the cell is not in the puzzle.
        TypeError
            If the cell is not a Cell.
        """
        if not isinstance(cell, Cell):
            raise TypeError("cell must be of type Cell")
        row_index = next(
            (
                i
                for i, row in enumerate(self.rows)
                if cell.id in [cell.id for cell in row.cells]
            ),
            -1,
        )

        column_index = next(
            (
                j
                for j, column in enumerate(self.columns)
                if cell.id in [cell.id for cell in column.cells]
            ),
            -1,
        )

        if -1 in (row_index, column_index):
            raise ValueError("Cell not found in puzzle")
        return f"row {row_index + 1}, column {column_index + 1}"

    def row_of_cell(self, cell: Cell) -> Row:
        """Return the row that contains the cell.

        Parameters
        ----------
        cell: Cell
            The cell to find the row of.

        Returns
        -------
        Row
            The row that contains the cell.

        Raises
        ------
        TypeError
            If cell is not of type Cell.
        ValueError
            If cell is not found in the puzzle.
        """
        if not isinstance(cell, Cell):
            raise TypeError("cell must be of type Cell")
        for row in self.rows:
            if cell.id in [cell.id for cell in row.cells]:
                return row
        raise ValueError("Cell not found in puzzle")

    def column_of_cell(self, cell: Cell) -> Column:
        """Return the column that contains the cell.

        Parameters
        ----------
        cell: Cell
            The cell to find the column of.

        Returns
        -------
        Column
            The column that contains the cell.

        Raises
        ------
        TypeError
            If cell is not of type Cell.
        ValueError
            If cell is not found in the puzzle.
        """
        if not isinstance(cell, Cell):
            raise TypeError("cell must be of type Cell")
        for column in self.columns:
            if cell.id in [cell.id for cell in column.cells]:
                return column
        raise ValueError("Cell not found in puzzle")

    def block_of_cell(self, cell: Cell) -> Block:
        """Return the block that contains the cell.

        Parameters
        ----------
        cell: Cell
            The cell to find the block of.

        Returns
        -------
        Block
            The block that contains the cell.

        Raises
        ------
        TypeError
            If cell is not of type Cell.
        ValueError
            If cell is not found in the puzzle.
        """
        if not isinstance(cell, Cell):
            raise TypeError("cell must be of type Cell")
        for block in self.blocks:
            if cell in block:
                return block
        raise ValueError("Cell not found in puzzle")

    def block_index(self, block: Block) -> int:
        """Return the index of the block if it is in the puzzle.

        Parameters
        ----------
        block: Block
            The block to find.

        Returns
        -------
        int
            The index of the block.

        Raises
        ------
        ValueError
            If the block is not in the puzzle.
        TypeError
            If the block is not of type Block.
        """
        if not isinstance(block, Block):
            raise TypeError("block must be a Block")
        for i, b in enumerate(self.blocks):
            if block is b:
                return i
        raise ValueError("Block not found in puzzle")

    def as_list(self) -> list[list[int]]:
        """Serialize puzzle as list of lists.

        Returns
        -------
        list[list[int]]
            The puzzle as a list of lists of integers.
        """
        return [[cell.value for cell in row] for row in self.rows]

    def reset(self) -> None:
        """Reset the puzzle to the initial state."""
        self._rows = [Row([Cell(cell, editable=(cell == 0)) for cell in cells]) for cells in self._initial_puzzle]
        self._columns = [Column([row.cells[i] for row in self.rows]) for i in range(9)]
        self._blocks = [
            Block([self.rows[(i * 3) + k].cells[(j * 3) + p] for k in range(3) for p in range(3)])
            for i in range(3)
            for j in range(3)
        ]
