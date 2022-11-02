# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT
import datetime
import zoneinfo

import asyncpg
import discord
import pytest
from discord.utils import MISSING

from charbot.bot import CBot, Holder, Tree


@pytest.fixture
def unused_patch_datetime_now(monkeypatch: pytest.MonkeyPatch):
    """Patch the datetime.now() method to return a fixed time"""

    class MyDateTime(datetime.datetime):
        """A datetime class that returns a fixed time"""

        @classmethod
        def now(cls, tz: datetime.tzinfo | None = ...):
            """Return a fixed time"""
            return datetime.datetime(1, 1, 2, 1, 0, 0, 0, tzinfo=tz)

    monkeypatch.setattr(datetime, "datetime", MyDateTime)


def test_holder():
    """Test the Holder class"""
    holder = Holder()
    val = holder["value"]
    assert val is MISSING
    del holder["nonexistent"]
    assert holder.pop("nonexistent") is MISSING
    assert holder.get("nonexistent") is MISSING
    holder.setdefault("value", "default")
    assert holder["value"] == "default"
    holder.setdefault("value", "new")
    assert holder["value"] == "default"
    assert holder.get("value") == "default"
    assert holder.pop("value") == "default"
    assert holder.get("value") is MISSING
    holder["value"] = "new"
    del holder["value"]
    assert holder.get("value") is MISSING


def test_time(unused_patch_datetime_now):
    """Test the time class method"""
    assert CBot.TIME() == datetime.datetime(1, 1, 1, 9, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo(key="America/Detroit"))


@pytest.mark.asyncio
async def test_first_time_gain(database: asyncpg.Pool):
    """Test that the first time gain is done properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await bot.first_time_game_gain(10, 1, 1)
    assert await database.fetchval("SELECT points FROM users WHERE id = 10") == 2
    assert await database.fetchval("SELECT bid FROM bids WHERE id = 10") == 0
    assert dict(
        await database.fetchrow(  # pyright: ignore[reportGeneralTypeIssues]
            "SELECT last_particip_dt, particip, won FROM daily_points WHERE id = 10"
        )
    ) == {
        "last_particip_dt": bot.TIME(),
        "particip": 1,
        "won": 1,
    }
    await database.execute("DELETE FROM users WHERE id = 10")


@pytest.mark.asyncio
async def test_first_gain_of_day(database: asyncpg.Pool):
    """Test that the first gain of the day is done properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await database.execute("INSERT INTO users (id, points) VALUES (10, 0)")
    await database.execute(
        "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won) VALUES (10, $1, $1, 10, 10)",
        bot.TIME() - datetime.timedelta(days=1),
    )
    await bot.first_of_day_game_gain(10, 1, 1)
    assert await database.fetchval("SELECT points FROM users WHERE id = 10") == 2
    assert dict(
        await database.fetchrow(  # pyright: ignore[reportGeneralTypeIssues]
            "SELECT last_particip_dt, particip, won FROM daily_points WHERE id = 10"
        )
    ) == {
        "last_particip_dt": bot.TIME(),
        "particip": 1,
        "won": 1,
    }
    await database.execute("DELETE FROM users WHERE id = 10")


@pytest.mark.asyncio
async def test_fallback_gain(database: asyncpg.Pool):
    """Test that the fallback gain is done properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await database.execute("INSERT INTO users (id, points) VALUES (10, 0)")
    await database.execute(
        "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won) VALUES (10, $1, $1, 9, 9)",
        bot.TIME(),
    )
    await bot.fallback_game_gain(10, 9, 2, 2)
    assert await database.fetchval("SELECT points FROM users WHERE id = 10") == 2
    assert dict(
        await database.fetchrow(  # pyright: ignore[reportGeneralTypeIssues]
            "SELECT particip, won FROM daily_points WHERE id = 10"
        )
    ) == {
        "particip": 10,
        "won": 10,
    }
    await database.execute("DELETE FROM users WHERE id = 10")


@pytest.mark.asyncio
async def test_translate_good_key():
    """Test that the translation method works with a good key"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    assert (
        await bot.translate("giveaway-try-later", discord.Locale.american_english)
        == "You have won 3 giveaways recently, please wait until the first of the next month to bid again."
    )


@pytest.mark.asyncio
async def test_translate_bad_key_with_fallback():
    """Test that the translation method works with a bad key"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    assert await bot.translate("bad-key", discord.Locale.american_english, fallback="fallback") == "fallback"


@pytest.mark.asyncio
async def test_translate_bad_key_without_fallback():
    """Test that the translation method works with a bad key"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    with pytest.raises(ValueError) as exec_info:
        await bot.translate("bad-key", discord.Locale.american_english)
    assert exec_info.value.args[0] == "Key bad-key not a valid key for translation"
