import datetime
import zoneinfo

import asyncpg
import discord
import pytest
from discord.utils import MISSING
from pytest_mock import MockerFixture

from charbot import Config, _Config
from charbot.bot import CBot, Holder, Tree


@pytest.fixture()
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


@pytest.mark.asyncio()
async def test_first_time_gain(database: asyncpg.Pool):
    """Test that the first time gain is done properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await bot.first_time_game_gain(10, 1, 1)
    assert await database.fetchval("SELECT points FROM users WHERE id = 10") == 2
    assert await database.fetchval("SELECT bid FROM bids WHERE id = 10") == 0
    assert dict(  # pyright: ignore[reportCallIssue]
        await database.fetchrow(  # pyright: ignore[reportArgumentType]
            "SELECT last_particip_dt, particip, won FROM daily_points WHERE id = 10"
        )
    ) == {
        "last_particip_dt": bot.TIME(),
        "particip": 1,
        "won": 1,
    }
    await database.execute("DELETE FROM users WHERE id = 10")


@pytest.mark.asyncio()
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
    assert dict(  # pyright: ignore[reportCallIssue]
        await database.fetchrow(  # pyright: ignore[reportArgumentType]
            "SELECT last_particip_dt, particip, won FROM daily_points WHERE id = 10"
        )
    ) == {
        "last_particip_dt": bot.TIME(),
        "particip": 1,
        "won": 1,
    }
    await database.execute("DELETE FROM users WHERE id = 10")


@pytest.mark.asyncio()
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
    assert dict(  # pyright: ignore[reportCallIssue]
        await database.fetchrow(  # pyright: ignore[reportArgumentType]
            "SELECT particip, won FROM daily_points WHERE id = 10"
        )
    ) == {
        "particip": 10,
        "won": 10,
    }
    await database.execute("DELETE FROM users WHERE id = 10")


@pytest.mark.asyncio()
async def test_first_time_gain_called(mocker: MockerFixture, database: asyncpg.Pool):
    """Test that the first time gain is called properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await bot.give_game_points(mocker.AsyncMock(discord.Member, id=10), 1, 1)
    assert await database.fetchval("SELECT points FROM users WHERE id = 10") == 2
    assert await database.fetchval("SELECT bid FROM bids WHERE id = 10") == 0
    assert dict(  # pyright: ignore[reportCallIssue]
        await database.fetchrow(  # pyright: ignore[reportArgumentType]
            "SELECT last_particip_dt, particip, won FROM daily_points WHERE id = 10"
        )
    ) == {
        "last_particip_dt": bot.TIME(),
        "particip": 1,
        "won": 1,
    }
    await database.execute("DELETE FROM users WHERE id = 10")


@pytest.mark.asyncio()
async def test_first_gain_of_day_called(mocker: MockerFixture, database: asyncpg.Pool):
    """Test that the first gain of the day is called properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await database.execute("INSERT INTO users (id, points) VALUES (10, 0)")
    await database.execute(
        "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won) VALUES (10, $1, $1, 10, 10)",
        bot.TIME() - datetime.timedelta(days=1),
    )
    await database.execute("INSERT INTO bids (id, bid) VALUES (10, 0)")
    await bot.give_game_points(mocker.AsyncMock(discord.Member, id=10), 1, 1)
    assert await database.fetchval("SELECT points FROM users WHERE id = 10") == 2
    assert dict(  # pyright: ignore[reportCallIssue]
        await database.fetchrow(  # pyright: ignore[reportArgumentType]
            "SELECT last_particip_dt, particip, won FROM daily_points WHERE id = 10"
        )
    ) == {
        "last_particip_dt": bot.TIME(),
        "particip": 1,
        "won": 1,
    }
    await database.execute("DELETE FROM users WHERE id = 10")


@pytest.mark.asyncio()
async def test_fallback_gain_called(mocker: MockerFixture, database: asyncpg.Pool):
    """Test that the fallback gain is called properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await database.execute("INSERT INTO users (id, points) VALUES (10, 0)")
    await database.execute(
        "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won) VALUES (10, $1, $1, 9, 9)",
        bot.TIME(),
    )
    await database.execute("INSERT INTO bids (id, bid) VALUES (10, 0)")
    await bot.give_game_points(mocker.AsyncMock(discord.Member, id=10), 2, 2)
    assert await database.fetchval("SELECT points FROM users WHERE id = 10") == 2
    assert dict(  # pyright: ignore[reportCallIssue]
        await database.fetchrow(  # pyright: ignore[reportArgumentType]
            "SELECT particip, won FROM daily_points WHERE id = 10"
        )
    ) == {
        "particip": 10,
        "won": 10,
    }
    await database.execute("DELETE FROM users WHERE id = 10")


@pytest.mark.asyncio()
async def test_give_game_points_final_branch_called(mocker: MockerFixture, database: asyncpg.Pool):
    """Test that the supposed to be unreachable branch processes properly"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    bot.pool = database
    await database.execute("INSERT INTO users (id, points) VALUES (10, 0)")
    await database.execute(
        "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won) VALUES (10, $1, $1, 7, 7)",
        bot.TIME() + datetime.timedelta(days=1),
    )
    await database.execute("INSERT INTO bids (id, bid) VALUES (10, 0)")
    assert await bot.give_game_points(mocker.AsyncMock(discord.Member, id=10), 2, 2) == 0
    assert await database.fetchval("SELECT points FROM users WHERE id = 10") == 0
    assert dict(  # pyright: ignore[reportCallIssue]
        await database.fetchrow(  # pyright: ignore[reportArgumentType]
            "SELECT particip, won FROM daily_points WHERE id = 10"
        )
    ) == {"particip": 7, "won": 7}
    await database.execute("DELETE FROM users WHERE id = 10")


@pytest.mark.asyncio()
async def test_translate_good_key():
    """Test that the translation method works with a good key"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    assert (
        await bot.translate("giveaway-try-later", discord.Locale.american_english)
        == "You have won 3 giveaways recently, please wait until the first of the next month to bid again."
    )


@pytest.mark.asyncio()
async def test_translate_bad_key_with_fallback():
    """Test that the translation method works with a bad key"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    assert await bot.translate("bad-key", discord.Locale.american_english, fallback="fallback") == "fallback"


@pytest.mark.asyncio()
async def test_translate_bad_key_without_fallback():
    """Test that the translation method works with a bad key"""
    bot = CBot(command_prefix=[], tree_cls=Tree, intents=discord.Intents.default())
    with pytest.raises(ValueError, match="Key bad-key not a valid key for translation"):
        await bot.translate("bad-key", discord.Locale.american_english)
