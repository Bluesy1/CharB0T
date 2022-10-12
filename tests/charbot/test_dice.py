# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
import random

import discord
import pytest
from discord.ext import commands
from fluent.runtime import FluentResourceLoader, FluentLocalization
from pytest_mock import MockerFixture

from charbot import dice


@pytest.fixture(autouse=True)
def not_random(monkeypatch):
    """Mock random.randint() to return a fixed value."""
    monkeypatch.setattr(random, "randint", lambda *args: 1)


@pytest.fixture()
def user_localizer() -> tuple[str, FluentLocalization]:
    """Return a user localizer.

    Returns:
        tuple[str, FluentLocalization]: A tuple of the user's locale and the user's localizer.
    """
    return "User", FluentLocalization(["en-US"], ["dice.ftl"], FluentResourceLoader("i18n/{locale}"))


def test_valid_roll(user_localizer):
    """Test valid roll."""
    assert dice.roll("1d4+5", *user_localizer) == "User rolled `1d4+5` and got `1, 5`for a total of `6`."


def test_valid_implicit_roll(user_localizer):
    """Test valid implicit roll."""
    assert dice.roll("d4+5", *user_localizer) == "User rolled `d4+5` and got `1, 5`for a total of `6`."


def test_valid_implicit_roll_no_bonus(user_localizer):
    """Test valid implicit roll without bonus."""
    assert dice.roll("d4", *user_localizer) == "User rolled `d4` and got `1`for a total of `1`."


def test_valid_implicit_roll_only_bonus(user_localizer):
    """Test valid implicit roll only bonus."""
    assert dice.roll("5", *user_localizer) == "User rolled `5` and got `5`for a total of `5`."


def test_invalid_roll(user_localizer):
    """Test invalid roll."""
    assert dice.roll("1e4+5", *user_localizer) == (
        "User:\n"
        "Error invalid argument:\n"
        " Specified dice can only be d<int>, or if a constant modifier must be a "
        "perfect integer, positive or negative, connected with `+`, and no spaces."
    )


def test_invalid_die(user_localizer):
    """Test invalid die."""
    assert dice.roll("1de+5", *user_localizer) == (
        "User:\n"
        "Error invalid argument:\n"
        " Specified dice can only be d<int>, or if a constant modifier must be a "
        "perfect integer, positive or negative, connected with `+`, and no spaces."
    )


@pytest.mark.asyncio
async def test_valid_roll_async(mocker: MockerFixture):
    """Test valid roll command."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_bot = mocker.Mock(spec=commands.Bot)
    mock_bot.localizer_loader = FluentResourceLoader("i18n/{locale}")
    mock_ctx.bot = mock_bot
    mock_ctx.author.mention = "mock"
    cog = dice.Roll(mock_bot)
    await cog.roll.__call__(mock_ctx, mock_ctx, dice="1d4+5")  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once_with("mock rolled `1d4+5` and got `1, 5`for a total of `6`.", mention_author=True)


@pytest.mark.asyncio
async def test_invalid_roll_async(mocker: MockerFixture):
    """Test invalid roll command."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_bot = mocker.Mock(spec=commands.Bot)
    mock_bot.localizer_loader = FluentResourceLoader("i18n/{locale}")
    mock_ctx.bot = mock_bot
    mock_ctx.author.mention = "mock"
    cog = dice.Roll(mock_bot)
    await cog.roll.__call__(mock_ctx, mock_ctx, dice="1e4+5")  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once_with(
        "mock:\n"
        "Error invalid argument:\n"
        " Specified dice can only be d<int>, or if a constant modifier must be a "
        "perfect integer, positive or negative, connected with `+`, and no spaces.",
        mention_author=True,
    )


def test_cog_check_no_guild(mocker: MockerFixture):
    """Test cog_check when no guild is present."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_ctx.guild = None
    mock_bot = mocker.Mock(spec=commands.Bot)
    mock_bot.localizer_loader = FluentResourceLoader("i18n/{locale}")
    mock_ctx.bot = mock_bot
    cog = dice.Roll(mock_bot)
    assert cog.cog_check(mock_ctx) is False


def test_cog_check_not_allowed(mocker: MockerFixture):
    """Test cog_check when user is not allowed."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_ctx.guild = mocker.Mock(spec=discord.Guild)
    mock_ctx.author = mocker.Mock(spec=discord.Member)
    mock_role = mocker.Mock(spec=discord.Role)
    mock_role.id = 0
    mock_ctx.author.roles = [mock_role]
    mock_bot = mocker.Mock(spec=commands.Bot)
    mock_bot.localizer_loader = FluentResourceLoader("i18n/{locale}")
    mock_ctx.bot = mock_bot
    cog = dice.Roll(mock_bot)
    assert cog.cog_check(mock_ctx) is False


def test_cog_check_allowed(mocker: MockerFixture):
    """Test cog_check when user is allowed."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_ctx.guild = mocker.Mock(spec=discord.Guild)
    mock_ctx.author = mocker.Mock(spec=discord.Member)
    mock_role = mocker.Mock(spec=discord.Role)
    mock_role.id = 338173415527677954
    mock_ctx.author.roles = [mock_role]
    mock_bot = mocker.Mock(spec=commands.Bot)
    mock_bot.localizer_loader = FluentResourceLoader("i18n/{locale}")
    mock_ctx.bot = mock_bot
    cog = dice.Roll(mock_bot)
    assert cog.cog_check(mock_ctx) is True


@pytest.mark.asyncio
async def test_cog_load(mocker: MockerFixture):
    """Test cog_load."""
    mock_bot = mocker.Mock(spec=commands.Bot)
    await dice.setup(mock_bot)
    mock_bot.add_cog.assert_called_once()
