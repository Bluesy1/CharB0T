# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Collection of functions for buying, retrieving, and using user items."""
from __future__ import annotations

from typing import TYPE_CHECKING

import asyncpg
from discord.app_commands import Choice

from ..types import Item
from ..utils import ItemsView

if TYPE_CHECKING:  # pragma: no cover
    from ... import CBot, GuildInteraction


async def view_available_items_autocomplete(interaction: GuildInteraction[CBot], current: str) -> list[Choice[str]]:
    """Autocomplete for buying an item.

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
        if not await conn.fetchrow("SELECT TRUE FROM gang_members WHERE user_id = $1", interaction.user.id):
            return []
        items = await conn.fetch("SELECT name, value FROM user_items ORDER BY value")
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
        if not await conn.fetchrow("SELECT TRUE FROM gang_members WHERE user_id = $1", interaction.user.id):
            return []
        items = await conn.fetch(
            "SELECT name FROM user_inventory JOIN user_items ui on ui.id = user_inventory.item WHERE user_id = $1",
            interaction.user.id,
        )
        return [Choice(name=i["name"], value=i["name"]) for i in items if i["name"].startswith(current)][:25]


async def try_buy_item(pool: asyncpg.Pool, user_id: int, item_name: str) -> str | int:
    """Try to buy a user item

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
        if not await conn.fetchval("SELECT TRUE FROM gang_members WHERE user_id = $1", user_id):
            return "You must be in a gang to buy items."
        item = await conn.fetchrow("SELECT * FROM user_items WHERE name = $1", item_name)
        if item is None:
            return f"The item `{item_name}` you requested doesn't exist."
        points: int = await conn.fetchval("SELECT points FROM users WHERE id = $1", user_id)
        if points < item["value"]:
            return f"You don't have enough rep to buy that. (Have: {points}, Need: {item['value']})"
        await conn.execute(
            "INSERT INTO user_inventory (user_id, item, quantity) VALUES ($1, $2, 1) ON CONFLICT(user_id, item) "
            "DO UPDATE SET quantity = (SELECT quantity + 1 FROM user_inventory WHERE user_id = $1 AND item = $2)",
            user_id,
            item["id"],
        )
        return await conn.fetchval(
            "UPDATE users SET points = points - $1 WHERE id = $2 RETURNING points", item["value"], user_id
        )


async def try_display_inventory(pool: asyncpg.Pool, user_id: int) -> str | ItemsView:
    """Try to display the user's inventory.

    Parameters
    ----------
    pool : asyncpg.Pool
        The database pool.
    user_id : int
        The user's ID.

    Returns
    -------
    items : str | ItemsView
        The view for the items, or a string error.
    """
    async with pool.acquire() as conn:
        items = await conn.fetch(
            "SELECT name, description, value, quantity "
            "FROM user_items INNER JOIN user_inventory ui on user_items.id = ui.item WHERE ui.user_id = $1",
            user_id,
        )
        if not items:
            return "You don't have any items."
        return ItemsView([Item(**item) for item in items], user_id)


async def try_display_available_items(pool: asyncpg.Pool, user_id: int) -> str | ItemsView:
    """Try to display the available items.

    Parameters
    ----------
    pool : asyncpg.Pool
        The database pool.
    user_id : int
        The user's ID.

    Returns
    -------
    items : str | ItemsView
        The view for the items, or a string error.
    """
    async with pool.acquire() as conn:
        if not await conn.fetchval("SELECT TRUE FROM gang_members WHERE user_id = $1", user_id):
            return "You must be in a gang to have items."
        items = await conn.fetch("SELECT name, description, value, NULL as quantity FROM user_items")
        if not items:
            return "There are no items available."
        return ItemsView([Item(**item) for item in items], user_id)
