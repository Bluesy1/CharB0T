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
"""Minesweeper modals."""
import discord
from discord import Interaction, SelectOption, ui

from . import Coordinate, Minesweeper, view


class RowSelect(ui.Select):
    def __init__(self):
        options = [
            SelectOption(label="Row 0", value="zero", emoji="0\N{combining enclosing keycap}"),
            SelectOption(label="Row 1", value="one", emoji="1\N{combining enclosing keycap}"),
            SelectOption(label="Row 2", value="two", emoji="2\N{combining enclosing keycap}"),
            SelectOption(label="Row 3", value="three", emoji="3\N{combining enclosing keycap}"),
            SelectOption(label="Row 4", value="four", emoji="4\N{combining enclosing keycap}"),
            SelectOption(label="Row 5", value="five", emoji="5\N{combining enclosing keycap}"),
            SelectOption(label="Row 6", value="six", emoji="6\N{combining enclosing keycap}"),
            SelectOption(label="Row 7", value="seven", emoji="7\N{combining enclosing keycap}"),
            SelectOption(label="Row 8", value="eight", emoji="8\N{combining enclosing keycap}"),
            SelectOption(label="Row 9", value="nine", emoji="9\N{combining enclosing keycap}"),
            SelectOption(label="Row 10", value="ten", emoji="\N{keycap ten}"),
            SelectOption(label="Row A", value="eleven", emoji="🇦"),
            SelectOption(label="Row B", value="twelve", emoji="🇧"),
        ]
        placeholder = "Select a row"
        super().__init__(options=options, placeholder=placeholder, min_values=1, max_values=1)


class ColumnSelect(ui.Select):
    def __init__(self):
        options = [
            SelectOption(label="Column 0", value="zero", emoji="0\N{combining enclosing keycap}"),
            SelectOption(label="Column 1", value="one", emoji="1\N{combining enclosing keycap}"),
            SelectOption(label="Column 2", value="two", emoji="2\N{combining enclosing keycap}"),
            SelectOption(label="Column 3", value="three", emoji="3\N{combining enclosing keycap}"),
            SelectOption(label="Column 4", value="four", emoji="4\N{combining enclosing keycap}"),
            SelectOption(label="Column 5", value="five", emoji="5\N{combining enclosing keycap}"),
            SelectOption(label="Column 6", value="six", emoji="6\N{combining enclosing keycap}"),
            SelectOption(label="Column 7", value="seven", emoji="7\N{combining enclosing keycap}"),
            SelectOption(label="Column 8", value="eight", emoji="8\N{combining enclosing keycap}"),
            SelectOption(label="Column 9", value="nine", emoji="9\N{combining enclosing keycap}"),
            SelectOption(label="Column 10", value="ten", emoji="\N{keycap ten}"),
            SelectOption(label="Column A", value="eleven", emoji="🇦"),
            SelectOption(label="Column B", value="twelve", emoji="🇧"),
        ]
        placeholder = "Select a row"
        super().__init__(options=options, placeholder=placeholder, min_values=1, max_values=1)


class MoveModal(ui.Modal, title="Move"):
    def __init__(self, game: view.MinesweeperView):
        self.game = game
        super().__init__(timeout=60)

    move = ui.Select(
        placeholder="Select a move",
        min_values=1,
        max_values=1,
        options=[
            SelectOption(
                label="Togggle Flag",
                value="flagged",
                description="Add or remove a flag from a tile",
                emoji="🚩",
            ),
            SelectOption(
                label="Reveal",
                value="revealed",
                description="Uncover a cell and reveal it",
                emoji="⛏️",
            ),
            SelectOption(
                label="Chord",
                value="chord",
                description="Uncover all unmarked tiles surrounding a number if there are that number of"
                " flagged tiles around it",
                emoji="⚒️",
            ),
        ],
    )

    row = RowSelect()
    column = ColumnSelect()

    async def on_submit(self, interaction: Interaction) -> None:
        raise NotImplementedError()


class StartModal(ui.Modal):

    row = RowSelect()
    column = ColumnSelect()

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        puzzle = Minesweeper(Coordinate[self.row.values[0]], Coordinate[self.column.values[0]])
        game = view.MinesweeperView(puzzle)
        await interaction.followup.send(
            embed=discord.Embed(title="Minesweeper", description=str(puzzle), color=discord.Color.red()),
            view=game,
        )
