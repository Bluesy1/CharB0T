# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import asyncpg

from . import _types


class Gang:
    """Class representing a gang.

    Parameters
    ----------
    payload : _types.Gang
        The payload to construct from.
    """

    __slots__ = (
        "name",
        "color",
        "leader",
        "role",
        "channel",
        "control",
        "join_base",
        "join_slope",
        "upkeep_base",
        "upkeep_slope",
        "all_paid",
    )

    def __init__(self, payload: _types.Gang):
        self.name = payload["name"]
        self.color = payload["color"]
        self.leader = payload["leader"]
        self.role = payload["role"]
        self.channel = payload["channel"]
        self.control = payload["control"]
        self.join_base = payload["join_base"]
        self.join_slope = payload["join_slope"]
        self.upkeep_base = payload["upkeep_base"]
        self.upkeep_slope = payload["upkeep_slope"]

    async def pull(self, pool: asyncpg.Pool) -> None:
        """Pulls the most recent gang info from the database.

        Parameters
        ----------
        pool : asyncpg.Pool
            The database pool.
        """
        async with pool.acquire() as conn:
            new_state: _types.Gang = await conn.fetchrow(  # type: ignore
                "SELECT * FROM gangs WHERE name = $1", self.name
            )
            for key, value in new_state.items():
                setattr(self, key, value)

    @classmethod
    async def fetch(cls, pool: asyncpg.Pool, name: str) -> Gang:
        """Fetches a gang from the database.

        Parameters
        ----------
        pool : asyncpg.Pool
            The database pool.
        name : str
            The name of the gang to fetch.

        Returns
        -------
        Gang
            The gang.

        Raises
        ------
        ValueError
            If a gang does not exist with the passed name.
        """
        async with pool.acquire() as conn:
            payload: _types.Gang = await conn.fetchrow("SELECT * FROM gangs WHERE name = $1", name)  # type: ignore
        if payload is None:
            raise ValueError("No gang found with that name.")
        return cls(payload)


class Territory:
    """Class representing a territory.

    Parameters
    ----------
    payload : _types.Territory
        The payload to construct from.
    """

    __slots__ = ("id", "name", "gang", "control", "benefit", "raid_end", "raider")

    def __init__(self, payload: _types.Territory):
        self.id = payload["id"]
        self.name = payload["name"]
        self.gang = payload["gang"]
        self.control = payload["control"]
        self.benefit = payload["benefit"]
        self.raid_end = payload["raid_end"]
        self.raider = payload["raider"]

    async def pull(self, pool: asyncpg.Pool) -> None:
        """Pulls the most recent territory info from the database.

        Parameters
        ----------
        pool : asyncpg.Pool
            The database pool.
        """
        async with pool.acquire() as conn:
            new_state: _types.Territory = await conn.fetchrow(  # type: ignore
                "SELECT * FROM territories WHERE id = $1", self.id
            )
            for key, value in new_state.items():
                setattr(self, key, value)

    @classmethod
    async def fetch(cls, pool: asyncpg.Pool, territory_id: int) -> Territory:
        """Fetches a territory from the database.

        Parameters
        ----------
        pool : asyncpg.Pool
            The database pool.
        territory_id : int
            The id of the territory to fetch.

        Returns
        -------
        Territory
            The territory.

        Raises
        ------
        ValueError
            If a territory does not exist with the passed id.
        """
        async with pool.acquire() as conn:
            payload: _types.Territory = await conn.fetchrow(  # type: ignore
                "SELECT * FROM territories WHERE id = $1", territory_id
            )
        if payload is None:
            raise ValueError("No territory found with that id.")
        return cls(payload)
