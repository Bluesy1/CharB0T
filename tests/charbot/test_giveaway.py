# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Test the giveaway system."""
from __future__ import annotations

import asyncio
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
        giveaway.cog.pd,
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
    mock_bot = mocker.AsyncMock(spec=CBot, holder=Holder({"yesterdays_giveaway": 1, "current_giveaway": 2}))
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
    message = mocker.AsyncMock(spec=discord.WebhookMessage, embeds=[embed])
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


def test_view_from_message_invalid(mocker: MockerFixture, embed):
    """Test view recreation with invalid message"""
    embed.description = "Today's Game: Game"
    message = mocker.AsyncMock(spec=discord.WebhookMessage, embeds=[embed])
    bot = mocker.AsyncMock(spec=CBot)
    with pytest.raises(KeyError, match="Invalid giveaway embed."):
        giveaway.GiveawayView.recreate_from_message(message, bot)


@pytest.mark.asyncio
async def test_end_giveaway_with_users(mocker: MockerFixture, embed, database: asyncpg.Pool):
    """Test end_giveaway"""
    await database.executemany(
        "INSERT INTO users (id, points) VALUES ($1, $2) ON CONFLICT DO NOTHING ", [(1, 1), (2, 2), (3, 3), (4, 4)]
    )
    await database.executemany("INSERT INTO bids VALUES ($1, $2)", [(1, 1), (2, 2), (3, 3), (4, 4)])
    webhook = mocker.AsyncMock(spec=discord.Webhook)
    program_logs = mocker.AsyncMock(spec=discord.Webhook)
    bot = mocker.AsyncMock(spec=CBot, giveaway_webhook=webhook, program_logs=program_logs, pool=database)
    message = mocker.AsyncMock(
        spec=discord.WebhookMessage,
        embeds=[embed],
        guild=mocker.AsyncMock(
            spec=discord.Guild,
            fetch_member=mocker.AsyncMock(
                side_effect=lambda i: mocker.AsyncMock(spec=discord.Member, mention=f"<@{i}>")
            ),
        ),
    )
    view = giveaway.GiveawayView(bot, embed, "Game", "some_url")
    view.message = message
    random.seed(1)
    await view.end()
    assert all(
        button.disabled and button.label == "Giveaway ended" for button in (view.bid, view.check, view.toggle_alerts)
    ), "buttons should be disabled"
    webhook.send.assert_awaited_once()
    args = webhook.send.await_args.args
    assert (
        args[0] == "Congrats to <@4> for winning the Game giveaway! Please send a single DM to Charlie to claim it."
        " If you're listed under backups, stay tuned for if the first winner does not reach out to redeem their prize."
    )
    assert all(
        bid == 0 for bids in await database.fetch("SELECT bid FROM bids") for bid in bids
    ), "bids should be reset "
    message.edit.assert_awaited_once()
    bot.program_logs.send.assert_awaited_once()
    await database.execute("DELETE FROM users WHERE id <> 1")
    await database.execute("DELETE FROM bids WHERE bid = $1", 0)


@pytest.mark.asyncio
async def test_end_giveaway_no_users(mocker: MockerFixture, embed, database: asyncpg.Pool):
    """Test giveaway end where no bids were done"""
    webhook = mocker.AsyncMock(spec=discord.Webhook)
    program_logs = mocker.AsyncMock(spec=discord.Webhook)
    bot = mocker.AsyncMock(spec=CBot, giveaway_webhook=webhook, program_logs=program_logs, pool=database)
    message = mocker.AsyncMock(spec=discord.WebhookMessage, embeds=[embed])
    view = giveaway.GiveawayView(bot, embed, "Game", "some_url")
    view.message = message
    await view.end()
    assert all(
        button.disabled and button.label == "Giveaway ended" for button in (view.bid, view.check, view.toggle_alerts)
    ), "buttons should be disabled"
    webhook.send.assert_not_awaited()
    bot.program_logs.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_giveaway_bid_max_wins(mocker: MockerFixture, embed, database: asyncpg.Pool):
    """Test giveaway bid where user already has 3 wins for the month"""
    bot = mocker.AsyncMock(spec=CBot)
    bot.pool = database
    await database.execute("INSERT INTO users (id, points) VALUES ($1, $2) ON CONFLICT DO NOTHING", 2, 1)
    await database.execute("INSERT INTO winners (id, wins) VALUES ($1, 3)", 2)
    view = giveaway.GiveawayView(bot, embed, "Game", "some_url")
    interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        client=bot,
        user=mocker.AsyncMock(spec=discord.Member, id=2),
        response=mocker.AsyncMock(spec=discord.InteractionResponse),
        locale=discord.Locale.american_english,
    )
    await view.bid.callback(interaction)
    interaction.response.send_message.assert_awaited_once()
    assert interaction.response.send_message.await_args.kwargs["ephemeral"] is True
    interaction.client.translate.assert_awaited_once()
    assert interaction.client.translate.await_args.args == ("giveaway-try-later", discord.Locale.american_english)
    await database.execute("DELETE FROM users WHERE id <> 1")
    await database.execute("DELETE FROM winners WHERE id <> 1")


