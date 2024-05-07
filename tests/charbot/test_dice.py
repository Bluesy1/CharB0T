import random

import discord
import pytest
from discord.ext import commands
from pytest_mock import MockerFixture

from charbot import dice


@pytest.fixture(autouse=True)
def _not_random(monkeypatch) -> None:
    """Mock random.randint() to return a fixed value."""
    monkeypatch.setattr(random, "randint", lambda *args: 1)


@pytest.mark.asyncio()
async def test_valid_roll_async(mocker: MockerFixture):
    """Test valid roll command."""
    mock_bot = mocker.Mock(spec=commands.Bot)
    mock_ctx = mocker.Mock(spec=commands.Context, bot=mock_bot)
    mock_ctx.author.mention = "mock"
    cog = dice.Roll(mock_bot)
    await cog.roll.__call__(mock_ctx, mock_ctx, dice="1d4+5")  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_awaited_once()


@pytest.mark.asyncio()
async def test_invalid_roll_async(mocker: MockerFixture):
    """Test invalid roll command."""
    mock_bot = mocker.Mock(spec=commands.Bot)
    mock_ctx = mocker.Mock(spec=commands.Context, bot=mock_bot)
    mock_ctx.author.mention = "mock"
    cog = dice.Roll(mock_bot)
    await cog.roll.__call__(mock_ctx, mock_ctx, dice="1e4+5")  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_awaited_once()


def test_cog_check_no_guild(mocker: MockerFixture):
    """Test cog_check when no guild is present."""
    mock_bot = mocker.Mock(spec=commands.Bot)
    mock_ctx = mocker.Mock(spec=commands.Context, bot=mock_bot, guild=None)
    mock_ctx.bot = mock_bot
    cog = dice.Roll(mock_bot)
    assert cog.cog_check(mock_ctx) is False


def test_cog_check_not_allowed(mocker: MockerFixture):
    """Test cog_check when user is not allowed."""
    mock_bot = mocker.Mock(spec=commands.Bot)
    mock_ctx = mocker.Mock(
        spec=commands.Context,
        guild=mocker.Mock(spec=discord.Guild),
        author=mocker.Mock(spec=discord.Member, roles=[mocker.Mock(spec=discord.Role, id=0)]),
        bot=mock_bot,
    )
    cog = dice.Roll(mock_bot)
    assert cog.cog_check(mock_ctx) is False


def test_cog_check_allowed(mocker: MockerFixture):
    """Test cog_check when user is allowed."""
    mock_bot = mocker.Mock(spec=commands.Bot)
    mock_ctx = mocker.Mock(
        spec=commands.Context,
        bot=mock_bot,
        guild=mocker.Mock(spec=discord.Guild),
        author=mocker.Mock(spec=discord.Member, roles=[mocker.Mock(spec=discord.Role, id=338173415527677954)]),
    )
    mock_ctx.bot = mock_bot
    cog = dice.Roll(mock_bot)
    assert cog.cog_check(mock_ctx) is True


@pytest.mark.asyncio()
async def test_cog_load(mocker: MockerFixture):
    """Test cog_load."""
    mock_bot = mocker.Mock(spec=commands.Bot)
    await dice.setup(mock_bot)
    mock_bot.add_cog.assert_called_once()
