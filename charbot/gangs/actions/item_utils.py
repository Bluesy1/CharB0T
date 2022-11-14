# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Collection of shared utils for user and gang inventories."""
from __future__ import annotations

from typing import overload

import asyncpg

from ..types import TerritoryDefender, TerritoryOffense


async def check_defensive_item(conn: asyncpg.Connection, user_id: int) -> str | TerritoryDefender:
    """Check if a user can use defensive items.

    Parameters
    ----------
    conn : asyncpg.Connection
        The database connection.
    user_id : int
        The user's ID.

    Returns
    -------
    item : str | TerritoryDefender
        The error message, or information about the territory being defended.
    """
    raid: TerritoryDefender = await conn.fetchrow(  # pyright: ignore[reportGeneralTypeIssues]
        "SELECT defenders, id, defense FROM territories WHERE "
        "gang = (SELECT gang FROM gang_members WHERE user_id = $1) AND raid_end IS NOT NULL",
        user_id,
    )
    if raid is None:
        return "Your gang is not defending against a raid, you cannot use defensive items at this time."
    if user_id not in raid["defenders"]:
        return (
            "You are not participating in your gang's raid defense, you cannot use defensive items without"
            " joining a raid defense."
        )
    return raid


async def check_offensive_item(conn: asyncpg.Connection, user_id: int) -> str | TerritoryOffense:
    """Check if a user can use offensive items.

    Parameters
    ----------
    conn : asyncpg.Connection
        The database connection.
    user_id : int
        The user's ID.

    Returns
    -------
    item : str | TerritoryOffense
        The error message, or information about the territory being raided.
    """
    raid: TerritoryOffense = await conn.fetchrow(  # pyright: ignore[reportGeneralTypeIssues]
        "SELECT attackers, id, attack FROM territories WHERE "
        "gang = (SELECT gang FROM gang_members WHERE user_id = $1) AND raid_end IS NOT NULL",
        user_id,
    )
    if raid is None:
        return "Your gang is not attacking another gang, you cannot use offensive items at this time."
    if user_id not in raid["attackers"]:
        return "You are not participating in your gang's raid, you cannot use offensive items without joining a raid."
    return raid


@overload
async def consume_item(
    conn: asyncpg.Connection, item_id: int, quantity: int, /, *, user: int, gang: None = None
) -> None:  # pragma: no cover
    ...


@overload
async def consume_item(
    conn: asyncpg.Connection, item_id: int, quantity: int, /, *, user: None = None, gang: str
) -> None:  # pragma: no cover
    ...


async def consume_item(
    conn: asyncpg.Connection, item_id: int, quantity: int, /, *, user: int | None = None, gang: str | None = None
) -> None:
    """Consume an item.

    Parameters
    ----------
    conn: asyncpg.Connection
        The database connection.
    item_id : int
        The item's ID.
    quantity : int
        The number of this item the user has.
    user : int | None, optional
        The user's ID, or leave blank if the item is a gang item.
    gang : str | None, optional
        The gang's name, or leave blank if the item is a user item.
    """
    if user is not None and gang is not None:
        raise TypeError("Cannot specify both user_id and gang.")
    if user is None and gang is None:
        raise TypeError("Must specify either user_id or gang.")
    if quantity == 1:
        if gang is not None:
            await conn.execute("DELETE FROM gang_inventory WHERE gang = $1 AND item = $2", gang, item_id)
        else:
            await conn.execute("DELETE FROM user_inventory WHERE user_id = $1 AND item = $2", user, item_id)
    else:
        if gang is not None:
            await conn.execute(
                "UPDATE gang_inventory SET quantity = quantity - 1 WHERE gang = $1 AND item = $2", gang, item_id
            )
        else:
            await conn.execute(
                "UPDATE user_inventory SET quantity = quantity - 1 WHERE user_id = $1 AND item = $2", user, item_id
            )
