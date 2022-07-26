# -*- coding: utf-8 -*-

import discord
import pytest
from discord.ext import commands
from pytest_mock import MockerFixture

from charbot import query


def test_cog_check_no_guild(mocker: MockerFixture):
    """Test cog_check when no guild is present."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_ctx.guild = None
    mock_bot = mocker.Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    assert cog.cog_check(mock_ctx) is False


def test_cog_check_not_allowed(mocker: MockerFixture):
    """Test cog_check when user is not allowed."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_ctx.guild = mocker.Mock(spec=discord.Guild)
    mock_ctx.author = mocker.Mock(spec=discord.Member)
    mock_role = mocker.Mock(spec=discord.Role)
    mock_role.id = 684936661745795088
    mock_ctx.author.roles = [mock_role]
    mock_bot = mocker.Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
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
    cog = query.Query(mock_bot)
    assert cog.cog_check(mock_ctx) is True


@pytest.mark.asyncio
async def test_time_command(mocker: MockerFixture):
    """Test time command."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_bot = mocker.Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.time.__call__(mock_ctx, mock_ctx)  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once()


@pytest.mark.asyncio
async def test_changelog_command(mocker: MockerFixture):
    """Test changelog command."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_bot = mocker.Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.changelog.__call__(mock_ctx, mock_ctx)  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once_with("Here's the changelog: https://bluesy1.github.io/CharB0T/changes")


@pytest.mark.asyncio
async def test_faq_command(mocker: MockerFixture):
    """Test faq command."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_bot = mocker.Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.faq.__call__(mock_ctx, mock_ctx)  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once()


@pytest.mark.asyncio
async def test_source_command(mocker: MockerFixture):
    """Test source command."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_bot = mocker.Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.source.__call__(mock_ctx, mock_ctx)  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once_with(f"https://bluesy1.github.io/CharB0T/\n{query.__source__}\nMIT License")


@pytest.mark.asyncio
async def test_setup_function(mocker: MockerFixture):
    """Test setup function."""
    mock_bot = mocker.AsyncMock(spec=commands.Bot)
    await query.setup(mock_bot)
    mock_bot.add_cog.assert_called_once()