@pytest.mark.asyncio
async def test_giveaway_bid(mocker: MockerFixture, embed, database: asyncpg.Pool):
    """Test giveaway bid"""
    bot = mocker.AsyncMock(spec=CBot)
    bot.pool = database
    view = giveaway.GiveawayView(bot, embed, "Game", "some_url")
    interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        client=bot,
        user=mocker.AsyncMock(spec=discord.Member, id=2),
        response=mocker.AsyncMock(spec=discord.InteractionResponse),
    )
    await view.bid.callback(interaction)
    interaction.response.send_modal.assert_awaited_once()
    modal: discord.ui.Modal = interaction.response.send_modal.await_args.args[0]
    modal.stop()


@pytest.mark.asyncio
async def test_giveaway_check_max_wins(mocker: MockerFixture, embed, database: asyncpg.Pool):
    """Test giveaway check method where user already has 3 wins"""
    bot = mocker.AsyncMock(spec=CBot)
    bot.pool = database
    await database.execute("INSERT INTO users (id, points) VALUES ($1, $2) ON CONFLICT DO NOTHING", 2, 1)
    await database.execute("INSERT INTO winners (id, wins) VALUES ($1, 3)", 2)
    view = giveaway.GiveawayView(bot, embed, "Game", "some_url")
    interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        client=bot,
        user=mocker.AsyncMock(spec=discord.Member, id=2),
        response=mocker.AsyncMock(spec=discord.InteractionResponse),
        locale=discord.Locale.american_english,
    )
    await view.check.callback(interaction)
    interaction.response.send_message.assert_awaited_once()
    assert interaction.response.send_message.await_args.kwargs["ephemeral"] is True
    interaction.client.translate.assert_awaited_once()
    assert interaction.client.translate.await_args.args == ("giveaway-try-later", discord.Locale.american_english)
    await database.execute("DELETE FROM users WHERE id <> 1")
    await database.execute("DELETE FROM winners WHERE id <> 1")


@pytest.mark.asyncio
async def test_giveaway_check(mocker: MockerFixture, embed, database: asyncpg.Pool):
    """Test giveaway check method where user already has 3 wins"""
    bot = mocker.AsyncMock(spec=CBot)
    bot.pool = database
    await database.execute("INSERT INTO users (id, points) VALUES ($1, $2) ON CONFLICT DO NOTHING", 2, 1)
    await database.execute("INSERT INTO bids (id, bid) VALUES ($1, $2)", 2, 1)
    await database.execute("INSERT INTO winners (id, wins) VALUES ($1, 1)", 2)
    view = giveaway.GiveawayView(bot, embed, "Game", "some_url")
    view.total_entries = 1
    interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        client=bot,
        user=mocker.AsyncMock(spec=discord.Member, id=2),
        response=mocker.AsyncMock(spec=discord.InteractionResponse),
        locale=discord.Locale.american_english,
    )
    await view.check.callback(interaction)
    interaction.response.send_message.assert_awaited_once()
    assert interaction.response.send_message.await_args.kwargs["ephemeral"] is True
    interaction.client.translate.assert_awaited_once()
    assert interaction.client.translate.await_args.args == ("giveaway-check-success", discord.Locale.american_english)
    assert interaction.client.translate.await_args.kwargs["data"] == {"bid": 1, "chance": 1, "wins": 1}
    await database.execute("DELETE FROM users WHERE id <> 1")
    await database.execute("DELETE FROM bids WHERE id <> 1")
    await database.execute("DELETE FROM winners WHERE id <> 1")


@pytest.mark.asyncio
async def test_modal_check_points_none(mocker: MockerFixture):
    """Test the bid modal if the bidder has None for points"""
    bot = mocker.AsyncMock(spec=CBot)
    modal = giveaway.BidModal(bot, mocker.AsyncMock(spec=giveaway.GiveawayView))
    interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        client=bot,
        followup=mocker.AsyncMock(spec=discord.Webhook),
        locale=discord.Locale.american_english,
    )
    assert await modal.check_points(1, interaction, None) is False
    interaction.followup.send.assert_awaited_once()
    interaction.client.translate.assert_awaited_once()
    assert interaction.client.translate.await_args.args == ("giveaway-bid-no-rep", discord.Locale.american_english)


