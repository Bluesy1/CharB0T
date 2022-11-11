# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import discord
import pytest
from pytest_mock import MockerFixture

from charbot import CBot, gangs


@pytest.mark.asyncio
async def test_dues_button_paid(mocker: MockerFixture, database):
    """Test the dues button for an  already paid member."""
    interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        response=mocker.AsyncMock(spec=discord.InteractionResponse),
        followup=mocker.AsyncMock(spec=discord.Webhook),
        client=mocker.AsyncMock(spec=CBot, pool=database),
    )
    interaction.user.id = 1
    await database.execute("INSERT INTO users (id, points) VALUES (001, 50) ON CONFLICT (id) DO UPDATE SET points = 50")
    await database.execute(
        "INSERT INTO gangs (name, color, leader, role, channel, control, join_base, join_slope, upkeep_base, "
        "upkeep_slope, all_paid) VALUES ('White', $1, 1, 1, 1, 1, 1, 1, 1, 1, FALSE) ON CONFLICT DO NOTHING",
        0x3498DB,
    )
    await database.execute("INSERT INTO gang_members (user_id, gang, paid) VALUES (001, 'White', TRUE)")
    button = gangs.DuesButton("White")
    await button.callback(interaction)
    interaction.response.defer.assert_awaited_once()
    assert interaction.response.defer.await_args.kwargs["ephemeral"] is True, "Ephemeral should be true"
    interaction.followup.send.assert_awaited_once_with("You have already paid your dues for this month.")
    # noinspection SqlWithoutWhere
    await database.execute("DELETE FROM gang_members; DELETE FROM gangs; DELETE FROM users")


@pytest.mark.asyncio
async def test_dues_button_not_enough_points(mocker: MockerFixture, database):
    """Test the dues button for a member without enough points."""
    interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        response=mocker.AsyncMock(spec=discord.InteractionResponse),
        followup=mocker.AsyncMock(spec=discord.Webhook),
        client=mocker.AsyncMock(spec=CBot, pool=database),
    )
    interaction.user.id = 1
    await database.execute("INSERT INTO users (id, points) VALUES (001, 50) ON CONFLICT (id) DO UPDATE SET points = 50")
    await database.execute(
        "INSERT INTO gangs (name, color, leader, role, channel, control, join_base,"
        " join_slope, upkeep_base, upkeep_slope, all_paid) VALUES ('White', $1, 1, 1, 1, 1, 1, 1, 99, 1, FALSE)"
        " ON CONFLICT (name) DO UPDATE SET upkeep_base = 99",
        0x3498DB,
    )
    await database.execute("INSERT INTO gang_members (user_id, gang, paid) VALUES (001, 'White', FALSE)")
    button = gangs.DuesButton("White")
    await button.callback(interaction)
    interaction.response.defer.assert_awaited_once()
    assert interaction.response.defer.await_args.kwargs["ephemeral"] is True, "Ephemeral should be true"
    interaction.followup.send.assert_awaited_once_with(
        "You do not have enough rep to pay your dues, you have 50 rep and need 100 rep to pay your dues."
    )
    # noinspection SqlWithoutWhere
    await database.execute("DELETE FROM gang_members; DELETE FROM gangs; DELETE FROM users")


@pytest.mark.asyncio
async def test_dues_button_enough_points(mocker: MockerFixture, database):
    """Test the dues button for a member with enough points."""
    interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        response=mocker.AsyncMock(spec=discord.InteractionResponse),
        followup=mocker.AsyncMock(spec=discord.Webhook),
        client=mocker.AsyncMock(spec=CBot, pool=database),
    )
    interaction.user.id = 1
    await database.execute(
        "INSERT INTO users (id, points) VALUES (001, 100) ON CONFLICT (id) DO UPDATE SET points = 100"
    )
    await database.execute(
        "INSERT INTO gangs (name, color, leader, role, channel, control, join_base, join_slope, upkeep_base, "
        "upkeep_slope, all_paid) VALUES ('White', $1, 1, 1, 1, 1, 1, 1, 49, 1, FALSE) ON CONFLICT (name) "
        "DO UPDATE SET upkeep_base = 49",
        0x3498DB,
    )
    await database.execute("INSERT INTO gang_members (user_id, gang, paid) VALUES (001, 'White', FALSE)")
    button = gangs.DuesButton("White")
    await button.callback(interaction)
    interaction.response.defer.assert_awaited_once()
    assert interaction.response.defer.await_args.kwargs["ephemeral"] is True, "Ephemeral should be true"
    interaction.followup.send.assert_awaited_once_with(
        "You have paid your dues for White Gang! You now have 50 rep remaining."
    )
    assert await database.fetchval("SELECT paid FROM gang_members WHERE user_id = 1") is True
    assert await database.fetchval("SELECT points FROM users WHERE id = 1") == 50
    assert await database.fetchval("SELECT control FROM gangs WHERE name = 'White'") == 2
    # noinspection SqlWithoutWhere
    await database.execute("DELETE FROM gang_members; DELETE FROM gangs; DELETE FROM users")
