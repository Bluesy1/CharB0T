# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Collection of functions for joining a gang."""
from __future__ import annotations

import asyncpg


async def try_join(conn: asyncpg.Connection, gang: str, user: int) -> str | tuple[int, int]:
    """Try to join a gang.

    Parameters
    ----------
    conn : asyncpg.Connection
        The database connection.
    gang : str
        The name of the gang to join.
    user : int
        The ID of the user to join the gang.

    Returns
    -------
    str | tuple[int, int]
        The error message, or the remaining and needed rep
    """
    if not await conn.fetchval("SELECT 1 FROM gangs WHERE name = $1", gang):
        return "That gang doesn't exist!"
    pts: int | None = await conn.fetchval("SELECT points FROM users WHERE id = $1", user)
    if pts is None:
        return "You have never gained any points, try gaining some first!"
    needed: int = await conn.fetchval(
        "SELECT join_base + (join_slope * (SELECT COUNT(*) FROM gang_members WHERE gang = $1))"
        " FROM gangs WHERE name = $1",
        gang,
    )
    if needed > pts:
        return (
            f"You don't have enough rep to join that gang! You need at least {needed} rep to join that gang,"
            f" and you have {pts}."
        )
    return (
        await conn.fetchval("UPDATE users SET points = points - $1 WHERE id = $2 RETURNING points", needed, user),
        needed,
    )
