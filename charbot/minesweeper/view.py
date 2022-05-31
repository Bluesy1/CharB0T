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
"""Minesweeper view."""
import random

import discord
from discord import Interaction, SelectOption, ui


straight_titles = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "A", "B"]
indicator_emojis = [
    "0\N{combining enclosing keycap}",
    "1\N{combining enclosing keycap}",
    "2\N{combining enclosing keycap}",
    "3\N{combining enclosing keycap}",
    "4\N{combining enclosing keycap}",
    "5\N{combining enclosing keycap}",
    "6\N{combining enclosing keycap}",
    "7\N{combining enclosing keycap}",
    "8\N{combining enclosing keycap}",
    "9\N{combining enclosing keycap}",
    "\N{keycap ten}",
    ":regional_indicator_a:",
    ":regional_indicator_b:",
]


class TestModal(ui.Modal):
    move = ui.Select(
        placeholder="Select a move",
        min_values=1,
        max_values=1,
        options=[
            SelectOption(label="Togggle Flag", value="flagged", emoji="🚩"),
            SelectOption(label="Reveal", value="revealed", emoji="⛏️"),
            SelectOption(label="Chord", value="chord", emoji="⚒️"),
        ],
    )

    row = ui.Select(
        placeholder="Select a row",
        min_values=1,
        max_values=1,
        options=[
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
        ],
    )

    column = ui.Select(
        placeholder="Select a column",
        min_values=1,
        max_values=1,
        options=[
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
        ],
    )

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.send_message(
            f"You {self.move.values[0]} {self.row.values[0]}-{self.column.values[0]}"
        )


class TestView(ui.View):
    @ui.button(
        label="Open Modal",
        emoji="🔎",
        style=discord.ButtonStyle.primary,
    )
    async def open_modal(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_modal(TestModal(title="Test Modal"))


text = "⏹️" + "".join(indicator_emojis) + "\n"
for emoji in indicator_emojis:
    text += emoji
    for i in range(13):
        text += random.choice(["⏹️", "⏹️", "⏹️", "💣"])
    text += "\n"
