import datetime
import random

import discord
import pytest
from pytest_mock import MockerFixture

from charbot import CBot
from charbot.programs import shrugman


pytestmark = pytest.mark.asyncio


@pytest.fixture
def _not_random(monkeypatch) -> None:
    """Mock random.choice() to return a fixed value."""
    monkeypatch.setattr(random, "choice", lambda *args: "mock")


@pytest.mark.usefixtures("_not_random")
async def test_view_init(mocker: MockerFixture):
    """Test Shrugman view init."""
    mock_bot = mocker.Mock(spec=CBot)
    view = shrugman.Shrugman(mock_bot, "mock")
    assert view.bot is mock_bot
    assert view.word == "mock"


@pytest.mark.usefixtures("_not_random")
async def test_view_buttons_alive(mocker: MockerFixture):
    """Test Shrugman view buttons."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    view = shrugman.Shrugman(mock_bot, "mock")
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.guess_button.callback(mock_interaction)
    mock_interaction.response.send_modal.assert_called_once()
    mock_interaction_two = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction_two.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.stop_button.callback(mock_interaction_two)
    mock_interaction_two.response.edit_message.assert_called_once()


@pytest.mark.usefixtures("_not_random")
async def test_view_buttons_dead(mocker: MockerFixture):
    """Test Shrugman view buttons."""
    mock_bot = mocker.AsyncMock(spec=CBot)
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


@pytest.mark.usefixtures("_not_random")
async def test_view_cancel_long_game(mocker: MockerFixture):
    """Test Shrugman view cancel."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    view = shrugman.Shrugman(mock_bot, "mock")
    view.start_time = discord.utils.utcnow() - datetime.timedelta(minutes=2)
    view.guess_count = 6
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.user = mocker.Mock(spec=discord.Member)
    await view.stop_button.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()
    mock_bot.give_game_points.assert_called_once_with(mock_interaction.user, 2, 0)
    embed = mock_interaction.response.edit_message.call_args.kwargs["embed"]
    assert embed.footer.text == "Play by typing /programs shrugman"


@pytest.mark.usefixtures("_not_random")
async def test_modal_valid_guess(mocker: MockerFixture):
    """Test Shrugman modal proper guess."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    game = shrugman.Shrugman(mock_bot, "a")
    modal = shrugman.GuessModal(game)
    modal.guess._value = "a"
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.user = mocker.Mock(spec=discord.Member)
    await modal.on_submit(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_response.assert_called_once()
    mock_bot.give_game_points.assert_called_once_with(mock_interaction.user, 2, 5)
    embed = mock_interaction.edit_original_response.call_args.kwargs["embed"]
    assert embed.footer.text == "Play by typing /programs shrugman"


@pytest.mark.usefixtures("_not_random")
async def test_modal_wrong_guess(mocker: MockerFixture):
    """Test Shrugman modal wrong guess."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    game = shrugman.Shrugman(mock_bot, "a")
    game.mistakes = 8
    modal = shrugman.GuessModal(game)
    modal.guess._value = "b"
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.user = mocker.Mock(spec=discord.Member)
    await modal.on_submit(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_response.assert_called_once()
    mock_bot.give_game_points.assert_called_once_with(mock_interaction.user, 2, 0)
    embed = mock_interaction.edit_original_response.call_args.kwargs["embed"]
    assert embed.footer.text == "Play by typing /programs shrugman"


@pytest.mark.usefixtures("_not_random")
async def test_modal_invalid_guess(mocker: MockerFixture):
    """Test Shrugman modal invalid guess."""
    mock_game = mocker.AsyncMock(spec=shrugman.Shrugman)
    modal = shrugman.GuessModal(mock_game)
    modal.guess._value = "1"
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.followup = mocker.AsyncMock(spec=discord.Webhook)
    await modal.on_submit(mock_interaction)
    mock_interaction.followup.send.assert_called_once_with("Invalid guess.", ephemeral=True)
    mock_interaction.response.defer.assert_called_once_with(ephemeral=True)


@pytest.mark.usefixtures("_not_random")
async def test_modal_duplicate_guess(mocker: MockerFixture):
    """Test Shrugman modal duplicate guess."""
    mock_game = mocker.AsyncMock(spec=shrugman.Shrugman)
    mock_game.guesses = ["a"]
    modal = shrugman.GuessModal(mock_game)
    modal.guess._value = "a"
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.followup = mocker.AsyncMock(spec=discord.Webhook)
    await modal.on_submit(mock_interaction)
    mock_interaction.followup.send.assert_called_once_with("You already guessed a.", ephemeral=True)
    mock_interaction.response.defer.assert_called_once_with(ephemeral=True)
