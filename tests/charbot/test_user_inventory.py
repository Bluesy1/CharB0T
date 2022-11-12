# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import asyncpg
import discord
import pytest
import pytest_asyncio
from pytest_mock import MockerFixture

from charbot import CBot, GuildInteraction
from charbot.gangs.actions import user_items
from charbot.gangs import enums

pytestmark = pytest.mark.asyncio


@pytest.fixture
def interaction(mocker: MockerFixture, database: asyncpg.Pool) -> GuildInteraction[CBot]:
    """Mock interaction."""
    inter = mocker.AsyncMock(
        spec=discord.Interaction,
        client=mocker.AsyncMock(spec=CBot, pool=database),
    )
    inter.user.id = 1
    return inter


@pytest_asyncio.fixture(autouse=True)
async def setup_gang(database: asyncpg.Pool):
    """Set up a gang and member for the tests."""
    await database.execute("INSERT INTO users (id, points) VALUES (1, 10) ON CONFLICT DO NOTHING")
    await database.execute(
        "INSERT INTO gangs (name, color, leader, role, channel, control, join_base, join_slope, upkeep_base, "
        "upkeep_slope, all_paid) VALUES ('White', 0, 1, 1, 1, 1, 1, 1, 1, 1, FALSE) ON CONFLICT DO NOTHING",
    )
    await database.execute("INSERT INTO gang_members (user_id, gang) VALUES (1, 'White')")
    yield
    await database.execute("DELETE FROM gangs WHERE name = 'White'")
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")


@pytest.mark.parametrize("in_gang", [True, False])
async def test_buy_item_autocomplete_no_items(interaction, in_gang) -> None:
    """Test the buy item autocomplete."""
    if not in_gang:
        await interaction.client.pool.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert await user_items.view_available_items_autocomplete(interaction, "") == []


async def test_buy_item_autocomplete_with_items(interaction, database: asyncpg.Pool):
    """Test the buy item autocomplete."""
    await database.execute("INSERT INTO user_items (name, benefit, value) VALUES ('test', $1, 1)", enums.Benefits.other)
    res = await user_items.view_available_items_autocomplete(interaction, "")
    await database.execute("DELETE FROM user_items WHERE name = 'test'")
    await database.execute("DELETE FROM gangs WHERE name = 'White'")
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert res == [discord.app_commands.Choice(name="test - Cost: 1", value="test")]


@pytest.mark.parametrize("in_gang", [True, False])
async def test_view_item_autocomplete_no_items(interaction, in_gang) -> None:
    """Test the view item autocomplete."""
    if not in_gang:
        await interaction.client.pool.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert await user_items.view_item_autocomplete(interaction, "") == []


async def test_view_item_autocomplete_with_items(interaction, database: asyncpg.Pool):
    """Test the view item autocomplete."""
    item_id: int = await database.fetchval(
        "INSERT INTO user_items (name, benefit, value) VALUES ('test', $1, 1) RETURNING id", enums.Benefits.other
    )
    await database.execute("INSERT INTO user_inventory (user_id, item, quantity) VALUES (1, $1, 1)", item_id)
    res = await user_items.view_item_autocomplete(interaction, "")
    await database.execute("DELETE FROM user_items WHERE name = 'test'")
    await database.execute("DELETE FROM gangs WHERE name = 'White'")
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    await database.execute("DELETE FROM user_inventory WHERE user_id = 1")
    assert res == [discord.app_commands.Choice(name="test", value="test")]


async def test_try_buy_item_not_in_gang(database: asyncpg.Pool):
    """Test buying an item when not in a gang."""
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert await user_items.try_buy_item(database, 1, "test") == "You must be in a gang to buy items."


async def test_try_buy_item_nonexistent(database: asyncpg.Pool):
    """Test buying a nonexistent item."""
    assert await user_items.try_buy_item(database, 1, "test") == "The item `test` you requested doesn't exist."


async def test_try_buy_item_not_enough_points(database: asyncpg.Pool):
    """Test buying an item with not enough points."""
    await database.execute("INSERT INTO users (id, points) VALUES (1, 0) ON CONFLICT (id) DO UPDATE SET points = 0")
    await database.execute("INSERT INTO user_items (name, benefit, value) VALUES ('test', $1, 1)", enums.Benefits.other)
    res = await user_items.try_buy_item(database, 1, "test")
    await database.execute("DELETE FROM user_items WHERE name = 'test'")
    await database.execute("DELETE FROM users WHERE id = 1")
    assert res == "You don't have enough rep to buy that. (Have: 0, Need: 1)"


async def test_try_buy_item_success(database: asyncpg.Pool):
    """Test buying an item with enough points."""
    await database.execute("INSERT INTO users (id, points) VALUES (1, 10) ON CONFLICT (id) DO UPDATE SET points = 10")
    await database.execute("INSERT INTO user_items (name, benefit, value) VALUES ('test', $1, 1)", enums.Benefits.other)
    res = await user_items.try_buy_item(database, 1, "test")
    await database.execute("DELETE FROM user_items WHERE name = 'test'")
    await database.execute("DELETE FROM users WHERE id = 1")
    assert res == 9
