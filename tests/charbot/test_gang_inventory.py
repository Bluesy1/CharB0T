# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.nocontrolly.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import asyncpg
import discord
import pytest
import pytest_asyncio
from pytest_mock import MockerFixture

from charbot import CBot
from charbot.gangs.actions import gang_items
from charbot.gangs import enums

# noinspection DuplicatedCode
pytestmark = pytest.mark.asyncio


@pytest.fixture
def interaction(mocker: MockerFixture, database: asyncpg.Pool) -> discord.Interaction[CBot]:
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
        "upkeep_slope, all_paid) VALUES ('White', 0, 1, 1, 1, 1, 1, 1, 1, 1, FALSE) ON CONFLICT (name)"
        "DO UPDATE SET leader = 1, role = 1, channel = 1, control = 1, join_base = 1, join_slope = 1, "
        "upkeep_base = 1, upkeep_slope = 1, all_paid = FALSE"
    )
    await database.execute("INSERT INTO gang_members (user_id, gang) VALUES (1, 'White')")
    await database.execute(
        "INSERT INTO territories (id, name, gang, benefit, raider) VALUES (1, 'test', 'White', 'none', 'White')"
    )
    yield
    await database.execute("DELETE FROM gangs WHERE name = 'White'")
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    await database.execute("DELETE FROM territories WHERE gang = 'White'")


@pytest.mark.parametrize("in_gang", [True, False])
async def test_buy_item_autocomplete_no_items(interaction, in_gang) -> None:
    """Test the buy item autocomplete."""
    if not in_gang:
        await interaction.client.pool.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert await gang_items.view_items_autocomplete(interaction, "") == []


async def test_buy_item_autocomplete_with_items(interaction, database: asyncpg.Pool):
    """Test the buy item autocomplete."""
    await database.execute(
        "INSERT INTO gang_items (name, benefit, value, cost) VALUES ('test', $1, 1, 1)", enums.Benefits.other
    )
    res = await gang_items.view_items_autocomplete(interaction, "")
    await database.execute("DELETE FROM gang_items WHERE name = 'test'")
    await database.execute("DELETE FROM gangs WHERE name = 'White'")
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert res == [discord.app_commands.Choice(name="test - Cost: 1", value="test")]


async def test_try_buy_item_not_gang_leadership(database: asyncpg.Pool):
    """Test buying an item when not in a gang."""
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert (
        await gang_items.try_buy_item(database, 1, "test")
        == "You are not in the leadership of a gang, you cannot buy gang items."
    )


async def test_try_buy_item_nonexistent(database: asyncpg.Pool):
    """Test buying a nonexistent item."""
    assert await gang_items.try_buy_item(database, 1, "test") == "The item `test` you requested doesn't exist."


async def test_try_buy_item_not_enough_points(database: asyncpg.Pool):
    """Test buying an item with not enough points."""
    await database.execute("INSERT INTO users (id, points) VALUES (1, 0) ON CONFLICT (id) DO UPDATE SET points = 0")
    await database.execute(
        "INSERT INTO gang_items (name, benefit, value, cost) VALUES ('test', $1, 2, 2)", enums.Benefits.other
    )
    res = await gang_items.try_buy_item(database, 1, "test")
    await database.execute("DELETE FROM gang_items WHERE name = 'test'")
    await database.execute("DELETE FROM users WHERE id = 1")
    assert res == "Your gang doesn't have enough control to buy that. (Have: 1, Need: 2)"


async def test_try_buy_item_success(database: asyncpg.Pool):
    """Test buying an item with enough points."""
    await database.execute("INSERT INTO users (id, points) VALUES (1, 10) ON CONFLICT (id) DO UPDATE SET points = 10")
    await database.execute(
        "INSERT INTO gang_items (name, benefit, value, cost) VALUES ('test', $1, 1, 1)", enums.Benefits.other
    )
    res = await gang_items.try_buy_item(database, 1, "test")
    await database.execute("DELETE FROM gang_items WHERE name = 'test'")
    await database.execute("DELETE FROM users WHERE id = 1")
    assert res == 0


async def test_try_display_inventory_not_leadership(database: asyncpg.Pool):
    """Test displaying the inventory when not in a gang."""
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert (
        await gang_items.try_display_inventory(database, 1)
        == "You are not in the leadership of a gang, you cannot view your gang's inventory."
    )


