# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Gang war utils."""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from enum import Enum
from itertools import islice
from typing import TYPE_CHECKING, Literal, Final

import discord
from discord import Color


if TYPE_CHECKING:
    from .types import Item


__all__ = ("ColorOpts", "rep_to_control", "BASE_GANG_COST", "GANGS", "SQL_MONTHLY", "item_embed_pages")


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


def item_embed_pages(
    items: Iterable[Item], items_type: Literal["personal", "gang"], owned: bool
) -> Iterator[discord.Embed]:  # pragma: no cover
    """Create an embed for each page of items.

    Parameters
    ----------
    items : Iterable[Item]
        The items.
    items_type : {"personal", "gang"}
        The type of items, can be personal or gang.
    owned : bool
        Whether the items are owned or not.

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
            description=f"A list of some or all of the {items_type} items you {'own' if owned else 'can buy'}.",
            timestamp=discord.utils.utcnow(),
        )
        for item in batch:
            embed.add_field(
                name=item.name,
                value=f"{item.description}\nCost: {item.value}"
                f"{f'{newline}Quantity: {item.quantity}' if item.quantity is not None else ''}",
                inline=False,
            )
        yield embed
