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
import concurrent.futures
import random
from random import sample
from itertools import islice
from copy import deepcopy
from typing import Callable, Literal, Optional, Any

import discord
from discord import ui
from discord.ext import commands

from main import CBot


class Cell:
    def __init__(self, value: int, editable: bool):
        if 9 < value < 0:
            raise ValueError("Value must be between 0 and 9.")
        self._value = value
        self._editable = editable
        self._possible_values: set[int] = set(range(1, 10)) if editable else {value}

    def __str__(self):
        return f"""╔═══╗
        ║ {self.value} ║
        ╚═══╝
        """

    def __repr__(self):
        return f"<Cell value={self.value} possible_values={self.possible_values}>"

    def __eq__(self, other):
        return self.value == other.value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not self._editable:
            raise ValueError("Cannot set value of non-editable cell.")
        if 9 < value < 0:
            raise ValueError("Value must be between 0 and 9.")
        self._value = value
        self._possible_values = {value}

    @property
    def possible_values(self):
        return self._possible_values

    @possible_values.setter
    def possible_values(self, values: set[int]):
        if not self._editable:
            raise ValueError("Cannot set possible values of non-editable cell.")
        self._possible_values = values.intersection(set(range(1, 10)))

    @property
    def editable(self):
        return self._editable

    def clear(self):
        if not self.editable:
            raise ValueError("Cannot clear non-editable cell.")
        self.value = 0
        self.possible_values = set(range(1, 10))


class Row:
    def __init__(self, cells: list[Cell]):
        if len(cells) != 9:
            raise ValueError("Row must have exactly 9 cells.")
        self._cells = cells

    @property
    def cells(self):
        return self._cells

    def __repr__(self):
        return f"<Row cells={self.cells}>"

    def __eq__(self, other):
        return self.cells == other.cells

    def __getitem__(self, item):
        return self.cells[item]

    @property
    def solved(self):
        return all(cell.value != 0 for cell in self.cells) and len(set(cell.value for cell in self.cells)) == 9


class Column:
    def __init__(self, cells: list[Cell]):
        if len(cells) != 9:
            raise ValueError("Column must have exactly 9 cells.")
        self._cells = cells

    @property
    def cells(self):
        return self._cells

    def __repr__(self):
        return f"<Column cells={self.cells}>"

    def __getitem__(self, item):
        return self.cells[item]

    def __eq__(self, other):
        return self.cells == other.cells

    @property
    def solved(self):
        return all(cell.value != 0 for cell in self.cells) and len(set(cell.value for cell in self.cells)) == 9


class Block:
    def __init__(self, cells: list[Cell]):
        if len(cells) != 9:
            raise ValueError("Block must have exactly 9 cells.")
        self._row1 = cells[0:3]
        self._row2 = cells[3:6]
        self._row3 = cells[6:9]

    @property
    def cells(self):
        return self._row1 + self._row2 + self._row3

    def __getitem__(self, item):
        return self.cells[item]

    def __repr__(self):
        return f"<Block cells={self.cells}>"

    def __eq__(self, other):
        return self.cells == other.cells

    @property
    def solved(self):
        return all(cell.value != 0 for cell in self.cells) and len(set(cell.value for cell in self.cells)) == 9

    def clear(self):
        for cell in self.cells:
            if cell.editable:
                cell.value = 0
                cell.possible_values = set(range(1, 10))