async def test_try_display_inventory_empty(database: asyncpg.Pool):
    """Test displaying the inventory when it is empty."""
    assert await gang_items.try_display_inventory(database, 1) == "Your gang doesn't have any items."


async def test_try_display_inventory_success(database: asyncpg.Pool):
    """Test displaying the inventory when it is not empty."""
    item_id: int = await database.fetchval(
        "INSERT INTO gang_items (name, benefit, value, cost) VALUES ('test', $1, 1, 1) RETURNING id",
        enums.Benefits.other,
    )
    await database.execute("INSERT INTO gang_inventory (gang, item, quantity) VALUES ('White', $1, 1)", item_id)
    res = await gang_items.try_display_inventory(database, 1)
    await database.execute("DELETE FROM gang_items WHERE name = 'test'")
    await database.execute("DELETE FROM gang_inventory WHERE gang = 'White'")
    assert isinstance(res, gang_items.ItemsView)


async def test_try_display_available_items_not_leadership(database: asyncpg.Pool):
    """Test displaying the available items when not in a gang."""
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert (
        await gang_items.try_display_available_items(database, 1)
        == "You are not in the leadership of a gang, you cannot view the available items."
    )


async def test_try_display_available_items_empty(database: asyncpg.Pool):
    """Test displaying the available items when it is empty."""
    assert await gang_items.try_display_available_items(database, 1) == "There are no items available."


async def test_try_display_available_items_success(database: asyncpg.Pool):
    """Test displaying the available items when it is not empty."""
    await database.execute(
        "INSERT INTO gang_items (name, benefit, value, cost) VALUES ('test', $1, 1, 1)", enums.Benefits.other
    )
    res = await gang_items.try_display_available_items(database, 1)
    await database.execute("DELETE FROM gang_items WHERE name = 'test'")
    assert isinstance(res, gang_items.ItemsView)


async def test_try_display_item_not_leadership(database: asyncpg.Pool):
    """Test displaying an item when not in a gang."""
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert (
        await gang_items.try_display_item(database, 1, "test")
        == "You are not in the leadership of a gang, you cannot view gang items."
    )


async def test_try_display_item_nonexistent(database: asyncpg.Pool):
    """Test displaying a nonexistent item."""
    assert await gang_items.try_display_item(database, 1, "test") == "The item `test` does not exist."


async def test_try_display_item_success(database: asyncpg.Pool):
    """Test displaying an item."""
    await database.execute(
        "INSERT INTO gang_items (name, benefit, value, cost) VALUES ('test', $1, 1, 1)", enums.Benefits.other
    )
    res = await gang_items.try_display_item(database, 1, "test")
    await database.execute("DELETE FROM gang_items WHERE name = 'test'")
    assert res == "**test**\n\nCost: 1\nOwned: 0"


async def test_try_display_item_has_one(database: asyncpg.Pool):
    """Test displaying an item when it has none."""
    item_id: int = await database.fetchval(
        "INSERT INTO gang_items (name, benefit, value, cost) VALUES ('test', $1, 1, 1) RETURNING id",
        enums.Benefits.other,
    )
    await database.execute("INSERT INTO gang_inventory (gang, item, quantity) VALUES ('White', $1, 1)", item_id)
    res = await gang_items.try_display_item(database, 1, "test")
    await database.execute("DELETE FROM gang_items WHERE name = 'test'")
    await database.execute("DELETE FROM gang_inventory WHERE gang = 'White'")
    assert res == "**test**\n\nCost: 1\nOwned: 1"


async def test_try_sell_item_not_leadership(database: asyncpg.Pool):
    """Test selling an item when not in a gang."""
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    assert (
        await gang_items.try_sell_item(database, 1, "test")
        == "You are not in the leadership of a gang, you cannot sell gang items."
    )


async def test_try_sell_item_nonexistent(database: asyncpg.Pool):
    """Test selling a nonexistent item."""
    assert (
        await gang_items.try_sell_item(database, 1, "test")
        == "Your gang doesn't have any `test` to sell, or it doesn't exist."
    )


