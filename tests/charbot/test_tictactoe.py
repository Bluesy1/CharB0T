import discord
import pytest
from pytest_mock import MockerFixture

from charbot.programs import tictactoe
from charbot.types.bot import CBot
from charbot_rust.tictactoe import Difficulty, Game


@pytest.mark.asyncio
async def test_view_init():
    """Test TicTacToe view init."""
    view = tictactoe.TicTacToe(Difficulty.EASY)
    assert len(view._buttons) == 9


@pytest.mark.asyncio
async def test_view_stop_method():
    """Test TicTacToe view stop method."""
    view = tictactoe.TicTacToe(Difficulty.EASY)
    view.disable()
    assert view.is_finished()
    for button in view._buttons:
        assert button.disabled
    assert view.cancel.disabled


@pytest.mark.asyncio
async def test_view_move_method(mocker: MockerFixture):
    """Test TicTacToe view move method."""
    view = tictactoe.TicTacToe(Difficulty.EASY)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.move(mock_interaction, view._buttons[0], 0)
    mock_interaction.response.edit_message.assert_called_once_with(view=None)
    mock_interaction.edit_original_response.assert_called_once()
    assert view.top_left.disabled


@pytest.mark.asyncio
async def test_view_player_win(mocker: MockerFixture):
    """Test TicTacToe view player win method."""
    view = tictactoe.TicTacToe(Difficulty.EASY)
    view.game = mocker.Mock(spec=Game)
    view.game.play = lambda position: None
    view.game.points = lambda: (1, 1)
    view.display = lambda: None  # pyright: ignore[reportAttributeAccessIssue]
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.client = mocker.AsyncMock(spec=CBot)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.move(mock_interaction, view._buttons[0], 0)
    mock_interaction.response.edit_message.assert_called_once_with(view=None)
    mock_interaction.edit_original_response.assert_called_once()
    assert view.top_left.disabled


@pytest.mark.asyncio
async def test_view_bot_win(mocker: MockerFixture):
    """Test TicTacToe view bot win method."""
    view = tictactoe.TicTacToe(Difficulty.EASY)
    view.game = mocker.Mock(spec=Game)
    view.game.play = lambda position: 1
    view.game.is_draw = lambda: False
    view.game.has_player_lost = lambda: True
    view.game.has_player_won = lambda: False
    view.game.points = lambda: (1, 1)
    view.display = lambda: None  # pyright: ignore[reportAttributeAccessIssue]
    view.top_left.disabled = True
    view.mid_left.disabled = True
    view.mid_mid.disabled = True
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.client = mocker.AsyncMock(spec=CBot)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.move(mock_interaction, view._buttons[7], 7)
    mock_interaction.response.edit_message.assert_called_once_with(view=None)
    mock_interaction.edit_original_response.assert_called_once()
    assert view.is_finished()
    for button in view._buttons:
        assert button.disabled
    assert view.cancel.disabled


@pytest.mark.asyncio
async def test_view_tie(mocker: MockerFixture):
    """Test TicTacToe view tie method."""
    view = tictactoe.TicTacToe(Difficulty.EASY)
    view.game = mocker.Mock(spec=Game)
    view.game.play = lambda position: 1
    view.game.has_player_lost = lambda: False
    view.game.has_player_won = lambda: False
    view.game.is_draw = lambda: True
    view.game.points = lambda: (1, 1)
    view.display = lambda: None  # pyright: ignore[reportAttributeAccessIssue]
    for button in view._buttons:
        button.disabled = True
    view.top_mid.disabled = False
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.client = mocker.AsyncMock(spec=CBot)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.move(mock_interaction, view._buttons[1], 1)
    mock_interaction.response.edit_message.assert_called_once_with(view=None)
    mock_interaction.edit_original_response.assert_called_once()
    assert view.is_finished()
    for button in view._buttons:
        assert button.disabled
    assert view.cancel.disabled


@pytest.mark.asyncio
@pytest.mark.parametrize("button", [0, 1, 2, 3, 4, 5, 6, 7, 8])
async def test_move_buttons(button, mocker: MockerFixture):
    """Test TicTacToe move button methods."""
    view = tictactoe.TicTacToe(Difficulty.EASY)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view._buttons[button].callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once_with(view=None)
    mock_interaction.edit_original_response.assert_called_once()
    assert view._buttons[button].disabled


@pytest.mark.asyncio
async def test_cancel_button(mocker: MockerFixture):
    """Test TicTacToe cancel button method."""
    view = tictactoe.TicTacToe(Difficulty.EASY)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.cancel.callback(mock_interaction)
    assert view.is_finished()
    for button in view._buttons:
        assert button.disabled
    assert view.cancel.disabled
    mock_interaction.response.edit_message.assert_called_once()
    assert "embed" in mock_interaction.response.edit_message.call_args.kwargs
    embed = mock_interaction.response.edit_message.call_args.kwargs["embed"]
    assert isinstance(embed, discord.Embed)
    assert embed.title == "TicTacToe"
    assert embed.color == discord.Color.red()
    assert embed.footer.text == "Start playing by typing /programs tictactoe"
