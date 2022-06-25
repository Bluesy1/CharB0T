# -*- coding: utf-8 -*-
import datetime
import random

import discord
import pytest
from pytest_mock import MockerFixture

from charbot import shrugman


pytestmark = pytest.mark.asyncio


@pytest.fixture
def _unused_not_random(monkeypatch):
    """Mock random.choice() to return a fixed value."""
    monkeypatch.setattr(random, "choice", lambda *args: "mock")


async def test_CBot_view_protocol(mocker: MockerFixture):
    """Test CBot protocol."""
    mock_member = mocker.Mock(spec=discord.Member)
    mock_Proto = mocker.Mock(spec=shrugman.view.CBot)
    assert await shrugman.view.CBot.give_game_points(mock_Proto, mock_member, "mock", 1) is None


async def test_view_init(_unused_not_random, mocker: MockerFixture):
    """Test Shrugman view init."""
    mock_bot = mocker.Mock(spec=shrugman.view.CBot)
    view = shrugman.Shrugman(mock_bot, "mock")
    assert view.bot is mock_bot
    assert view.word == "mock"


async def test_view_buttons_alive(_unused_not_random, mocker: MockerFixture):
    """Test Shrugman view buttons."""
    mock_bot = mocker.AsyncMock(spec=shrugman.view.CBot)
    view = shrugman.Shrugman(mock_bot, "mock")
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.guess_button.callback(mock_interaction)
    mock_interaction.response.send_modal.assert_called_once()
    mock_interaction_two = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction_two.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.stop_button.callback(mock_interaction_two)
    mock_interaction_two.response.edit_message.assert_called_once()


async def test_view_buttons_dead(_unused_not_random, mocker: MockerFixture):
    """Test Shrugman view buttons."""
    mock_bot = mocker.AsyncMock(spec=shrugman.view.CBot)
    view = shrugman.Shrugman(mock_bot, "mock")
    view.dead = True
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.message = mocker.AsyncMock(spec=discord.Message)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.guess_button.callback(mock_interaction)
    mock_interaction.response.send_message.assert_called_once_with(
        "You're dead, you can't guess anymore.", ephemeral=True
    )
    mock_interaction.message.edit.assert_called_once()


async def test_view_cancel_long_game(_unused_not_random, mocker: MockerFixture):
    """Test Shrugman view cancel."""
    mock_bot = mocker.AsyncMock(spec=shrugman.view.CBot)
    view = shrugman.Shrugman(mock_bot, "mock")
    view.start_time = discord.utils.utcnow() - datetime.timedelta(minutes=2)
    view.guess_count = 6
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.user = mocker.Mock(spec=discord.Member)
    await view.stop_button.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()
    mock_bot.give_game_points.assert_called_once_with(mock_interaction.user, "shrugman", 2, 0)
    embed = mock_interaction.response.edit_message.call_args.kwargs["embed"]
    assert embed.footer.text == "Play by typing /programs shrugman"


async def test_modal_valid_guess(_unused_not_random, mocker: MockerFixture):
    """Test Shrugman modal proper guess."""
    mock_bot = mocker.AsyncMock(spec=shrugman.view.CBot)
    game = shrugman.Shrugman(mock_bot, "a")
    modal = shrugman.GuessModal(game)
    modal.guess._value = "a"
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.user = mocker.Mock(spec=discord.Member)
    await modal.on_submit(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_message.assert_called_once()
    mock_bot.give_game_points.assert_called_once_with(mock_interaction.user, "shrugman", 2, 5)
    embed = mock_interaction.edit_original_message.call_args.kwargs["embed"]
    assert embed.footer.text == "Play by typing /programs shrugman"


async def test_modal_wrong_guess(_unused_not_random, mocker: MockerFixture):
    """Test Shrugman modal wrong guess."""
    mock_bot = mocker.AsyncMock(spec=shrugman.view.CBot)
    game = shrugman.Shrugman(mock_bot, "a")
    game.mistakes = 8
    modal = shrugman.GuessModal(game)
    modal.guess._value = "b"
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.user = mocker.Mock(spec=discord.Member)
    await modal.on_submit(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_message.assert_called_once()
    mock_bot.give_game_points.assert_called_once_with(mock_interaction.user, "shrugman", 2, 0)
    embed = mock_interaction.edit_original_message.call_args.kwargs["embed"]
    assert embed.footer.text == "Play by typing /programs shrugman"


async def test_modal_invalid_guess(_unused_not_random, mocker: MockerFixture):
    """Test Shrugman modal invalid guess."""
    mock_game = mocker.AsyncMock(spec=shrugman.Shrugman)
    modal = shrugman.GuessModal(mock_game)
    modal.guess._value = "1"
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await modal.on_submit(mock_interaction)
    mock_interaction.response.send_message.assert_called_once_with("Invalid guess.", ephemeral=True)


async def test_modal_duplicate_guess(_unused_not_random, mocker: MockerFixture):
    """Test Shrugman modal duplicate guess."""
    mock_game = mocker.AsyncMock(spec=shrugman.Shrugman)
    mock_game.guesses = ["a"]
    modal = shrugman.GuessModal(mock_game)
    modal.guess._value = "a"
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await modal.on_submit(mock_interaction)
    mock_interaction.response.send_message.assert_called_once_with("You already guessed a.", ephemeral=True)