async def test_try_sell_item_has_one(database: asyncpg.Pool):
    """Test selling an item when it has one."""
    item_id: int = await database.fetchval(
        "INSERT INTO gang_items (name, benefit, value, cost) VALUES ('test', $1, 10, 10) RETURNING id",
        enums.Benefits.other,
    )
    await database.execute("INSERT INTO gang_inventory (gang, item, quantity) VALUES ('White', $1, 1)", item_id)
    res = await gang_items.try_sell_item(database, 1, "test")
    await database.execute("DELETE FROM gang_items WHERE name = 'test'")
    await database.execute("DELETE FROM gang_inventory WHERE gang = 'White'")
    assert res == 2


async def test_try_sell_item_has_multiple(database: asyncpg.Pool):
    """Test selling an item when it has multiple."""
    item_id: int = await database.fetchval(
        "INSERT INTO gang_items (name, benefit, value, cost) VALUES ('test', $1, 10, 10)RETURNING id",
        enums.Benefits.other,
    )
    await database.execute("INSERT INTO gang_inventory (gang, item, quantity) VALUES ('White', $1, 5)", item_id)
    res = await gang_items.try_sell_item(database, 1, "test")
    await database.execute("DELETE FROM gang_items WHERE name = 'test'")
    await database.execute("DELETE FROM gang_inventory WHERE gang = 'White'")
    assert res == 2


async def test_use_defensive_item_unable(database, mocker: MockerFixture, monkeypatch):
    """Test trying to use a defensive item without enough control"""
    monkeypatch.setattr(
        gang_items.utils,
        "check_defensive_item",
        mocker.AsyncMock(return_value="Fail"),
    )
    async with database.acquire() as conn:
        assert (
            await gang_items.use_defensive_item(
                conn,
                {"id": 1, "name": "name", "quantity": 1, "value": 1, "cost": 1, "benefit": enums.Benefits.defense},
                1,
                True,
            )
            == "Fail"
        )


async def test_use_defensive_item_reusable_too_little_control(database, mocker: MockerFixture, monkeypatch):
    """Test trying to use a defensive item without enough control"""
    monkeypatch.setattr(
        gang_items.utils,
        "check_defensive_item",
        mocker.AsyncMock(return_value={"id": 1, "defenders": [1], "defense": 3}),
    )
    async with database.acquire() as conn:
        assert (
            await gang_items.use_defensive_item(
                conn,
                {"id": 1, "name": "name", "quantity": 1, "value": 1, "cost": 11, "benefit": enums.Benefits.defense},
                1,
                True,
            )
            == "You do not have enough control to use `name`. You need 11 control, and have 1."
        )


async def test_use_defensive_item_reusable_success(database, mocker: MockerFixture, monkeypatch):
    """Test trying to use a defensive item successfully"""
    monkeypatch.setattr(
        gang_items.utils,
        "check_defensive_item",
        mocker.AsyncMock(return_value={"id": 1, "defenders": [1], "defense": 3}),
    )
    async with database.acquire() as conn:
        res = await gang_items.use_defensive_item(
            conn,
            {"id": 1, "name": "name", "quantity": 1, "value": 1, "cost": 1, "benefit": enums.Benefits.defense},
            1,
            True,
        )
        defense = await conn.fetchval("SELECT defense FROM territories WHERE gang = 'White' AND raider = 'White'")
    assert defense == 1
    assert res == "You used `name` and gained 1 defense. Your gang now has 4 defense. You now have 0 control."


async def test_use_defensive_item_consumable_success(database, mocker: MockerFixture, monkeypatch):
    """Test trying to use a defensive item successfully"""
    monkeypatch.setattr(
        gang_items.utils,
        "check_defensive_item",
        mocker.AsyncMock(return_value={"id": 1, "defenders": [1], "defense": 3}),
    )
    monkeypatch.setattr(gang_items.utils, "consume_item", mocker.AsyncMock())
    async with database.acquire() as conn:
        res = await gang_items.use_defensive_item(
            conn,
            {"id": 1, "name": "name", "quantity": 1, "value": 1, "cost": 1, "benefit": enums.Benefits.defense},
            1,
            False,
        )
        defense = await conn.fetchval("SELECT defense FROM territories WHERE gang = 'White' AND raider = 'White'")
    assert defense == 1
    assert res == "You used `name` and gained 1 defense. Your gang now has 4 defense."


