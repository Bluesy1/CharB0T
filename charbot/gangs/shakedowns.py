# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Shakedown functions."""
from __future__ import annotations

import random
from typing import Final

import asyncpg


__all__ = ("do_shakedown",)

ITEM_FIND_CHANCE: Final[float] = 0.2  # 20% chance to find an item.


async def shakedown_chance(pool: asyncpg.Pool) -> float:
    """Calculate the chance of a shakedown succeeding.

    Parameters
    ----------
    pool : asyncpg.Pool
        The database pool.

    Returns
    -------
    chance:float
        The chance of a shakedown happening, 0 is 0%, 1 is 100%.
    """
    async with pool.acquire() as conn:
        user_items: int = await conn.fetchval("SELECT SUM(quantity) FROM user_inventory")
        gang_items: int = await conn.fetchval("SELECT SUM(quantity) FROM gang_inventory")
        total_items: int = user_items + gang_items
    return max(min(total_items / 100, 1), 0)


async def do_shakedown(pool: asyncpg.Pool, *, force: bool = False) -> int:
    """Run a shakedown.

    Parameters
    ----------
    pool : asyncpg.Pool
        The database pool.
    force : bool, optional
        Whether to force a shakedown, by default False

    Returns
    -------
    found: int
        The number of items found.
    """
    chance: float = await shakedown_chance(pool)
    items: int = 0
    if force or chance > random.random():
        async with pool.acquire() as conn:
            for i in await conn.fetch("SELECT * FROM user_inventory"):
                if random.random() < ITEM_FIND_CHANCE:
                    items += 1
                    if i["quantity"] > 1:
                        await conn.execute(
                            "UPDATE user_inventory SET quantity = quantity - 1 WHERE user_id = $1 AND item = $2",
                            i["user_id"],
                            i["item"],
                        )
                    else:
                        await conn.execute(
                            "DELETE FROM user_inventory WHERE user_id = $1 AND item = $2", i["user_id"], i["item"]
                        )
            for i in await conn.fetch("SELECT * FROM gang_inventory"):
                if random.random() < ITEM_FIND_CHANCE:
                    items += 1
                    if i["quantity"] > 1:
                        await conn.execute(
                            "UPDATE gang_inventory SET quantity = quantity - 1 WHERE gang = $1 AND item = $2",
                            i["gang"],
                            i["item"],
                        )
                    else:
                        await conn.execute(
                            "DELETE FROM gang_inventory WHERE gang = $1 AND item = $2", i["gang"], i["item"]
                        )
    return items
