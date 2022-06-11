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
"""View class."""
import datetime
from typing import Literal, Protocol

import asyncpg
import discord
from discord import ButtonStyle, Interaction, SelectOption, ui
from discord.utils import MISSING, utcnow

from . import Block, Cell, Puzzle


class CBot(Protocol):
    """Protocol for the CBot class."""

    pool: asyncpg.Pool

    async def give_game_points(
        self, member: discord.Member | discord.User, game: str, points: int, bonus: int = 0
    ) -> int:
        """Give points to a member for a game."""
        ...


# noinspection GrazieInspection
class Sudoku(ui.View):
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
    """

    def __init__(self, puzzle: Puzzle, author: discord.Member, bot: CBot):
        super().__init__(timeout=None)
        self.puzzle = puzzle
        self.author = author
        self.bot = bot
        self.level: Literal["Puzzle", "Block", "Cell"] = "Puzzle"
        self.block: Block = MISSING
        self.cell: Cell = MISSING
        self.noting_mode = False
        self.start_time = utcnow()
        self.moves = 0

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

    # noinspection DuplicatedCode
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
            self.one.disabled = not self.block[0].editable
            self.two.disabled = not self.block[1].editable
            self.three.disabled = not self.block[2].editable
            self.four.disabled = not self.block[3].editable
            self.five.disabled = not self.block[4].editable
            self.six.disabled = not self.block[5].editable
            self.seven.disabled = not self.block[6].editable
            self.eight.disabled = not self.block[7].editable
            self.nine.disabled = not self.block[8].editable
            self.clear.disabled = False
            self.back.disabled = False
        elif self.level == "Cell":
            self.back.disabled = False
            if self.cell.editable:
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
        embed = discord.Embed(title="Sudoku", description=f"```ansi\n{self.puzzle}```", color=discord.Color.blurple())
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text="Start playing by typing /programs sudoku")
        embed.add_field(
            name=f"Choose a value for the cell at {self.puzzle.location_of_cell(self.cell)}",
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
        embed = discord.Embed(title="Sudoku", description=f"```ansi\n{self.puzzle}```", color=discord.Color.blurple())
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text="Start playing by typing /programs sudoku")
        embed.add_field(
            name=f"Choose a cell from block {self.puzzle.block_index(self.block) + 1}",
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
        embed = discord.Embed(title="Sudoku", description=f"```ansi\n{self.puzzle}```", color=discord.Color.blurple())
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text="Start playing by typing /programs sudoku")
        embed.add_field(name="Choose a block", value="Use the keypad to choose a block", inline=True)
        return embed

    async def _on_win(self, interaction: Interaction):
        """Send the win embed.

        Parameters
        ----------
        interaction: Interaction
            The interaction that triggered the win.
        """
        self.disable_keypad()
        self.back.disabled = True
        self.cancel.disabled = True
        self.mode.disabled = True
        if self.cell is not MISSING:
            self.cell.selected = False
        embed = discord.Embed(
            title="**Solved!!** Sudoku",
            description=f"```ansi\n{self.puzzle}```",
            color=discord.Color.green(),
        )
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text="Start playing by typing /programs sudoku")
        time_taken = utcnow().replace(microsecond=0) - self.start_time.replace(microsecond=0)
        embed.add_field(name="Time Taken", value=f"{time_taken}", inline=True)
        points = await self.bot.give_game_points(self.author, "sudoku", 5, 10)
        embed.add_field(
            name="Reputation gained",
            value="15 Reputation" if points == 15 else f"{points} Reputation (Daily Cap Hit)",
            inline=True,
        )
        await interaction.edit_original_message(embed=embed, view=self)
        await self.bot.pool.execute(
            "UPDATE users SET sudoku_time = $1 WHERE id = $2 and sudoku_time > $1",
            time_taken,
            self.author.id,
        )

    # noinspection DuplicatedCode
    async def keypad_callback(self, interaction: Interaction, button: ui.Button, key: int):
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
        await interaction.response.defer(ephemeral=True)
        if self.level == "Puzzle":
            self.block = self.puzzle.blocks[key]
            self.block.selected = True
            self.level = "Block"
            self.update_keypad()
            await interaction.edit_original_message(embed=self.cell_choose_embed(), view=self)
        elif self.level == "Block":
            if self.block is not None:
                self.cell = self.block[key]
                self.level = "Cell"
                self.block.selected = False
                self.cell.selected = True
                self.update_keypad()
                await interaction.edit_original_message(embed=self.change_cell_prompt_embed(), view=self)
        elif self.level == "Cell":  # skipcq: PTC-W0048
            if self.cell is not None:  # skipcq: PTC-W0048
                if self.cell.editable and not self.noting_mode:
                    self.moves += 1
                    val = button.label
                    assert isinstance(val, str)  # skipcq: BAN-B101
                    self.cell.value = int(val)
                    self.level = "Block"
                    self.cell.possible_values.clear()
                    self.cell.selected = False
                    if self.block is not MISSING:
                        self.block.selected = True
                    self.cell = MISSING
                    if self.puzzle.is_solved:
                        await self._on_win(interaction)
                    else:
                        self.update_keypad()
                        await interaction.edit_original_message(embed=self.cell_choose_embed(), view=self)
                elif self.cell.editable and self.noting_mode:
                    val = button.label
                    assert isinstance(val, str)  # skipcq: BAN-B101
                    real_val = int(val)
                    if real_val not in self.cell.possible_values:
                        self.cell.possible_values.add(real_val)
                    else:
                        self.cell.possible_values.remove(real_val)
                    raise NotImplementedError("Noting mode not implemented")
                else:
                    if self.cell is not MISSING:
                        self.cell.selected = False
                    if self.block is not MISSING:
                        self.block.selected = False
                    self.cell = MISSING
                    self.level = "Block"
                    self.update_keypad()
                    await interaction.edit_original_message(embed=self.cell_choose_embed(), view=self)

    @ui.button(label="Back", disabled=True, style=ButtonStyle.green, row=0)
    async def back(self, interaction: Interaction, button: ui.Button):
        """Back to the previous level of the puzzle.

        This acts dynamically based on the current focus level of the puzzle.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        if self.level == "Puzzle":
            button.disabled = True
            self.enable_keypad()
            await interaction.response.edit_message(view=self)
        elif self.level == "Block":
            self.level = "Puzzle"
            button.disabled = True
            if self.block is not MISSING:
                self.block.selected = False
            self.block = MISSING
            self.enable_keypad()
            await interaction.response.edit_message(embed=self.block_choose_embed(), view=self)
        elif self.level == "Cell":
            self.level = "Block"
            if self.cell is not MISSING:
                self.cell.selected = False
            if self.block is not MISSING:
                self.block.selected = True
            self.cell = MISSING
            self.enable_keypad()
            await interaction.response.edit_message(embed=self.cell_choose_embed(), view=self)

    @ui.button(label="1", style=ButtonStyle.blurple, row=0)
    async def one(self, interaction: Interaction, button: ui.Button):
        """Keypad callback for the 1 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 0)

    @ui.button(label="2", style=ButtonStyle.blurple, row=0)
    async def two(self, interaction: Interaction, button: ui.Button):
        """Keypad callback for the 2 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 1)

    @ui.button(label="3", style=ButtonStyle.blurple, row=0)
    async def three(self, interaction: Interaction, button: ui.Button):
        """Keypad callback for the 3 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 2)

    # noinspection PyUnusedLocal,DuplicatedCode
    @ui.button(label="Stop", style=ButtonStyle.red, row=1)
    async def cancel(self, interaction: Interaction, button: ui.Button):  # skipcq: PYL-W0613
        """Cancel/Stop button callback.

        This button displays a solution and turns off the view.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        solution = self.puzzle.solution
        embed = discord.Embed(
            title="**FAILED** Sudoku",
            description=f"The solution was\n```ansi\n{solution}```",
            color=discord.Color.red(),
        )
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text="Start playing by typing /programs sudoku")
        time_taken = utcnow().replace(microsecond=0) - self.start_time.replace(microsecond=0)
        embed.add_field(name="Time Taken", value=f"{time_taken}", inline=True)
        if (utcnow() - self.start_time) > datetime.timedelta(minutes=3) and self.moves > 10:
            embed.add_field(name="Time Taken", value=f"{time_taken}", inline=True)
            points = await self.bot.give_game_points(self.author, "sudoku", 5, 0)
            embed.add_field(
                name="Reputation gained",
                value="5 Reputation" if points == 5 else f"{points} Reputation (Daily Cap Hit)",
                inline=True,
            )
        else:
            embed.add_field(name="Reputation gained", value="0 Reputation", inline=True)
        self.disable_keypad()
        self.mode.disabled = True
        self.cancel.disabled = True
        self.back.disabled = True
        self.stop()
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="4", style=ButtonStyle.blurple, row=1)
    async def four(self, interaction: Interaction, button: ui.Button):
        """Keypad callback for the 4 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 3)

    @ui.button(label="5", style=ButtonStyle.blurple, row=1)
    async def five(self, interaction: Interaction, button: ui.Button):
        """Keypad callback for the 5 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 4)

    @ui.button(label="6", style=ButtonStyle.blurple, row=1)
    async def six(self, interaction: Interaction, button: ui.Button):
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
    @ui.button(label="Clear", style=ButtonStyle.red, row=2)
    async def clear(self, interaction: Interaction, button: ui.Button):  # skipcq: PYL-W0613
        """Clear button callback.

        Clears the current cell, block or resets the puzzle depending on the current state.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
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

    @ui.button(label="7", style=ButtonStyle.blurple, row=2)
    async def seven(self, interaction: Interaction, button: ui.Button):
        """Keypad callback for the 7 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 6)

    @ui.button(label="8", style=ButtonStyle.blurple, row=2)
    async def eight(self, interaction: Interaction, button: ui.Button):
        """Keypad callback for the 8 button.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await self.keypad_callback(interaction, button, 7)

    @ui.button(label="9", style=ButtonStyle.blurple, row=2)
    async def nine(self, interaction: Interaction, button: ui.Button):
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
            SelectOption(label="Solve Mode", value="Solve", description="Mode to solve the puzzle in"),
            SelectOption(label="Note Mode", value="Note", description="Mode to note individual cells of the puzzle in"),
        ],
    )
    async def mode(self, interaction: Interaction, select: ui.Select):
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
