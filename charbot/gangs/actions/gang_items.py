# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Collection of functions for buying, retrieving, and using gang items."""
from __future__ import annotations

from typing import TYPE_CHECKING

import asyncpg
from discord.app_commands import Choice

from ..types import Item
from ..utils import ItemsView

if TYPE_CHECKING:  # pragma: no cover
    from ... import CBot, GuildInteraction


async def view_available_items_autocomplete(interaction: GuildInteraction[CBot], current: str) -> list[Choice[str]]:
    """Autocomplete for viewing available items.

    Parameters
    ----------
    interaction : GuildInteraction[CBot]
        The interaction.
    current : str
        The current string.

    Returns
    -------
    choices : list[Choice[str]]
        The choices.
    """
    async with interaction.client.pool.acquire() as conn:
        if not await conn.fetchval(
            "SELECT (leader OR leadership) AS is_leader FROM gang_members WHERE user_id = $1", interaction.user.id
        ):
            return []
        items = await conn.fetch("SELECT name, value FROM gang_items ORDER BY value")
        return [
            Choice(name=f"{i['name']} - Cost: {i['value']}", value=i["name"])
            for i in items
            if i["name"].startswith(current)
        ][:25]


async def view_item_autocomplete(interaction: GuildInteraction[CBot], current: str) -> list[Choice[str]]:
    """Autocomplete for viewing an item.

    Parameters
    ----------
    interaction : GuildInteraction[CBot]
        The interaction.
    current : str
        The current string.

    Returns
    -------
    choices : list[Choice[str]]
        The choices.
    """
    async with interaction.client.pool.acquire() as conn:
        if not await conn.fetchval(
            "SELECT (leader OR leadership) AS is_leader FROM gang_members WHERE user_id = $1", interaction.user.id
        ):
            return []
        items = await interaction.client.pool.fetch(
            "SELECT name FROM gang_inventory JOIN gang_items gi on gang_inventory.item = gi.id "
            "WHERE gang = (SELECT gang FROM gang_members WHERE user_id = $1)",
            interaction.user.id,
        )
        return [Choice(name=i["name"], value=i["name"]) for i in items if i["name"].startswith(current)][:25]


async def try_buy_item(pool: asyncpg.Pool, user_id: int, item_name: str) -> str | int:
    """Try to buy a gang item

    Parameters
    ----------
    pool : asyncpg.Pool
        The pool.
    user_id : int
        The user's ID.
    item_name : str
        The item's name.

    Returns
    -------
    remaining : str | int
        The remaining points, or a string error.
    """
    async with pool.acquire() as conn, conn.transaction():
        if not await conn.fetchval(
            "SELECT (leader OR leadership) AS is_leader FROM gang_members WHERE user_id = $1", user_id
        ):
            return "You are not in the leadership of a gang, you cannot buy gang items."
        item = await conn.fetchrow("SELECT * FROM gang_items WHERE name = $1", item_name)
        if item is None:
            return f"The item `{item_name}` you requested doesn't exist."
        control: int = await conn.fetchval(
            "SELECT control FROM gangs WHERE name = (SELECT gang FROM gang_members WHERE user_id = $1)", user_id
        )
        if control < item["value"]:
            return f"Your gang doesn't have enough control to buy that. (Have: {control}, Need: {item['value']})"
        await conn.execute(
            "INSERT INTO gang_inventory (gang, item, quantity) VALUES "
            "((SELECT gang FROM gang_members WHERE user_id = $1), $2, 1) ON CONFLICT(gang, item) "
            "DO UPDATE SET quantity = (SELECT quantity + 1 FROM gang_inventory WHERE"
            " gang = excluded.gang AND item = excluded.item)",
            user_id,
            item["id"],
        )
        return await conn.fetchval(
            "UPDATE gangs SET control = control - $1 WHERE name = (SELECT gang FROM gang_members WHERE user_id = $2)"
            " RETURNING control",
            item["value"],
            user_id,
        )


async def try_display_inventory(pool: asyncpg.Pool, user_id: int) -> str | ItemsView:
    """Try to display the user's gang inventory.

    Parameters
    ----------
    pool : asyncpg.Pool
        The pool.
    user_id : int
        The user's ID.

    Returns
    -------
    items : str | ItemsView
        The items, or a string error.
    """
    async with pool.acquire() as conn:
        if not await conn.fetchval(
            "SELECT (leader OR leadership) AS is_leader FROM gang_members WHERE user_id = $1", user_id
        ):
            return "You are not in the leadership of a gang, you cannot view your gang's inventory."
        items = await conn.fetch(
            "SELECT name, description, value, quantity FROM gang_items INNER JOIN gang_inventory gi ON id = gi.item "
            "WHERE gang = (SELECT gang FROM gang_members WHERE user_id = $1)",
            user_id,
        )
        if not items:
            return "Your gang doesn't have any items."
        return ItemsView([Item(**item) for item in items], user_id)


async def try_display_available_items(pool: asyncpg.Pool, user_id: int) -> str | ItemsView:
    """Try to display the available items.

    Parameters
    ----------
    pool : asyncpg.Pool
        The pool.
    user_id : int
        The user's ID.

    Returns
    -------
    items : str | ItemsView
        The items, or a string error.
    """
    async with pool.acquire() as conn:
        if not await conn.fetchval(
            "SELECT (leader OR leadership) AS is_leader FROM gang_members WHERE user_id = $1", user_id
        ):
            return "You are not in the leadership of a gang, you cannot view the available items."
        items = await conn.fetch("SELECT name, description, value, NULL as quantity FROM gang_items")
        if not items:
            return "There are no items available."
        return ItemsView([Item(**item) for item in items], user_id)
