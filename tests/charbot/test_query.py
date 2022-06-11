# -*- coding: utf-8 -*-
from unittest.mock import AsyncMock, Mock

import discord
import pytest
from discord.ext import commands

from charbot import query


def test_cog_check_no_guild():
    """Test cog_check when no guild is present."""
    mock_ctx = Mock(spec=commands.Context)
    mock_ctx.guild = None
    mock_bot = Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    assert cog.cog_check(mock_ctx) is False


def test_cog_check_not_allowed():
    """Test cog_check when user is not allowed."""
    mock_ctx = Mock(spec=commands.Context)
    mock_ctx.guild = Mock(spec=discord.Guild)
    mock_ctx.author = Mock(spec=discord.Member)
    mock_role = Mock(spec=discord.Role)
    mock_role.id = 684936661745795088
    mock_ctx.author.roles = [mock_role]
    mock_bot = Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    assert cog.cog_check(mock_ctx) is False


def test_cog_check_allowed():
    """Test cog_check when user is allowed."""
    mock_ctx = Mock(spec=commands.Context)
    mock_ctx.guild = Mock(spec=discord.Guild)
    mock_ctx.author = Mock(spec=discord.Member)
    mock_role = Mock(spec=discord.Role)
    mock_role.id = 338173415527677954
    mock_ctx.author.roles = [mock_role]
    mock_bot = Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    assert cog.cog_check(mock_ctx) is True


@pytest.mark.asyncio
async def test_time_command():
    """Test time command."""
    mock_ctx = Mock(spec=commands.Context)
    mock_bot = Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.time.__call__(mock_ctx, mock_ctx)  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once()


@pytest.mark.asyncio
async def test_changelog_command():
    """Test changelog command."""
    mock_ctx = Mock(spec=commands.Context)
    mock_bot = Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.changelog.__call__(mock_ctx, mock_ctx)  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once_with("Here's the changelog: https://bluesy1.github.io/CharB0T/changes")


@pytest.mark.asyncio
async def test_faq_command():
    """Test faq command."""
    mock_ctx = Mock(spec=commands.Context)
    mock_bot = Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.faq.__call__(mock_ctx, mock_ctx)  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once()


@pytest.mark.asyncio
async def test_source_command():
    """Test source command."""
    mock_ctx = Mock(spec=commands.Context)
    mock_bot = Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.source.__call__(mock_ctx, mock_ctx)  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once_with(f"https://bluesy1.github.io/CharB0T/\n{query.__source__}\nMIT License")


@pytest.mark.asyncio
async def test_imgscam_command():
    """Test imgscam command."""
    mock_ctx = Mock(spec=commands.Context)
    mock_bot = Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.imgscam.__call__(mock_ctx, mock_ctx)  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once_with("https://blog.hyperphish.com/articles/001-loading/")


@pytest.mark.asyncio
async def test_setup_function():
    """Test setup function."""
    mock_bot = AsyncMock(spec=commands.Bot)
    await query.setup(mock_bot)
    mock_bot.add_cog.assert_called_once()
