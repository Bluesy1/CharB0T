# -*- coding: utf-8 -*-
import datetime
import random
from unittest.mock import AsyncMock, Mock

import discord
import pytest

from charbot import shrugman


pytestmark = pytest.mark.asyncio


@pytest.fixture
def _unused_not_random(monkeypatch):
    """Mock random.choice() to return a fixed value."""
    monkeypatch.setattr(random, "choice", lambda *args: "mock")


async def test_CBot_view_protocol():
    """Test CBot protocol."""
    mock_member = Mock(spec=discord.Member)
    mock_Proto = Mock(spec=shrugman.view.CBot)
    assert await shrugman.view.CBot.give_game_points(mock_Proto, mock_member, "mock", 1) is None


async def test_view_init(_unused_not_random):
    """Test Shrugman view init."""
    mock_bot = Mock(spec=shrugman.view.CBot)
    view = shrugman.Shrugman(mock_bot, "mock")
    assert view.bot is mock_bot
    assert view.word == "mock"


async def test_view_buttons_alive(_unused_not_random):
    """Test Shrugman view buttons."""
    mock_bot = AsyncMock(spec=shrugman.view.CBot)
    view = shrugman.Shrugman(mock_bot, "mock")
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await view.guess_button.callback(mock_interaction)
    mock_interaction.response.send_modal.assert_called_once()
    mock_interaction_two = AsyncMock(spec=discord.Interaction)
    mock_interaction_two.response = AsyncMock(spec=discord.InteractionResponse)
    await view.stop_button.callback(mock_interaction_two)
    mock_interaction_two.response.edit_message.assert_called_once()


async def test_view_buttons_dead(_unused_not_random):
    """Test Shrugman view buttons."""
    mock_bot = AsyncMock(spec=shrugman.view.CBot)
    view = shrugman.Shrugman(mock_bot, "mock")
    view.dead = True
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.message = AsyncMock(spec=discord.Message)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await view.guess_button.callback(mock_interaction)
    mock_interaction.response.send_message.assert_called_once_with(
        "You're dead, you can't guess anymore.", ephemeral=True
    )
    mock_interaction.message.edit.assert_called_once()


async def test_view_cancel_long_game(_unused_not_random):
    """Test Shrugman view cancel."""
    mock_bot = AsyncMock(spec=shrugman.view.CBot)
    view = shrugman.Shrugman(mock_bot, "mock")
    view.start_time = discord.utils.utcnow() - datetime.timedelta(minutes=2)
    view.guess_count = 6
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.user = Mock(spec=discord.Member)
    await view.stop_button.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()
    mock_bot.give_game_points.assert_called_once_with(mock_interaction.user, "shrugman", 2, 0)


async def test_modal_valid_guess(_unused_not_random):
    """Test Shrugman modal proper guess."""
    mock_bot = AsyncMock(spec=shrugman.view.CBot)
    game = shrugman.Shrugman(mock_bot, "a")
    modal = shrugman.GuessModal(game)
    modal.guess._value = "a"
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.user = Mock(spec=discord.Member)
    await modal.on_submit(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_message.assert_called_once()
    mock_bot.give_game_points.assert_called_once_with(mock_interaction.user, "shrugman", 2, 5)


async def test_modal_wrong_guess(_unused_not_random):
    """Test Shrugman modal wrong guess."""
    mock_bot = AsyncMock(spec=shrugman.view.CBot)
    game = shrugman.Shrugman(mock_bot, "a")
    game.mistakes = 8
    modal = shrugman.GuessModal(game)
    modal.guess._value = "b"
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.user = Mock(spec=discord.Member)
    await modal.on_submit(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_message.assert_called_once()
    mock_bot.give_game_points.assert_called_once_with(mock_interaction.user, "shrugman", 2, 0)


async def test_modal_invalid_guess(_unused_not_random):
    """Test Shrugman modal invalid guess."""
    mock_game = AsyncMock(spec=shrugman.Shrugman)
    modal = shrugman.GuessModal(mock_game)
    modal.guess._value = "1"
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await modal.on_submit(mock_interaction)
    mock_interaction.response.send_message.assert_called_once_with("Invalid guess.", ephemeral=True)


async def test_modal_duplicate_guess(_unused_not_random):
    """Test Shrugman modal duplicate guess."""
    mock_game = AsyncMock(spec=shrugman.Shrugman)
    mock_game.guesses = ["a"]
    modal = shrugman.GuessModal(mock_game)
    modal.guess._value = "a"
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await modal.on_submit(mock_interaction)
    mock_interaction.response.send_message.assert_called_once_with("You already guessed a.", ephemeral=True)