class Puzzle:
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
        return f"<Puzzle rows={self.rows} columns={self.columns} blocks={self.blocks}>"

    def __eq__(self, other):
        return self.rows == other.rows and self.columns == other.columns and self.blocks == other.blocks

    @property
    def rows(self):
        return self._rows

    @property
    def columns(self):
        return self._columns

    @property
    def blocks(self):
        return self._blocks

    @property
    def is_solved(self):
        return (
            all(row.solved for row in self.rows)
            and all(column.solved for column in self.columns)
            and all(block.solved for block in self.blocks)
        )

    @property
    def solution(self):
        solutions = self.shortSudokuSolve(self.as_list())
        solution = next(solutions, None)
        if solution is None:
            _solutions = self.shortSudokuSolve(self._initial_puzzle)
            solution = next(_solutions, None)
            if solution is None:
                raise AttributeError("No solution found.")
        return self.__class__(solution)

    @classmethod
    def from_rows(cls, rows: list[Row]):
        return cls([[cell.value for cell in row] for row in rows])

    @classmethod
    def from_columns(cls, columns: list[Column]):
        rows = []
        for i in range(9):
            row = []
            for column in columns:
                row.append(column.cells[i].value)
            rows.append(row)
        return cls(rows)

    @classmethod
    def new(cls):
        base = 3
        side = base * base

        # pattern for a baseline valid solution
        def pattern(r, c):
            return (base * (r % base) + r // base + c) % side

        # randomize rows, columns and numbers (of valid base pattern)
        def shuffle(s):
            return sample(s, len(s))

        r_base = range(base)
        rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, base * base + 1))

        # produce board using randomized baseline pattern
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]

        solution = deepcopy(board)

        """for line in board:
            print(line)"""

        squares = side * side
        empties = squares * 3 // 4
        for p in sample(range(squares), empties):
            board[p // side][p % side] = 0

        num_size = len(str(side))
        """for line in board:
            print("[" + "  ".join(f"{n or '.':{num_size}}" for n in line) + "]")"""

        while True:
            solved = [*islice(cls.shortSudokuSolve(board), 2)]
            if len(solved) == 1:
                break
            diff_pos = [(r, c) for r in range(9) for c in range(9) if solved[0][r][c] != solved[1][r][c]]
            r, c = random.choice(diff_pos)
            board[r][c] = solution[r][c]
        return cls(board)

    @staticmethod
    def shortSudokuSolve(_board):
        size = len(_board)
        block = int(size**0.5)
        _board = [n for row in _board for n in row]
        span = {
            (n, k): {
                (g, n)
                for g in (n > 0)
                * [k // size, size + k % size, 2 * size + k % size // block + k // size // block * block]
            }
            for k in range(size * size)
            for n in range(size + 1)
        }
        _empties = [i for i, n in enumerate(_board) if n == 0]
        used = set().union(*(span[n, _p] for _p, n in enumerate(_board) if n))
        empty = 0
        while 0 <= empty < len(_empties):
            pos = _empties[empty]
            used -= span[_board[pos], pos]
            _board[pos] = next((n for n in range(_board[pos] + 1, size + 1) if not span[n, pos] & used), 0)
            used |= span[_board[pos], pos]
            empty += 1 if _board[pos] else -1
            if empty == len(_empties):
                _solution = [_board[r : r + size] for r in range(0, size * size, size)]
                yield _solution
                empty -= 1

    def location_of_cell(self, cell: Cell):
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
        if row_index == -1 or column_index == -1:
            raise ValueError("Cell not found in puzzle")
        return f"row {row_index + 1}, column {column_index + 1}"

    def row_of_cell(self, cell: Cell):
        for row in self.rows:
            if cell in row:
                return row
        raise ValueError("Cell not found in puzzle")

    def column_of_cell(self, cell: Cell):
        for column in self.columns:
            if cell in column:
                return column
        raise ValueError("Cell not found in puzzle")

    def block_of_cell(self, cell: Cell):
        for block in self.blocks:
            if cell in block:
                return block
        raise ValueError("Cell not found in puzzle")

    def block_index(self, block: Block):
        for i, b in enumerate(self.blocks):
            if block is b:
                return i
        raise ValueError("Block not found in puzzle")

    def as_list(self):
        return [[cell.value for cell in row] for row in self.rows]

    def reset(self):
        self._rows = [Row([Cell(cell, editable=(cell == 0)) for cell in cells]) for cells in self._initial_puzzle]
        self._columns = [Column([row.cells[i] for row in self.rows]) for i in range(9)]
        self._blocks = [
            Block([self.rows[(i * 3) + k].cells[(j * 3) + p] for k in range(3) for p in range(3)])
            for i in range(3)
            for j in range(3)
        ]


class SudokuGame(ui.View):
    def __init__(self, puzzle: Puzzle, author: discord.Member):
        super().__init__(timeout=600)
        self.puzzle = puzzle
        self.author = author
        self.level: Literal["Puzzle", "Block", "Cell"] = "Puzzle"
        self.block: Optional[Block] = None
        self.cell: Optional[Cell] = None
        self.noting_mode = False

    def enable_keypad(self):
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
        embed = discord.Embed(title="Sudoku", description=f"```{self.puzzle}```", color=discord.Color.blurple())
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text="Play Sudoku by Typing !sudoku")
        embed.add_field(name="Choose a block", value="Use the keypad to choose a block", inline=True)
        return embed

    async def keypad_callback(self, interaction: discord.Interaction, button: ui.Button, key: int):
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
        elif self.level == "Cell":
            if self.cell is not None:
                if self.cell.editable and not self.noting_mode:
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
        return interaction.user.id == self.author.id

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: ui.Item[Any]) -> None:
        if isinstance(error, discord.app_commands.CheckFailure):
            await interaction.response.send_message("Only the invoker can play this instance of Sudoku", ephemeral=True)
        else:
            await super().on_error(interaction, error, item)

    @ui.button(label="Back", disabled=True, style=discord.ButtonStyle.green, row=0)
    async def back(self, interaction: discord.Interaction, button: ui.Button):
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
        await self.keypad_callback(interaction, button, 0)

    @ui.button(label="2", style=discord.ButtonStyle.blurple, row=0)
    async def two(self, interaction: discord.Interaction, button: ui.Button):
        await self.keypad_callback(interaction, button, 1)

    @ui.button(label="3", style=discord.ButtonStyle.blurple, row=0)
    async def three(self, interaction: discord.Interaction, button: ui.Button):
        await self.keypad_callback(interaction, button, 2)

    @ui.button(label=" ", style=discord.ButtonStyle.grey, row=0, disabled=True)
    async def placeholder_0(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("This button is disabled", ephemeral=True)

    @ui.button(label="Stop", style=discord.ButtonStyle.red, row=1)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        solution = self.puzzle.solution
        embed = discord.Embed(
            title="**FAILED** Sudoku", description=f"The solution was\n```{solution}```", color=discord.Color.red()
        )
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text="Play Sudoku by Typing !sudoku")
        self.disable_keypad()
        self.mode.disabled = True
        self.cancel.disabled = True
        self.back.disabled = True
        self.stop()
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="4", style=discord.ButtonStyle.blurple, row=1)
    async def four(self, interaction: discord.Interaction, button: ui.Button):
        await self.keypad_callback(interaction, button, 3)

    @ui.button(label="5", style=discord.ButtonStyle.blurple, row=1)
    async def five(self, interaction: discord.Interaction, button: ui.Button):
        await self.keypad_callback(interaction, button, 4)

    @ui.button(label="6", style=discord.ButtonStyle.blurple, row=1)
    async def six(self, interaction: discord.Interaction, button: ui.Button):
        await self.keypad_callback(interaction, button, 5)

    @ui.button(label=" ", style=discord.ButtonStyle.grey, row=1, disabled=True)
    async def placeholder_1(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("This button is disabled", ephemeral=True)

    @ui.button(label="Clear", style=discord.ButtonStyle.red, row=2)
    async def clear(self, interaction: discord.Interaction, button: ui.Button):
        if self.level == "Puzzle":
            self.puzzle.reset()
            await interaction.response.edit_message(embed=self.block_choose_embed(), view=self)
        elif self.level == "Block":
            if self.block is not None:
                self.block.clear()
            await interaction.response.edit_message(embed=self.cell_choose_embed(), view=self)
        elif self.level == "Cell":
            if self.cell is not None:
                if self.cell.editable:
                    self.cell.clear()
            await interaction.response.edit_message(embed=self.change_cell_prompt_embed(), view=self)

    @ui.button(label="7", style=discord.ButtonStyle.blurple, row=2)
    async def seven(self, interaction: discord.Interaction, button: ui.Button):
        await self.keypad_callback(interaction, button, 6)

    @ui.button(label="8", style=discord.ButtonStyle.blurple, row=2)
    async def eight(self, interaction: discord.Interaction, button: ui.Button):
        await self.keypad_callback(interaction, button, 7)

    @ui.button(label="9", style=discord.ButtonStyle.blurple, row=2)
    async def nine(self, interaction: discord.Interaction, button: ui.Button):
        await self.keypad_callback(interaction, button, 8)

    @ui.button(label=" ", style=discord.ButtonStyle.grey, row=2, disabled=True)
    async def placeholder_3(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("This button is disabled", ephemeral=True)

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
        raise NotImplementedError("Only solve mode is implemented currently")


class Sudoku(commands.Cog):
    def __init__(self, bot: CBot):
        self.bot = bot

    @commands.command(name="sudoku", aliases=["sud"])
    async def sudoku(self, ctx: commands.Context):
        """
        Generates a sudoku puzzle.
        """
        if ctx.guild is None:
            return
        if ctx.channel.id not in (839690221083820032, 687817008355737606):
            return
        if not any(338173415527677954 == role.id for role in ctx.author.roles):  # type: ignore
            return
        if ctx.channel.id == 687817008355737606 and ctx.author.id != 363095569515806722:
            return
        puzzle = await self.bot.loop.run_in_executor(self.bot.process_pool, Puzzle.new)
        view = SudokuGame(puzzle, ctx.author)  # type: ignore
        await ctx.send(embed=view.block_choose_embed(), view=view)


async def setup(bot):
    await bot.add_cog(Sudoku(bot))
