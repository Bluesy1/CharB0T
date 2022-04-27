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
"""Sudoko minigame."""
import datetime
import random
from random import sample
from itertools import islice
from copy import deepcopy
from typing import Callable, Literal, Optional, Any, Generator

import discord
from discord import ui
from discord.ext import commands
from discord.utils import utcnow

from main import CBot


# noinspection GrazieInspection
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

    See Also
    --------
    Row
        Row of cells.
    Column
        Column of cells.
    Box
        Box of cells.
    Puzzle
        The sudoku board.
    """

    def __init__(self, value: int, editable: bool):
        if 9 < value < 0:
            raise ValueError("Value must be between 0 and 9.")
        self._value = value
        self._editable = editable
        self._possible_values: set[int] = set(range(1, 10)) if editable else {value}

    def __repr__(self):
        """Return a string representation of the cell."""
        return f"<Cell value={self.value} possible_values={self.possible_values}>"

    def __eq__(self, other):
        """Two cells are equal if they have the same value and editability."""
        return self.value == other.value and self.editable == other.editable

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
        if 9 < value < 0:
            raise ValueError("Value must be between 0 and 9.")
        self._value = value
        self._possible_values = {value}

    @property
    def possible_values(self) -> set[int]:
        """Possible values for the cell, as thought by the user."""
        if not self._editable:
            return set()
        return self._possible_values

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
        return self.cells == other.cells

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
        return self.cells == other.cells

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
        self._row1 = cells[0:3]
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
        return self.cells == other.cells

    @property
    def cells(self) -> list[Cell]:
        """Cells in the block."""
        return self._row1 + self._row2 + self._row3

    @property
    def solved(self) -> bool:
        """Whether the block is solved."""
        return all(cell.value != 0 for cell in self.cells) and len({cell.value for cell in self.cells}) == 9

    def clear(self) -> None:
        """Reset the block."""
        for cell in self.cells:
            if cell.editable:
                cell.clear()


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

    def __init__(self, puzzle: list[list[int]]):
        self._rows = [Row([Cell(cell, editable=(cell == 0)) for cell in cells]) for cells in puzzle]
        self._columns = [Column([row.cells[i] for row in self.rows]) for i in range(9)]
        self._blocks = [
            Block([self.rows[(i * 3) + k].cells[(j * 3) + p] for k in range(3) for p in range(3)])
            for i in range(3)
            for j in range(3)
        ]
        self._initial_puzzle = puzzle

    def __str__(self):
        """Return the puzzle as a string."""
        base = 3
        side = base * base
        expand_line: Callable[[str], str] = lambda x: x[0] + x[5:9].join([x[1:5] * (base - 1)] * base) + x[9:13]

        line0 = expand_line("╔═══╤═══╦═══╗")
        line1 = expand_line("║ . │ . ║ . ║")
        line2 = expand_line("╟───┼───╫───╢")
        line3 = expand_line("╠═══╪═══╬═══╣")
        line4 = expand_line("╚═══╧═══╩═══╝")

        symbol = " 1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        symbols = [[""] + [symbol[n.value] for n in row] for row in self.rows]
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
        return Puzzle(solution)

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
            row = []
            for column in columns:
                row.append(column.cells[i].value)
            rows.append(row)
        return cls(rows)

    @classmethod
    def new(cls):
        """Create a new puzzle randomly.

        Returns
        -------
        Puzzle
            A new puzzle.
        """
        base = 3
        side = base * base

        # pattern for a baseline valid solution
        pattern = lambda r, c: (base * (r % base) + r // base + c) % side  # noqa: E731

        # randomize rows, columns and numbers (of valid base pattern)
        shuffle = lambda s: sample(s, len(s))  # noqa: E731

        r_base = range(base)
        rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, base * base + 1))

        # produce board using randomized baseline pattern
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]

        solution = deepcopy(board)

        squares = side * side
        empties = squares * 3 // 4
        for p in sample(range(squares), empties):
            board[p // side][p % side] = 0

        while True:
            solved = [*islice(cls.shortSudokuSolve(board), 2)]
            if len(solved) == 1:
                break
            diff_pos = [(r, c) for r in range(9) for c in range(9) if solved[0][r][c] != solved[1][r][c]]
            r, c = random.choice(diff_pos)
            board[r][c] = solution[r][c]
        return cls(board)

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
                * [k // size, size + k % size, 2 * size + k % size // block + k // size // block * block]
            }
            for k in range(size * size)
            for n in range(size + 1)
        }
        _empties = [i for i, n in enumerate(board) if n == 0]
        used = set().union(*(span[n, _p] for _p, n in enumerate(board) if n))  # type: ignore
        empty = 0
        while 0 <= empty < len(_empties):
            pos = _empties[empty]
            used -= span[board[pos], pos]  # type: ignore
            board[pos] = next(  # type: ignore
                (n for n in range(board[pos] + 1, size + 1) if not span[n, pos] & used), 0  # type: ignore
            )
            used |= span[board[pos], pos]  # type: ignore
            empty += 1 if board[pos] else -1
            if empty == len(_empties):
                # fmt: off
                _solution = [board[r:r + size] for r in range(0, size * size, size)]
                # fmt: on
                yield _solution
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
        row_index = -1
        for i, row in enumerate(self.rows):
            if cell in row:
                row_index = i
                break
        column_index = -1
        for i, column in enumerate(self.columns):
            if cell in column:
                column_index = i
                break
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
            if cell in row:
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
            if cell in column:
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


# noinspection GrazieInspection
class SudokuGame(ui.View):
    """View for playing Sudoku.

    Parameters
    ----------
    puzzle : Puzzle
        Puzzle to be played.
    author: discord.Member
        Member who created the puzzle.
    bot: CBot
        The bot instance.

    Attributes
    ----------
    puzzle : Puzzle
        Puzzle being played.
    author: discord.Member
        Member playing the puzzle.
    bot: CBot
        The bot instance.
    level: Literal["Puzzle", "Block", "Cell"]
        Level of focus on the puzzle
    block: Optional[Block]
        Block being focused on.
    cell: Optional[Cell]
        Cell being focused on.
    noting_mode: bool
        Whether or not the user is in noting mode.
    start_time: datetime.datetime
        Time the game started, used for calculating time taken. Timezone aware.
    message: discord.Message, optional
        Message that the game was started in.
    """

    def __init__(self, puzzle: Puzzle, author: discord.Member, bot: CBot):
        super().__init__(timeout=600)
        self.puzzle = puzzle
        self.author = author
        self.bot = bot
        self.level: Literal["Puzzle", "Block", "Cell"] = "Puzzle"
        self.block: Optional[Block] = None
        self.cell: Optional[Cell] = None
        self.noting_mode = False
        self.start_time = utcnow()
        self.moves = 0
        self.message: Optional[discord.Message] = None

    def enable_keypad(self):
        """Enable all keypad buttons."""
        self.one.disabled = False
        self.two.disabled = False
        self.three.disabled = False
        self.four.disabled = False
        self.five.disabled = False
        self.six.disabled = False
        self.seven.disabled = False
        self.eight.disabled = False
        self.nine.disabled = False
        self.clear.disabled = False

    def disable_keypad(self):
        """Disable all keypad buttons."""
        self.one.disabled = True
        self.two.disabled = True
        self.three.disabled = True
        self.four.disabled = True
        self.five.disabled = True
        self.six.disabled = True
        self.seven.disabled = True
        self.eight.disabled = True
        self.nine.disabled = True
        self.clear.disabled = True

    def update_keypad(self):
        """Update the keypad dynamically to reflect the current focus."""
        if self.level == "Puzzle":
            self.enable_keypad()
            self.back.disabled = True
            self.enable_keypad()
        elif self.level == "Block":
            self.disable_keypad()
            self.one.disabled = not self.block[0].editable  # type: ignore
            self.two.disabled = not self.block[1].editable  # type: ignore
            self.three.disabled = not self.block[2].editable  # type: ignore
            self.four.disabled = not self.block[3].editable  # type: ignore
            self.five.disabled = not self.block[4].editable  # type: ignore
            self.six.disabled = not self.block[5].editable  # type: ignore
            self.seven.disabled = not self.block[6].editable  # type: ignore
            self.eight.disabled = not self.block[7].editable  # type: ignore
            self.nine.disabled = not self.block[8].editable  # type: ignore
            self.clear.disabled = False
            self.back.disabled = False
        elif self.level == "Cell":
            self.back.disabled = False
            if self.cell.editable:  # type: ignore
                self.enable_keypad()
            else:
                self.disable_keypad()

    def change_cell_prompt_embed(self) -> discord.Embed:
        """Embed for when the user is changing a cell.

        Returns
        -------
        discord.Embed
            Embed to send for when the user is changing a cell.
        """
        embed = discord.Embed(title="Sudoku", description=f"```{self.puzzle}```", color=discord.Color.blurple())
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text="Play Sudoku by Typing !sudoku")
        embed.add_field(
            name=f"Choose a value for the cell at {self.puzzle.location_of_cell(self.cell)}",  # type: ignore
            value="Use the keypad to choose a value",
            inline=True,
        )
        embed.add_field(name="Disabled Buttons", value="Disabled buttons reference static cells", inline=True)
        return embed

    def cell_choose_embed(self) -> discord.Embed:
        """Embed for when the user is choosing a cell.

        Returns
        -------
        discord.Embed
            Embed to send for when the user is choosing a cell.
        """
        embed = discord.Embed(title="Sudoku", description=f"```{self.puzzle}```", color=discord.Color.blurple())
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text="Play Sudoku by Typing !sudoku")
        embed.add_field(
            name=f"Choose a cell from block {self.puzzle.block_index(self.block) + 1}",  # type: ignore
            value="Use the keypad to choose a cell",
            inline=True,
        )
        embed.add_field(name="Disabled Buttons", value="Disabled buttons reference static cells", inline=True)
        return embed

    def block_choose_embed(self) -> discord.Embed:
        """Embed for choosing a block.

        Returns
        -------
        discord.Embed
            The embed to send for choosing a block.
        """
        embed = discord.Embed(title="Sudoku", description=f"```{self.puzzle}```", color=discord.Color.blurple())
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text="Play Sudoku by Typing !sudoku")
        embed.add_field(name="Choose a block", value="Use the keypad to choose a block", inline=True)
        return embed

    async def keypad_callback(self, interaction: discord.Interaction, button: ui.Button, key: int):
        """Keypad buttons callback.

        It will change the cell, block, or puzzle depending on the level of focus.

        Parameters
        ----------
        interaction: discord.Interaction
            Interaction object.
        button: ui.Button
            Button that was pressed.
        key: int
            index key for the item to change.

        Raises
        ------
        NotImplementedError
            If a cell level change is triggered and the puzzle is in noting mode.
        """
        if self.message is None and interaction.message is not None:
            self.message = interaction.message
        if self.level == "Puzzle":
            self.block = self.puzzle.blocks[key]
            self.level = "Block"
            self.update_keypad()
            await interaction.response.edit_message(embed=self.cell_choose_embed(), view=self)
        elif self.level == "Block":
            if self.block is not None:
                self.cell = self.block[key]
                self.level = "Cell"
                self.update_keypad()
                await interaction.response.edit_message(embed=self.change_cell_prompt_embed(), view=self)
        elif self.level == "Cell":  # skipcq: PTC-W0048
            if self.cell is not None:  # skipcq: PTC-W0048
                if self.cell.editable and not self.noting_mode:
                    self.moves += 1
                    self.cell.value = int(button.label)  # type: ignore
                    self.level = "Block"
                    self.cell.possible_values.clear()
                    self.cell = None
                    if self.puzzle.is_solved:
                        self.disable_keypad()
                        self.back.disabled = True
                        self.cancel.disabled = True
                        self.mode.disabled = True
                        embed = discord.Embed(
                            title="**Solved!!** Sudoku",
                            description=f"```{self.puzzle}```",
                            color=discord.Color.green(),
                        )
                        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
                        embed.set_footer(text="Play Sudoku by Typing !sudoku")
                        embed.add_field(name="Time Taken", value=f"{(utcnow() - self.start_time)}", inline=True)
                        embed.add_field(
                            name="Points gained",
                            value=f"{await self.bot.give_game_points(self.author.id, 2, 3)} Points",
                            inline=True,
                        )
                        await interaction.response.edit_message(embed=embed, view=self)
                    else:
                        self.update_keypad()
                        await interaction.response.edit_message(embed=self.cell_choose_embed(), view=self)
                elif self.cell.editable and self.noting_mode:
                    if int(button.label) not in self.cell.possible_values:  # type: ignore
                        self.cell.possible_values.add(int(button.label))  # type: ignore
                    else:
                        self.cell.possible_values.remove(int(button.label))  # type: ignore
                    raise NotImplementedError("Noting mode not implemented")
                else:
                    self.cell = None
                    self.level = "Block"
                    self.update_keypad()
                    await interaction.response.edit_message(embed=self.cell_choose_embed(), view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Make sure the interaction user is the same as the initial invoker.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction to check.

        Returns
        -------
        bool
            Whether or not the interaction user is the same as the initial invoker.
        """
        return interaction.user.id == self.author.id

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: ui.Item[Any]) -> None:
        """Call when an item's callback or :meth:`interaction_check` fails with an error.

        Parameters
        ----------
        interaction: :class:`~discord.Interaction`
            The interaction that led to the failure.
        error: :class:`Exception`
            The exception that was raised.
        item: :class:`~discord.ui.Item`
            The item that failed the dispatch.
        """
        if isinstance(error, discord.app_commands.CheckFailure):
            await interaction.response.send_message("Only the invoker can play this instance of Sudoku", ephemeral=True)
        else:
            await super().on_error(interaction, error, item)

    async def on_timeout(self) -> None:
        """Call when the interaction times out."""
        solution = self.puzzle.solution
        embed = discord.Embed(
            title="**Timed Out** Sudoku", description=f"The solution was\n```{solution}```", color=discord.Color.red()
        )
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text="Play Sudoku by Typing !sudoku")
        embed.add_field(name="Time Taken", value=f"{(utcnow() - self.start_time)}", inline=True)
        embed.add_field(name="Points gained", value="0 Points", inline=True)
        self.disable_keypad()
        self.mode.disabled = True
        self.cancel.disabled = True
        self.back.disabled = True
        self.stop()
        await self.message.edit(embed=embed, view=self)  # type: ignore

    @ui.button(label="Back", disabled=True, style=discord.ButtonStyle.green, row=0)
    async def back(self, interaction: discord.Interaction, button: ui.Button):
        """Back to the previous level of the puzzle.

        This acts dynamically based on the current focus level of the puzzle.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        if self.message is None and interaction.message is not None:
            self.message = interaction.message
        if self.level == "Puzzle":
            button.disabled = True
            self.enable_keypad()
            await interaction.response.edit_message(view=self)
        elif self.level == "Block":
            self.level = "Puzzle"
            button.disabled = True
            self.enable_keypad()
            await interaction.response.edit_message(embed=self.block_choose_embed(), view=self)
        elif self.level == "Cell":
            self.level = "Block"
            self.cell = None
            self.enable_keypad()
            await interaction.response.edit_message(embed=self.cell_choose_embed(), view=self)

    @ui.button(label="1", style=discord.ButtonStyle.blurple, row=0)
    async def one(self, interaction: discord.Interaction, button: ui.Button):
        """Keypad callback for the 1 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 0)

    @ui.button(label="2", style=discord.ButtonStyle.blurple, row=0)
    async def two(self, interaction: discord.Interaction, button: ui.Button):
        """Keypad callback for the 2 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 1)

    @ui.button(label="3", style=discord.ButtonStyle.blurple, row=0)
    async def three(self, interaction: discord.Interaction, button: ui.Button):
        """Keypad callback for the 3 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 2)

    # noinspection PyUnusedLocal
    @ui.button(label="Stop", style=discord.ButtonStyle.red, row=1)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):  # skipcq: PYL-W0613
        """Cancel/Stop button callback.

        This button displays a solution and turns off the view.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        if self.message is None and interaction.message is not None:
            self.message = interaction.message
        solution = self.puzzle.solution
        embed = discord.Embed(
            title="**FAILED** Sudoku", description=f"The solution was\n```{solution}```", color=discord.Color.red()
        )
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text="Play Sudoku by Typing !sudoku")
        embed.add_field(name="Time Taken", value=f"{(utcnow() - self.start_time)}", inline=True)
        if (utcnow() - self.start_time) > datetime.timedelta(minutes=3) and self.moves > 10:
            embed.add_field(
                name="Points gained",
                value=f"{await self.bot.give_game_points(self.author.id, 2, 0)} Points",
                inline=True,
            )
        else:
            embed.add_field(name="Points gained", value="0 Points", inline=True)
        self.disable_keypad()
        self.mode.disabled = True
        self.cancel.disabled = True
        self.back.disabled = True
        self.stop()
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="4", style=discord.ButtonStyle.blurple, row=1)
    async def four(self, interaction: discord.Interaction, button: ui.Button):
        """Keypad callback for the 4 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 3)

    @ui.button(label="5", style=discord.ButtonStyle.blurple, row=1)
    async def five(self, interaction: discord.Interaction, button: ui.Button):
        """Keypad callback for the 5 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 4)

    @ui.button(label="6", style=discord.ButtonStyle.blurple, row=1)
    async def six(self, interaction: discord.Interaction, button: ui.Button):
        """Keypad callback for the 6 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 5)

    # noinspection PyUnusedLocal
    @ui.button(label="Clear", style=discord.ButtonStyle.red, row=2)
    async def clear(self, interaction: discord.Interaction, button: ui.Button):  # skipcq: PYL-W0613
        """Clear button callback.

        Clears the current cell, block or resets the puzzle depending on the current state.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        if self.message is None and interaction.message is not None:
            self.message = interaction.message
        self.moves += 1
        if self.level == "Puzzle":
            self.puzzle.reset()
            await interaction.response.edit_message(embed=self.block_choose_embed(), view=self)
        elif self.level == "Block":
            if self.block is not None:
                self.block.clear()
            await interaction.response.edit_message(embed=self.cell_choose_embed(), view=self)
        elif self.level == "Cell":
            if self.cell is not None and self.cell.editable:
                self.cell.clear()
            await interaction.response.edit_message(embed=self.change_cell_prompt_embed(), view=self)

    @ui.button(label="7", style=discord.ButtonStyle.blurple, row=2)
    async def seven(self, interaction: discord.Interaction, button: ui.Button):
        """Keypad callback for the 7 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 6)

    @ui.button(label="8", style=discord.ButtonStyle.blurple, row=2)
    async def eight(self, interaction: discord.Interaction, button: ui.Button):
        """Keypad callback for the 8 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 7)

    @ui.button(label="9", style=discord.ButtonStyle.blurple, row=2)
    async def nine(self, interaction: discord.Interaction, button: ui.Button):
        """Keypad callback for the 9 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 8)

    @ui.select(
        placeholder="Mode",
        row=3,
        disabled=True,
        options=[
            discord.SelectOption(label="Solve Mode", value="Solve", description="Mode to solve the puzzle in"),
            discord.SelectOption(
                label="Note Mode", value="Note", description="Mode to note individual cells of the puzzle in"
            ),
        ],
    )
    async def mode(self, interaction: discord.Interaction, select: ui.Select):
        """Switch between solve and note mode.

        When in solve mode, the user can solve the puzzle by entering numbers into the cells.
        When in note mode, the user can note individual cells of the puzzle by entering numbers into the cells.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        select : ui.Select
            The select object.

        Raises
        ------
        NotImplementedError
            This function is not implemented yet

        Notes
        -----
        This function is not implemented yet.
        """
        raise NotImplementedError("Only solve mode is implemented currently")


class Sudoku(commands.Cog):
    """Sudoku commands.

    This cog contains commands for playing Sudoku.

    Parameters
    ----------
    bot : CBot
        The bot instance.
    """

    def __init__(self, bot: CBot):
        self.bot = bot

    @commands.command(name="sudoku", aliases=["sud"])
    async def sudoku(self, ctx: commands.Context):
        """Generate a sudoku puzzle.

        Parameters
        ----------
        ctx : commands.Context
            The context of the command.
        """
        if ctx.guild is None:
            return
        if ctx.channel.id not in (839690221083820032, 687817008355737606, 926532222398369812):
            return
        if not any(role.id in (338173415527677954, 928481483742670971) for role in ctx.author.roles):  # type: ignore
            return
        if ctx.channel.id == 687817008355737606 and ctx.author.id != 363095569515806722:
            return
        puzzle = await self.bot.loop.run_in_executor(self.bot.process_pool, Puzzle.new)
        view = SudokuGame(puzzle, ctx.author, self.bot)  # type: ignore
        view.message = await ctx.send(embed=view.block_choose_embed(), view=view)


async def setup(bot: CBot):
    """Load the cog.

    Parameters
    ----------
    bot : CBot
    """
    await bot.add_cog(Sudoku(bot))
