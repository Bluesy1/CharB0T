# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Test the giveaway system."""
from __future__ import annotations

import random

import asyncpg
import discord
import pandas
import pytest
from pytest_mock import MockerFixture

from charbot import giveaway
from charbot.bot import CBot, Holder


@pytest.fixture
def mock_pandas_read_csv(monkeypatch):
    """Mock pandas.read_csv"""
    df = pandas.DataFrame(
        data={
            "date": ["5/1/2022", "5/2/2022", "5/3/2022"],
            "game": ["SOUL CALIBUR VI", "SUPERHOT", "CIVILIZATION VI: PLATINUM EDITION"],
            "url": [
                "https://store.steampowered.com/app/544750/SOULCALIBUR_VI/",
                "https://store.steampowered.com/app/322500/SUPERHOT/",
                "https://store.steampowered.com/bundle/12218",
            ],
            "source": ["HUMBLE - DEC 2019 MONTHLY", "HUMBLE - CONQUER COVID BUNDLE", "HUMBLE - JUNE 2021"],
        }
    )
    monkeypatch.setattr(
        giveaway.pd,
        "read_csv",
        lambda *args, **kwargs: df,
    )
    yield df


@pytest.fixture
def embed():
    """Test embed."""
    return discord.Embed.from_dict(
        {
            "footer": {"text": "Started at"},
            "author": {
                "name": "name",
                "icon_url": "mock",
            },
            "fields": [
                {"name": "mock", "value": "mock", "inline": True},
                {"name": "mock", "value": "mock.", "inline": True},
                {"name": "mock", "value": "mock", "inline": True},
                {"name": "Total Reputation Bid", "value": "1", "inline": True},
            ],
            "color": 2123412,
            "url": "https://store.steampowered.com/",
            "description": "Today's Game: [Game](some_url)",
        }
    )


def test_cog_init(mock_pandas_read_csv, mocker: MockerFixture):
    """Test Cog.__init__"""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_bot.holder = Holder({"yesterdays_giveaway": 1, "current_giveaway": 2})
    cog = giveaway.Giveaway(mock_bot)
    assert cog.games is mock_pandas_read_csv, "games should be set to the dataframe"
    assert cog.yesterdays_giveaway == 1, "yesterdays_giveaway should be set to 1 given the mock data"
    assert cog.current_giveaway == 2, "current_giveaway should be set to 2 given the mock data"
    assert cog.charlie is discord.utils.MISSING, "Charlie should not be set yet"
    assert cog.bot is mock_bot, "bot should be set to the mock bot"
    assert 1 not in mock_bot.holder, "1 should not be in the holder anymore"
    assert 2 not in mock_bot.holder, "2 should not be in the holder anymore"


@pytest.mark.asyncio
async def test_view_from_message(mocker: MockerFixture, embed):
    """Test view recreation"""
    message = mocker.AsyncMock(spec=discord.WebhookMessage)
    message.embeds = [embed]
    bot = mocker.AsyncMock(spec=CBot)
    view = giveaway.GiveawayView.recreate_from_message(message, bot)
    assert view.message is message, "message should be set to the mock message"
    assert view.bot is bot, "bot should be set to the mock bot"
    assert view.url == "https://store.steampowered.com/", "url should be set to the url in the embed"
    assert view.total_entries == 1, "value should be set to 1"
    assert view.top_bid == 0, "value should be set to 0"
    assert len(view.bidders) == 0, "bidders should be empty"
    assert view.game == "Game", "game should be set to the game in the embed"
    assert len(view.children) == 4, "children should be set to the 4 buttons"
    assert view.check.disabled is False, "check should be enabled"


@pytest.mark.asyncio
async def test_end_giveaway(mocker: MockerFixture, embed, database: asyncpg.Pool):
    """Test end_giveaway"""
    bot = mocker.AsyncMock(spec=CBot)
    webhook = mocker.AsyncMock(spec=discord.Webhook)
    bot.giveaway_webhook = webhook
    bot.program_logs = mocker.AsyncMock()
    await database.executemany(
        "INSERT INTO users (id, points) VALUES ($1, $2) ON CONFLICT DO NOTHING ", [(1, 1), (2, 2), (3, 3)]
    )
    await database.executemany("INSERT INTO bids VALUES ($1, $2)", [(1, 1), (2, 2), (3, 3)])
    bot.pool = database
    view = giveaway.GiveawayView(bot, embed, "Game", "some_url")
    message = mocker.AsyncMock(spec=discord.WebhookMessage)
    message.embeds = [embed]
    message.guild = mocker.AsyncMock(spec=discord.Guild)
    message.guild.fetch_member = mocker.AsyncMock(
        side_effect=lambda i: mocker.AsyncMock(spec=discord.Member, mention=f"<@{i}>")
    )
    view.message = message
    random.seed(1)
    await view.end()
    assert all(
        button.disabled and button.label == "Giveaway ended" for button in (view.bid, view.check, view.toggle_alerts)
    ), "buttons should be disabled"
    webhook.send.assert_awaited_once()
    args = webhook.send.await_args.args
    assert (
        args[0] == "Congrats to <@3> for winning the Game giveaway! Please send a single DM to Charlie to claim it."
        " If you're listed under backups, stay tuned for if the first winner does not reach out to redeem their prize."
    )
    assert all(bid == 0 for bids in await database.fetch("SELECT bid FROM bids") for bid in bids), (
        "bids should be " "reset "
    )
    message.edit.assert_awaited_once()
    await database.execute("DELETE FROM users WHERE id <> 1")
    await database.execute("DELETE FROM bids WHERE bid = $1", 0)
