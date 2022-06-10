# -*- coding: utf-8 -*-
import random
from unittest.mock import Mock

import discord
import pytest

from charbot import shrugman


@pytest.fixture
def _unused_not_random(monkeypatch):
    """Mock random.choice() to return a fixed value."""
    monkeypatch.setattr(random, "choice", lambda *args: "mock")


@pytest.mark.asyncio
async def test_CBot_view_protocol():
    """Test CBot protocol."""
    mock_member = Mock(spec=discord.Member)
    mock_Proto = Mock(spec=shrugman.view.CBot)
    assert await shrugman.view.CBot.give_game_points(mock_Proto, mock_member, "mock", 1) is None
    with pytest.raises(TypeError):
        shrugman.view.CBot()


@pytest.mark.asyncio
async def test_view_init(_unused_not_random):
    """Test Shrugman view init."""
    mock_bot = Mock(spec=shrugman.view.CBot)
    view = shrugman.Shrugman(mock_bot, "mock")
    assert view.bot is mock_bot
    assert view.word == "mock"
