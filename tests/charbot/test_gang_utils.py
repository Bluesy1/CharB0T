# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import discord
import pytest
from pytest_mock import MockerFixture

from charbot.gangs import utils, types


@pytest.fixture
def items() -> list[types.Item]:
    """Return a list of items."""
    return [types.Item("Item", "Description", 1, 1) for _ in range(26)]


@pytest.fixture
def interaction(mocker: MockerFixture):
    """Return a mock interaction."""
    inter = mocker.AsyncMock(spec=discord.Interaction, response=mocker.AsyncMock(spec=discord.InteractionResponse))
    inter.user.id = 1
    return inter


@pytest.mark.parametrize("slice_end,expected", [(0, 0), (25, 1), (26, 2)])
def test_item_embed_pages(items, slice_end, expected):
    """Check that the correct items are returned."""
    assert len(list(utils.item_embed_pages(items[:slice_end]))) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("user,expected", [(0, False), (1, True)])
async def test_items_view_interaction_check(items, interaction, user, expected):
    """Check that the interaction check returns True."""
    view = utils.ItemsView(items, user)
    assert await view.interaction_check(interaction) is expected


# noinspection DuplicatedCode
@pytest.mark.asyncio
async def test_items_view_buttons(items, interaction):
    """Check that the buttons are added."""
    view = utils.ItemsView(items, 1)
    assert view.current == 0
    assert view.max == 1
    assert view.first.disabled is view.back.disabled is True
    assert view.next.disabled is view.last.disabled is False
    await view.last.callback(interaction)
    assert view.current == 1
    assert view.first.disabled is view.back.disabled is False
    assert view.next.disabled is view.last.disabled is True
    await view.first.callback(interaction)
    assert view.current == 0
    assert view.first.disabled is view.back.disabled is True
    assert view.next.disabled is view.last.disabled is False
    await view.next.callback(interaction)
    assert view.current == 1
    assert view.first.disabled is view.back.disabled is False
    assert view.next.disabled is view.last.disabled is True
    await view.back.callback(interaction)
    assert view.current == 0
    assert view.first.disabled is view.back.disabled is True
    assert view.next.disabled is view.last.disabled is False
    await view.stop.callback(interaction)
    interaction.delete_original_response.assert_awaited_once()
