# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import asyncpg
import pytest

from charbot.gangs.actions import raid
from charbot.gangs.types import Gang, Territory


@pytest.mark.asyncio
async def test_try_start_raid_not_enough_control(database: asyncpg.Pool):
    """Test that a gang can't start a raid if they don't have enough control"""
    gang: Gang = {"control": 1}  # type: ignore
    territory: Territory = {}  # type: ignore
    assert await raid.try_start_raid(gang, territory, database) is False


@pytest.mark.asyncio
async def test_try_start_raid_territory_already_raided(database: asyncpg.Pool):
    """Test that a gang can't start a raid if the territory is already being raided"""
    gang: Gang = {"control": 2000}  # type: ignore
    territory: Territory = {"raider": "Anything"}  # type: ignore
    assert await raid.try_start_raid(gang, territory, database) is False


@pytest.mark.asyncio
async def test_try_start_raid_gang_already_raiding(database: asyncpg.Pool):
    """Test that a gang can't start a raid if they are already raiding a territory"""
    gang: Gang = {"control": 2000, "name": "White"}  # type: ignore
    territory: Territory = {"raider": None}  # type: ignore
    await database.execute(
        "INSERT INTO gangs (name, color, leader, role, channel, control, join_base, join_slope, upkeep_base, "
        "upkeep_slope, all_paid) VALUES ('White', $1, 1, 1, 1, 1, 1, 1, 1, 1, FALSE) ON CONFLICT DO NOTHING",
        0x3498DB,
    )
    await database.execute(
        "INSERT INTO territories (name, gang, raider, benefit) VALUES ('name', 'White', 'White', 'none')"
    )
    assert await raid.try_start_raid(gang, territory, database) is False
    await database.execute("DELETE FROM gangs WHERE name = 'White'; DELETE FROM territories WHERE name = 'name'")


@pytest.mark.asyncio
async def test_try_start_raid_gang_success(database: asyncpg.Pool):
    """Test that a gang can start a raid if they have enough control and the territory isn't being raided"""
    gang: Gang = {"control": 2000, "name": "White"}  # type: ignore
    territory: Territory = {"raider": None, "id": 50}  # type: ignore
    async with database.acquire() as conn:
        await conn.execute(
            "INSERT INTO gangs (name, color, leader, role, channel, control, join_base, join_slope, upkeep_base, "
            "upkeep_slope, all_paid) VALUES ('White', $1, 1, 1, 1, 2000, 1, 1, 1, 1, FALSE) ON CONFLICT DO NOTHING",
            0x3498DB,
        )
        await conn.execute(
            "INSERT INTO territories (id, name, gang, raider, benefit) VALUES " "(50, 'name', 'White', NULL, 'none')"
        )
    assert await raid.try_start_raid(gang, territory, database) is True
    assert await database.fetchval("SELECT control FROM gangs WHERE name = 'White'") == 1000
    assert await database.fetchval("SELECT raider FROM territories WHERE id = 50") == "White"
    await database.execute("DELETE FROM gangs WHERE name = 'White'; DELETE FROM territories WHERE id = 50")


@pytest.mark.asyncio
async def test_end_raid_attackers_win(database: asyncpg.Pool):
    """Test that a raid ends with the attackers winning"""
    territory: Territory = {  # type: ignore
        "id": 5,
        "raider": "White",
        "gang": "White",
        "defense": 1,
        "attack": 2,
        "name": "test",
    }
    assert (
        await raid.end_raid(database, territory) == "White has successfully raided test and taken it over from White!"
    )


@pytest.mark.asyncio
async def test_end_raid_attackers_lose(database: asyncpg.Pool):
    """Test that a raid ends with the attackers winning"""
    territory: Territory = {  # type: ignore
        "id": 5,
        "raider": "White",
        "gang": "White",
        "defense": 2,
        "attack": 1,
        "name": "test",
    }
    assert await raid.end_raid(database, territory) == "White has successfully defended test from White!"
