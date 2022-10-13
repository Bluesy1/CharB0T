# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
import discord
import pytest
from pytest_mock import MockerFixture

from charbot import CBot, gangs


@pytest.mark.asyncio
async def test_dues_button_paid(mocker: MockerFixture, database):
    """Test the dues button for an  already paid member."""
    interaction = mocker.AsyncMock(spec=discord.Interaction)
    interaction.client = mocker.AsyncMock(spec=CBot)
    interaction.client.pool = database
    interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    interaction.followup = mocker.AsyncMock(spec=discord.Webhook)
    interaction.user.id = 1
    await database.execute("INSERT INTO users (id, points) VALUES (001, 50) ON CONFLICT DO NOTHING")
    await database.execute(
        "INSERT INTO gangs (name, color, leader, role, channel, control, join_base,"
        " join_slope, upkeep_base, upkeep_slope, all_paid) VALUES ($1, $2, 1, 1, 1, 1, 1, 1, 1, 1, FALSE)"
        " ON CONFLICT DO NOTHING",
        "Gang",
        0x3498DB,
    )
    await database.execute("INSERT INTO gang_members (user_id, gang, paid) VALUES (001, 1, TRUE)")
    button = gangs.DuesButton("White")
    await button.callback(interaction)
    interaction.response.defer.assert_awaited_once()
    assert interaction.response.defer.await_args.kwargs["ephemeral"] is True, "Ephemeral should be true"
    interaction.followup.send.assert_awaited_once_with("You have already paid your dues for this month.")
    # noinspection SqlWithoutWhere
    await database.execute("DELETE FROM gang_members; DELETE FROM gangs; DELETE FROM users")
