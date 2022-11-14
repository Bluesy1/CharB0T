# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import asyncpg
import pytest
from pytest_mock import MockerFixture

from charbot.gangs.actions import item_utils

pytestmark = pytest.mark.asyncio


@pytest.fixture
def connection(mocker: MockerFixture):
    """Return a mock connection."""
    return mocker.AsyncMock(spec=asyncpg.Connection)


@pytest.mark.parametrize(
    "val,expected",
    [
        (None, "Your gang is not defending against a raid, you cannot use defensive items at this time."),
        (
            {"id": 1, "defenders": [1], "defense": 3},
            "You are not participating in your gang's raid defense, you cannot use defensive items without"
            " joining a raid defense.",
        ),
        ({"id": 1, "defenders": [2], "defense": 3}, {"id": 1, "defenders": [2], "defense": 3}),
    ],
)
async def test_check_defensive_item(connection, val, expected):
    """Test check_defensive_item."""
    connection.fetchrow.return_value = val
    assert await item_utils.check_defensive_item(connection, 2) == expected


@pytest.mark.parametrize(
    "val,expected",
    [
        (None, "Your gang is not attacking another gang, you cannot use offensive items at this time."),
        (
            {"id": 1, "attackers": [1], "attack": 3},
            "You are not participating in your gang's raid, you cannot use offensive items without joining a raid.",
        ),
        ({"id": 1, "attackers": [2], "attack": 3}, {"id": 1, "attackers": [2], "attack": 3}),
    ],
)
async def test_check_offensive_item(connection, val, expected):
    """Test check_defensive_item."""
    connection.fetchrow.return_value = val
    assert await item_utils.check_offensive_item(connection, 2) == expected


@pytest.mark.parametrize(
    "val,err", [(None, "Must specify either user_id or gang."), ("a", "Cannot specify both user_id and gang.")]
)
async def test_consume_item_over_specified(connection, val, err):
    """Test check_gang_item."""
    with pytest.raises(TypeError, match=err) as exec_info:
        await item_utils.consume_item(connection, 1, 1, user=val, gang=val)
    assert exec_info.value.args[0] == err


async def test_consume_user_item_has_one(connection, mocker: MockerFixture):
    """Test check_gang_item."""
    execute = mocker.AsyncMock(spec=asyncpg.Connection.execute)
    connection.execute = execute
    await item_utils.consume_item(connection, 1, 1, user=1)
    execute.assert_awaited_once_with("DELETE FROM user_inventory WHERE user_id = $1 AND item = $2", 1, 1)


async def test_consume_user_item_has_multiple(connection, mocker: MockerFixture):
    """Test check_gang_item."""
    execute = mocker.AsyncMock(spec=asyncpg.Connection.execute)
    connection.execute = execute
    await item_utils.consume_item(connection, 1, 2, user=1)
    execute.assert_awaited_once_with(
        "UPDATE user_inventory SET quantity = quantity - 1 WHERE user_id = $1 AND item = $2", 1, 1
    )


async def test_consume_gang_item_has_one(connection, mocker: MockerFixture):
    """Test check_gang_item."""
    execute = mocker.AsyncMock(spec=asyncpg.Connection.execute)
    connection.execute = execute
    await item_utils.consume_item(connection, 1, 1, gang="White")
    execute.assert_awaited_once_with("DELETE FROM gang_inventory WHERE gang = $1 AND item = $2", "White", 1)


async def test_consume_gang_item_has_multiple(connection, mocker: MockerFixture):
    """Test check_gang_item."""
    execute = mocker.AsyncMock(spec=asyncpg.Connection.execute)
    connection.execute = execute
    await item_utils.consume_item(connection, 1, 2, gang="White")
    execute.assert_awaited_once_with(
        "UPDATE gang_inventory SET quantity = quantity - 1 WHERE gang = $1 AND item = $2", "White", 1
    )
