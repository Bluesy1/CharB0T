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

# noinspection DuplicatedCode
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
    await database.execute("INSERT INTO users (id, points) VALUES (1, 10) ON CONFLICT(id) DO UPDATE SET points = 10")
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


async def test_try_display_inventory_not_in_gang(database: asyncpg.Pool):
    """Test displaying an inventory when not in a gang."""
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert await user_items.try_display_inventory(database, 1) == "You don't have any items."


async def test_try_display_inventory_has_one_item(database: asyncpg.Pool):
    """Test displaying an inventory with one item."""
    item_id: int = await database.fetchval(
        "INSERT INTO user_items (name, benefit, value) VALUES ('test', $1, 1) RETURNING id", enums.Benefits.other
    )
    await database.execute("INSERT INTO user_inventory (user_id, item, quantity) VALUES (1, $1, 1)", item_id)
    res = await user_items.try_display_inventory(database, 1)
    await database.execute("DELETE FROM user_items WHERE name = 'test'")
    await database.execute("DELETE FROM user_inventory WHERE user_id = 1")
    assert isinstance(res, user_items.ItemsView)


async def test_try_display_available_items_not_in_gang(database: asyncpg.Pool):
    """Test displaying available items when not in a gang."""
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert await user_items.try_display_available_items(database, 1) == "You must be in a gang to have items."


async def test_try_display_available_items_none_available(database: asyncpg.Pool):
    """Test displaying available items when none are available."""
    assert await user_items.try_display_available_items(database, 1) == "There are no items available."


async def test_try_display_available_items_one_available(database: asyncpg.Pool):
    """Test displaying available items when one is available."""
    await database.execute("INSERT INTO user_items (name, benefit, value) VALUES ('test', $1, 1)", enums.Benefits.other)
    res = await user_items.try_display_available_items(database, 1)
    await database.execute("DELETE FROM user_items WHERE name = 'test'")
    assert isinstance(res, user_items.ItemsView)


async def test_try_display_item_not_in_gang(database: asyncpg.Pool):
    """Test displaying an item when not in a gang."""
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert await user_items.try_display_item(database, 1, "test") == "You must be in a gang to have items."


async def test_try_display_item_nonexistent(database: asyncpg.Pool):
    """Test displaying a nonexistent item."""
    assert await user_items.try_display_item(database, 1, "test") == "The item `test` does not exist."


async def test_try_display_item_has_one(database: asyncpg.Pool):
    """Test displaying an item when you have one."""
    item_id: int = await database.fetchval(
        "INSERT INTO user_items (name, benefit, value) VALUES ('test', $1, 1) RETURNING id", enums.Benefits.other
    )
    await database.execute("INSERT INTO user_inventory (user_id, item, quantity) VALUES (1, $1, 1)", item_id)
    res = await user_items.try_display_item(database, 1, "test")
    await database.execute("DELETE FROM user_items WHERE name = 'test'")
    await database.execute("DELETE FROM user_inventory WHERE user_id = 1")
    assert res == "**test**\n\nValue: 1\nOwned: 1"


async def test_try_display_item_has_none(database: asyncpg.Pool):
    """Test displaying an item when you have none."""
    await database.execute("INSERT INTO user_items (name, benefit, value) VALUES ('test', $1, 1)", enums.Benefits.other)
    res = await user_items.try_display_item(database, 1, "test")
    await database.execute("DELETE FROM user_items WHERE name = 'test'")
    assert res == "**test**\n\nValue: 1\nOwned: 0"


async def test_try_sell_item_has_none(database: asyncpg.Pool):
    """Test selling an item when you have none."""
    await database.execute("INSERT INTO user_items (name, benefit, value) VALUES ('test', $1, 1)", enums.Benefits.other)
    res = await user_items.try_sell_item(database, 1, "test")
    await database.execute("DELETE FROM user_items WHERE name = 'test'")
    assert res == "You don't have any `test` to sell, or it doesn't exist."


async def test_try_sell_item_has_one(database: asyncpg.Pool):
    """Test selling an item when you have one."""
    item_id: int = await database.fetchval(
        "INSERT INTO user_items (name, benefit, value) VALUES ('test', $1, 10) RETURNING id", enums.Benefits.other
    )
    await database.execute("INSERT INTO user_inventory (user_id, item, quantity) VALUES (1, $1, 1)", item_id)
    res = await user_items.try_sell_item(database, 1, "test")
    await database.execute("DELETE FROM user_items WHERE name = 'test'")
    await database.execute("DELETE FROM user_inventory WHERE user_id = 1")
    assert res == 11


async def test_try_sell_item_has_multiple(database: asyncpg.Pool):
    """Test selling an item when you have multiple."""
    item_id: int = await database.fetchval(
        "INSERT INTO user_items (name, benefit, value) VALUES ('test', $1, 10) RETURNING id", enums.Benefits.other
    )
    await database.execute("INSERT INTO user_inventory (user_id, item, quantity) VALUES (1, $1, 2)", item_id)
    res = await user_items.try_sell_item(database, 1, "test")
    await database.execute("DELETE FROM user_items WHERE name = 'test'")
    await database.execute("DELETE FROM user_inventory WHERE user_id = 1")
    assert res == 11


async def test_try_gift_item_not_leadership(database: asyncpg.Pool):
    """Test gifting an item when you're not leadership."""
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert (
        await user_items.try_gift_item(database, 1, "test", 2)
        == "You are not in the leadership of a gang, you cannot gift items."
    )


async def test_try_gift_item_nonexistent(database: asyncpg.Pool):
    """Test gifting a nonexistent item."""
    assert (
        await user_items.try_gift_item(database, 1, "test", 2)
        == "You don't have any `test` to gift, or it doesn't exist."
    )


async def test_try_gift_item_has_one(database: asyncpg.Pool):
    """Test gifting an item when you have one."""
    await database.execute("INSERT INTO users (id, points) VALUES (2, 1)")
    item_id: int = await database.fetchval(
        "INSERT INTO user_items (name, benefit, value) VALUES ('test', $1, 10) RETURNING id", enums.Benefits.other
    )
    await database.execute("INSERT INTO user_inventory (user_id, item, quantity) VALUES (1, $1, 1)", item_id)
    res = await user_items.try_gift_item(database, 1, "test", 2)
    await database.execute("DELETE FROM user_items WHERE name = 'test'")
    await database.execute("DELETE FROM user_inventory WHERE user_id = 1;DELETE FROM user_inventory WHERE user_id = 1")
    await database.execute("DELETE FROM users WHERE id = 2")
    assert res == "You gifted `test` to <@2>."


async def test_try_gift_item_has_multiple(database: asyncpg.Pool):
    """Test gifting an item when you have multiple."""
    await database.execute("INSERT INTO users (id, points) VALUES (2, 1)")
    item_id: int = await database.fetchval(
        "INSERT INTO user_items (name, benefit, value) VALUES ('test', $1, 10) RETURNING id", enums.Benefits.other
    )
    await database.execute("INSERT INTO user_inventory (user_id, item, quantity) VALUES (1, $1, 2)", item_id)
    res = await user_items.try_gift_item(database, 1, "test", 2)
    await database.execute("DELETE FROM user_items WHERE name = 'test'")
    await database.execute("DELETE FROM user_inventory WHERE user_id = 1;DELETE FROM user_inventory WHERE user_id = 1")
    await database.execute("DELETE FROM users WHERE id = 2")
    assert res == "You gifted `test` to <@2>."
