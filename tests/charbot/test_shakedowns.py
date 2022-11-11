# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import asyncpg
import pytest

from charbot.gangs import shakedowns, enums

pytestmark = pytest.mark.asyncio


async def test_shakedown_chance_no_items(database: asyncpg.Pool):
    """Test that the shakedown chance is 0 if the gang has no items"""
    assert await shakedowns.shakedown_chance(database) == 0


async def test_shakedown_chance_one_item(database: asyncpg.Pool):
    """Test that the shakedown chance is 0.01 if the gang has one item"""
    await database.execute(
        "INSERT INTO gangs (name, color, leader, role, channel, control, join_base, join_slope, upkeep_base, "
        "upkeep_slope, all_paid) VALUES ('White', $1, 1, 1, 1, 2000, 1, 1, 1, 1, FALSE) ON CONFLICT DO NOTHING",
        0x3498DB,
    )
    res: int = await database.fetchval(
        "INSERT INTO gang_items (name, benefit, value) VALUES ('test', $1, 1) RETURNING id", enums.Benefits.other
    )
    await database.execute(
        "INSERT INTO gang_inventory (gang, item, quantity) VALUES ('White', $1, 1) ON CONFLICT DO NOTHING", res
    )
    assert round(await shakedowns.shakedown_chance(database), 2) == 0.01
    # noinspection SqlWithoutWhere
    await database.execute("DELETE FROM gangs WHERE name = 'White'; DELETE FROM gang_items; DELETE FROM gang_inventory")


async def test_shakedown_chance_multiple_quantity(database: asyncpg.Pool):
    """Test that the shakedown chance is 0.05 if the gang has 5 of one item"""
    await database.execute(
        "INSERT INTO gangs (name, color, leader, role, channel, control, join_base, join_slope, upkeep_base, "
        "upkeep_slope, all_paid) VALUES ('White', $1, 1, 1, 1, 2000, 1, 1, 1, 1, FALSE) ON CONFLICT DO NOTHING",
        0x3498DB,
    )
    res: int = await database.fetchval(
        "INSERT INTO gang_items (name, benefit, value) VALUES ('test', $1, 1) RETURNING id", enums.Benefits.other
    )
    await database.execute(
        "INSERT INTO gang_inventory (gang, item, quantity) VALUES ('White', $1, 5) ON CONFLICT DO NOTHING", res
    )
    assert round(await shakedowns.shakedown_chance(database), 2) == 0.05
    # noinspection SqlWithoutWhere
    await database.execute("DELETE FROM gangs WHERE name = 'White'; DELETE FROM gang_items; DELETE FROM gang_inventory")


async def test_do_shakedown_immediate_exit(database: asyncpg.Pool):
    """Test that the shakedown exits immediately if the chance is 0"""
    assert await shakedowns.do_shakedown(database) == 0