@pytest.mark.asyncio
async def test_modal_check_points_not_enough_points(mocker: MockerFixture):
    """Test the modal check points method when too few points"""
    bot = mocker.AsyncMock(spec=CBot)
    modal = giveaway.BidModal(bot, mocker.AsyncMock(spec=giveaway.GiveawayView))
    interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        client=bot,
        followup=mocker.AsyncMock(spec=discord.Webhook),
        locale=discord.Locale.american_english,
    )
    assert await modal.check_points(2, interaction, 1) is False
    interaction.followup.send.assert_awaited_once()
    interaction.client.translate.assert_awaited_once()
    assert interaction.client.translate.await_args.args == (
        "giveaway-bid-not-enough-rep",
        discord.Locale.american_english,
    )
    assert interaction.client.translate.await_args.kwargs["data"] == {"bid": 2, "points": 1}


@pytest.mark.asyncio
async def test_modal_check_points_valid(mocker: MockerFixture):
    """Test the modal check points method when enough points"""
    bot = mocker.AsyncMock(spec=CBot)
    modal = giveaway.BidModal(bot, mocker.AsyncMock(spec=giveaway.GiveawayView))
    interaction = mocker.AsyncMock(spec=discord.Interaction)
    assert await modal.check_points(1, interaction, 2) is True


@pytest.mark.asyncio
async def test_modal_invalid_bid_callback(mocker: MockerFixture):
    """Test the modal invalid bid callback"""
    bot = mocker.AsyncMock(spec=CBot)
    modal = giveaway.BidModal(bot, mocker.AsyncMock(spec=giveaway.GiveawayView))
    interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        client=bot,
        response=mocker.AsyncMock(spec=discord.InteractionResponse),
        locale=discord.Locale.american_english,
    )
    await modal.invalid_bid(interaction)
    interaction.response.send_message.assert_awaited_once()
    assert interaction.response.send_message.await_args.kwargs["ephemeral"] is True
    interaction.client.translate.assert_awaited_once()
    assert interaction.client.translate.await_args.args == ("giveaway-bid-invalid-bid", discord.Locale.american_english)


@pytest.mark.asyncio
async def test_modal_bid_success(mocker: MockerFixture):
    """Test the modal bid success callback"""
    bot = mocker.AsyncMock(spec=CBot)
    modal = giveaway.BidModal(bot, mocker.AsyncMock(spec=giveaway.GiveawayView, total_entries=1, top_bid=1))
    interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        client=bot,
        followup=mocker.AsyncMock(spec=discord.Webhook),
        locale=discord.Locale.american_english,
    )
    await modal.bid_success(interaction, 2, 2, 3, None)
    interaction.followup.send.assert_awaited_once()
    assert interaction.followup.send.await_args.kwargs["ephemeral"] is True
    interaction.client.translate.assert_awaited_once()
    assert interaction.client.translate.await_args.args == ("giveaway-bid-success", discord.Locale.american_english)
    assert interaction.client.translate.await_args.kwargs["data"] == {
        "bid": 2,
        "new_bid": 2,
        "chance": 2 / 3,
        "points": 3,
        "wins": 0,
    }
    assert modal.view.top_bid == 2


@pytest.mark.asyncio
async def test_modal_on_submit(mocker: MockerFixture, database: asyncpg.Pool):
    """Test the on modal submit works as expected"""
    await database.execute("INSERT INTO users (id, points) VALUES (2, 5)")
    await database.execute("INSERT INTO bids (id, bid) VALUES (2, 0)")
    bot = mocker.AsyncMock(spec=CBot, pool=database)
    modal = giveaway.BidModal(
        bot, mocker.AsyncMock(spec=giveaway.GiveawayView, total_entries=1, top_bid=1, bid_lock=asyncio.Lock())
    )
    interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        client=bot,
        response=mocker.AsyncMock(spec=discord.InteractionResponse),
        followup=mocker.AsyncMock(spec=discord.Webhook),
        locale=discord.Locale.american_english,
        user=mocker.AsyncMock(spec=discord.User, id=2),
    )
    modal.bid_str._value = "2"
    await modal.on_submit(interaction)
    interaction.response.defer.assert_awaited_once()
    assert interaction.response.defer.await_args.kwargs == {"ephemeral": True, "thinking": True}
    interaction.followup.send.assert_awaited_once()
    assert await database.fetchval("SELECT bid FROM bids WHERE id = 2") == 2
    assert await database.fetchval("SELECT points FROM users WHERE id = 2") == 3
    await database.execute("DELETE FROM bids WHERE id = 2")
    await database.execute("DELETE FROM users WHERE id = 2")


def test_rectify_bid():
    """Test the rectify bid method"""
    assert giveaway.modal.rectify_bid(2, 32767, 50) == 1
    assert giveaway.modal.rectify_bid(1, None, 2) == 1
    assert giveaway.modal.rectify_bid(2, 2, 1) == 1
    assert giveaway.modal.rectify_bid(2, 5, 2) == 2
