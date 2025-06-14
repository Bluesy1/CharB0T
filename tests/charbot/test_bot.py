import datetime
import zoneinfo

import asyncpg
import discord
import pytest
from discord.utils import MISSING
from pytest_mock import MockerFixture

from charbot import Config, _Config
from charbot.bot import CBot, Holder, Tree


@pytest.fixture
def _patch_datetime_now(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the datetime.now() method to return a fixed time"""

    class MyDateTime(datetime.datetime):
        """A datetime class that returns a fixed time"""

        @classmethod
        def now(cls, tz: datetime.tzinfo | None = None):
            """Return a fixed time"""
            return datetime.datetime(1, 1, 2, 1, 0, 0, 0, tzinfo=tz)

    monkeypatch.setattr(datetime, "datetime", MyDateTime)


def test_config():
    """Test the config property"""
    assert Config is _Config()


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


@pytest.mark.usefixtures("_patch_datetime_now")
def test_time():
    """Test the time class method"""
    assert CBot.TIME() == datetime.datetime(1, 1, 1, 9, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo(key="America/Detroit"))


@pytest.mark.asyncio
async def test_first_time_gain(database: asyncpg.Pool):
    """Test that the first time gain is done properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await bot.first_time_game_gain(10, 1, 1)
    results = await database.fetchrow("SELECT points, last_particip_dt, particip, won FROM users WHERE id = 10")
    assert results is not None
    assert results["points"] == 2
    assert results["last_particip_dt"] == bot.TIME()
    assert results["particip"] == 1
    assert results["won"] == 1


@pytest.mark.asyncio
async def test_first_gain_of_day(database: asyncpg.Pool):
    """Test that the first gain of the day is done properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await database.execute(
        "INSERT INTO users (id, points, last_claim, last_particip_dt, particip, won) VALUES (10, 0, $1, $1, 10, 10)",
        bot.TIME() - datetime.timedelta(days=1),
    )
    await bot.first_of_day_game_gain(10, 1, 1)
    results = await database.fetchrow("SELECT points, last_particip_dt, particip, won FROM users WHERE id = 10")
    assert results is not None
    assert results["points"] == 2
    assert results["last_particip_dt"] == bot.TIME()
    assert results["particip"] == 1
    assert results["won"] == 1


@pytest.mark.asyncio
async def test_fallback_gain(database: asyncpg.Pool):
    """Test that the fallback gain is done properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await database.execute(
        "INSERT INTO users (id, points, last_claim, last_particip_dt, particip, won) VALUES (10, 0, $1, $1, 9, 9)",
        bot.TIME(),
    )
    await bot.fallback_game_gain(10, 9, 2, 2)
    results = await database.fetchrow("SELECT points, particip, won FROM users WHERE id = 10")
    assert results is not None
    assert results["points"] == 2
    assert results["particip"] == 10
    assert results["won"] == 10


@pytest.mark.asyncio
async def test_first_time_gain_called(mocker: MockerFixture, database: asyncpg.Pool):
    """Test that the first time gain is called properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await bot.give_game_points(mocker.AsyncMock(discord.Member, id=10), 1, 1)
    results = await database.fetchrow("SELECT points, last_particip_dt, particip, won FROM users WHERE id = 10")
    assert results is not None
    assert results["points"] == 2
    assert results["last_particip_dt"] == bot.TIME()
    assert results["particip"] == 1
    assert results["won"] == 1


@pytest.mark.asyncio
async def test_first_gain_of_day_called(mocker: MockerFixture, database: asyncpg.Pool):
    """Test that the first gain of the day is called properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await database.execute(
        "INSERT INTO users (id, points, last_claim, last_particip_dt, particip, won) VALUES (10, 0, $1, $1, 10, 10)",
        bot.TIME() - datetime.timedelta(days=1),
    )
    await bot.give_game_points(mocker.AsyncMock(discord.Member, id=10), 1, 1)
    results = await database.fetchrow("SELECT points, last_particip_dt, particip, won FROM users WHERE id = 10")
    assert results is not None
    assert results["points"] == 2
    assert results["last_particip_dt"] == bot.TIME()
    assert results["particip"] == 1
    assert results["won"] == 1


@pytest.mark.asyncio
async def test_fallback_gain_called(mocker: MockerFixture, database: asyncpg.Pool):
    """Test that the fallback gain is called properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await database.execute(
        "INSERT INTO users (id, points, last_claim, last_particip_dt, particip, won) VALUES (10, 0, $1, $1, 9, 9)",
        bot.TIME(),
    )
    await bot.give_game_points(mocker.AsyncMock(discord.Member, id=10), 2, 2)
    results = await database.fetchrow("SELECT points, particip, won FROM users WHERE id = 10")
    assert results is not None
    assert results["points"] == 2
    assert results["particip"] == 10
    assert results["won"] == 10


@pytest.mark.asyncio
async def test_give_game_points_final_branch_called(mocker: MockerFixture, database: asyncpg.Pool):
    """Test that the supposed to be unreachable branch processes properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await database.execute(
        "INSERT INTO users (id, points, last_claim, last_particip_dt, particip, won) VALUES (10, 0, $1, $1, 7, 7)",
        bot.TIME() + datetime.timedelta(days=1),
    )
    assert await bot.give_game_points(mocker.AsyncMock(discord.Member, id=10), 2, 2) == 0
    results = await database.fetchrow("SELECT points, particip, won FROM users WHERE id = 10")
    assert results is not None
    assert results["points"] == 0
    assert results["particip"] == 7
    assert results["won"] == 7
