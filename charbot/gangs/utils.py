# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Gang war utils."""
from __future__ import annotations

from collections.abc import Iterator
from enum import Enum
from itertools import islice
from typing import TYPE_CHECKING, Literal, Final

import discord
from discord import Color


if TYPE_CHECKING:
    from .types import Item
    from .. import GuildComponentInteraction as Interaction, CBot


__all__ = ("ColorOpts", "rep_to_control", "BASE_GANG_COST", "GANGS", "SQL_MONTHLY", "item_embed_pages", "ItemsView")


class ColorOpts(Enum):
    Black = Color(0x36454F)  # actually called charcoal, but is close enough to black
    Red = Color.dark_red()
    Green = Color.green()
    Blue = Color(0x0000FF)
    Purple = Color(0x800080)
    Violet = Color(0xEE82EE)
    Yellow = Color(0xFFD700)
    Orange = Color(0xFF6200)
    White = Color(0xC0C0C0)  # actually called silver, but is close enough to white


def rep_to_control(rep: int) -> int:
    """Convert reputation to control.

    Parameters
    ----------
    rep : int
        The reputation to convert

    Returns
    -------
    control: int
        The control gained from the reputation.
    """
    return rep // 50  # TODO: make this a config option/proper formula


BASE_GANG_COST: Final[int] = 100
GANGS: Final = Literal["Black", "Red", "Green", "Blue", "Purple", "Violet", "Yellow", "Orange", "White"]
SQL_MONTHLY = """
DO $$
DECLARE
user_id BIGINT;
gang VARCHAR(10);
BEGIN
UPDATE gangs SET all_paid = TRUE WHERE all_paid IS NOT TRUE;
FOR user_id, gang IN SELECT gang_members.user_id, gang_members.gang FROM gang_members
    LOOP
    IF (SELECT points from users WHERE id == user_id) >= (SELECT upkeep_base + (
        upkeep_slope * (SELECT COUNT(*) FROM gang_members WHERE gang = gang)) FROM gangs WHERE name = gang)
        THEN
            UPDATE users SET points = points - (SELECT upkeep_base + (
                upkeep_slope * (SELECT COUNT(*) FROM gang_members WHERE gang = gang))
                                                FROM gangs WHERE name = gang) WHERE id = user_id;
    ELSE
        UPDATE gang_members SET paid = FALSE WHERE user_id = user_id;
        UPDATE gangs SET all_paid = FALSE WHERE name = gang;
    END IF;
END LOOP;
END $$;
"""


def item_embed_pages(items: list[Item]) -> Iterator[discord.Embed]:
    """Create an embed for each page of items.

    Parameters
    ----------
    items : list[Item]
        The items.

    Yields
    ------
    embed : discord.Embed
        The embed of the items.
    """
    it = iter(items)
    newline = ord("\n")
    while True:
        batch = list(islice(it, 25))
        if not batch:
            break
        embed = discord.Embed(
            title="Items",
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow(),
        )
        for item in batch:
            embed.add_field(
                name=item.name,
                value=f"{item.description}\nCost: {item.cost}"
                f"{f'{newline}Quantity: {item.quantity}' if item.quantity is not None else ''}",
                inline=False,
            )
        yield embed


class ItemsView(discord.ui.View):
    """View to display items"""

    def __init__(self, items: list[Item], invoker: int):
        super().__init__(timeout=300)
        self.invoker = invoker
        self.embeds = list(item_embed_pages(items))
        self.current = 0
        self.max = len(self.embeds) - 1

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        """Check if the interaction is valid."""
        ret = interaction.user.id == self.invoker
        if not ret:
            await interaction.response.send_message("You can't do that!", ephemeral=True)
        return ret

    @discord.ui.button(emoji="\u23EA", style=discord.ButtonStyle.blurple, disabled=True)  # pyright: ignore
    async def first(self, interaction: Interaction[CBot], button: discord.Button) -> None:
        """Go to the first page."""
        self.current = 0
        button.disabled = self.back.disabled = True
        self.next.disabled = self.last.disabled = False
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)

    @discord.ui.button(emoji="\u25C0", style=discord.ButtonStyle.blurple, disabled=True)  # pyright: ignore
    async def back(self, interaction: Interaction[CBot], button: discord.Button) -> None:
        """Go to the previous page."""
        self.current -= 1
        button.disabled = self.first.disabled = self.current == 0
        self.next.disabled = self.last.disabled = False
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)

    @discord.ui.button(emoji="\u23F9", style=discord.ButtonStyle.blurple)  # pyright: ignore[reportGeneralTypeIssues]
    async def stop(self, interaction: Interaction[CBot], _: discord.Button) -> None:
        """Stop the view."""
        await interaction.response.edit_message(embed=self.embeds[self.current], view=None)
        await interaction.delete_original_response()

    @discord.ui.button(emoji="\u25B6", style=discord.ButtonStyle.blurple)  # pyright: ignore[reportGeneralTypeIssues]
    async def next(self, interaction: Interaction[CBot], button: discord.Button) -> None:
        """Go to the next page."""
        self.current += 1
        button.disabled = self.last.disabled = self.current == self.max
        self.back.disabled = self.first.disabled = False
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)

    @discord.ui.button(emoji="\u23E9", style=discord.ButtonStyle.blurple)  # pyright: ignore[reportGeneralTypeIssues]
    async def last(self, interaction: Interaction[CBot], button: discord.Button) -> None:
        """Go to the last page."""
        self.current = self.max
        button.disabled = self.next.disabled = True
        self.back.disabled = self.first.disabled = False
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)
