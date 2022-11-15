# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import Final

import asyncpg

from ..types import Territory, Gang

RAID_START_COST: Final[int] = 1000


async def try_start_raid(gang: Gang, territory: Territory, pool: asyncpg.Pool) -> bool:
    """Check if the gang can start a raid, and if they can, do it

    Parameters
    ----------
    gang : Gang
        The gang trying to start a raid
    territory : Territory
        The territory the gang is trying to raid
    pool : asyncpg.Pool
        The database pool

    Returns
    -------
    bool
        True if the raid was started, False otherwise
    """
    if gang["control"] < RAID_START_COST:
        return False
    if territory["raider"] is not None:
        return False
    async with pool.acquire() as conn, conn.transaction():
        current_raid = await conn.fetch("SELECT * FROM territories WHERE raider = $1", gang["name"])
        if current_raid:
            return False
        await conn.execute("UPDATE gangs SET control = control - $1 WHERE name = $2", RAID_START_COST, gang["name"])
        await conn.execute(
            "UPDATE territories SET raider = $1, raid_end = CURRENT_TIMESTAMP + '7 days'::interval WHERE id = $2",
            gang["name"],
            territory["id"],
        )
    return True


async def end_raid(pool: asyncpg.Pool, territory: Territory) -> str:
    """End a raid

    Parameters
    ----------
    pool: asyncpg.Pool
        The database pool.
    territory : Territory
        The territory to end the raid on

    Returns
    -------
    result: str
        The result message
    """
    async with pool.acquire() as conn, conn.transaction():
        await conn.execute(
            "UPDATE territories SET raider = NULL, raid_end = NULL, attack = 0, defense = 0,"
            " attackers = '{}'::BIGINT[], defenders = '{}'::BIGINT[] WHERE id = $1",
            territory["id"],
        )
        if territory["defense"] < territory["attack"]:
            await conn.execute("UPDATE territories SET gang = $1 WHERE id = $2", territory["raider"], territory["id"])
            return (
                f"{territory['raider']} has successfully raided {territory['name']} and taken it over from "
                f"{territory['gang']}!"
            )
        return f"{territory['gang']} has successfully defended {territory['name']} from {territory['raider']}!"