async def test_use_offensive_item_unable(database, mocker: MockerFixture, monkeypatch):
    """Test trying to use an offensive item without enough control"""
    monkeypatch.setattr(
        gang_items.utils,
        "check_offensive_item",
        mocker.AsyncMock(return_value="Fail"),
    )
    async with database.acquire() as conn:
        assert (
            await gang_items.use_offensive_item(
                conn,
                {"id": 1, "name": "name", "quantity": 1, "value": 1, "cost": 1, "benefit": enums.Benefits.offense},
                1,
                True,
            )
            == "Fail"
        )


async def test_use_offensive_item_reusable_too_little_control(database, mocker: MockerFixture, monkeypatch):
    """Test trying to use an offensive item without enough control"""
    monkeypatch.setattr(
        gang_items.utils,
        "check_offensive_item",
        mocker.AsyncMock(return_value={"id": 1, "attackers": [1], "attack": 3}),
    )
    async with database.acquire() as conn:
        assert (
            await gang_items.use_offensive_item(
                conn,
                {"id": 1, "name": "name", "quantity": 1, "value": 1, "cost": 11, "benefit": enums.Benefits.offense},
                1,
                True,
            )
            == "You do not have enough control to use `name`. You need 11 control, and have 1."
        )


async def test_use_offensive_item_reusable_success(database, mocker: MockerFixture, monkeypatch):
    """Test trying to use an offensive item successfully"""
    monkeypatch.setattr(
        gang_items.utils,
        "check_offensive_item",
        mocker.AsyncMock(return_value={"id": 1, "attackers": [1], "attack": 3}),
    )
    async with database.acquire() as conn:
        res = await gang_items.use_offensive_item(
            conn,
            {"id": 1, "name": "name", "quantity": 1, "value": 1, "cost": 1, "benefit": enums.Benefits.offense},
            1,
            True,
        )
        attack = await conn.fetchval("SELECT attack FROM territories WHERE gang = 'White' AND raider = 'White'")
    assert attack == 1
    assert res == "You used `name` and gained 1 attack. Your gang now has 4 attack. You now have 0 control."


async def test_use_offensive_item_consumable_success(database, mocker: MockerFixture, monkeypatch):
    """Test trying to use an offensive item successfully"""
    monkeypatch.setattr(
        gang_items.utils,
        "check_offensive_item",
        mocker.AsyncMock(return_value={"id": 1, "attackers": [1], "attack": 3}),
    )
    monkeypatch.setattr(gang_items.utils, "consume_item", mocker.AsyncMock())
    async with database.acquire() as conn:
        res = await gang_items.use_offensive_item(
            conn,
            {"id": 1, "name": "name", "quantity": 1, "value": 1, "cost": 1, "benefit": enums.Benefits.offense},
            1,
            False,
        )
        attack = await conn.fetchval("SELECT attack FROM territories WHERE gang = 'White' AND raider = 'White'")
    assert attack == 1
    assert res == "You used `name` and gained 1 attack. Your gang now has 4 attack."


@pytest.mark.parametrize(
    "benefit,expected",
    [
        (enums.Benefits.currency, "Currency items are not implemented for gangs yet"),
        (enums.Benefits.currency_consumable, "Currency items are not implemented for gangs yet"),
        (enums.Benefits.defense, "Defense"),
        (enums.Benefits.defense_consumable, "Defense"),
        (enums.Benefits.offense, "Offense"),
        (enums.Benefits.offense_consumable, "Offense"),
        (enums.Benefits.other, "You cannot use `name`. It is not a usable item."),
    ],
)
async def test_try_use_item(mocker: MockerFixture, monkeypatch, database: asyncpg.Pool, benefit, expected):
    """Test trying to use an item"""
    item_id = await database.fetchval(
        "INSERT INTO gang_items (name, value, cost, benefit) VALUES ('name', 1, 1, $1) RETURNING id", benefit
    )
    await database.execute("INSERT INTO gang_inventory (gang, item, quantity) VALUES ('White', $1, 1)", item_id)
    monkeypatch.setattr(gang_items, "use_defensive_item", mocker.AsyncMock(return_value="Defense"))
    monkeypatch.setattr(gang_items, "use_offensive_item", mocker.AsyncMock(return_value="Offense"))
    ret = await gang_items.try_use_item(database, 1, "name")
    await database.execute("DELETE FROM gang_items WHERE id = $1", item_id)
    await database.execute("DELETE FROM gang_inventory WHERE gang = 'White'")
    assert ret == expected