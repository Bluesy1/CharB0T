import discord
import pytest
from pytest_mock import MockerFixture

from charbot.programs import tictactoe
from charbot.programs.tictactoe import Difficulty, Game, Piece
from charbot.types.bot import CBot


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


@pytest.mark.parametrize("alpha_beta", [False, True])
def test_minimax_player(alpha_beta):
    player = tictactoe.MinimaxPlayer(alpha_beta)
    board = tictactoe.Board()
    piece = tictactoe.Piece.X
    index = player.play(board, piece)

    assert index in tictactoe.Board.VALID_INDICES


def test_random_player():
    player = tictactoe.RandomPlayer()
    board = tictactoe.Board()
    piece = tictactoe.Piece.X
    index = player.play(board, piece)

    assert index in tictactoe.Board.VALID_INDICES


def test_game_board_creation():
    game = Game(Difficulty.EASY)  # Easy difficulty
    board = game.board.board
    assert len(board) == 9
    assert all(p == Piece.Empty for p in board)


@pytest.mark.parametrize(
    ("difficulty", "human_first_expected"),
    [
        (1, True),  # Easy
        (2, None),  # Medium can be either)
        (3, False),  # Hard, computer first
        (4, None),  # Random can be either
    ],
)
def test_game_creator(difficulty, human_first_expected):
    game = Game(difficulty)
    if human_first_expected is not None:
        assert game.human_first == human_first_expected
    else:
        assert isinstance(game.human_first, bool)  # random, just check it's a boolean


def test_play_move():
    game = Game(Difficulty.EASY)  # Easy mode
    game.board.board = [
        Piece.X,
        Piece.X,
        Piece.Empty,
        Piece.Empty,
        Piece.O,
        Piece.Empty,
        Piece.O,
        Piece.Empty,
        Piece.Empty,
    ]

    move = game.play(2)  # Human completes a line
    assert move is None  # Game ends after victory


def test_play_move_computer_first():
    game = Game(Difficulty.HARD)  # Hard mode
    available_move = 0 if game.board.cell_is_empty(0) else 1
    move = game.play(available_move)
    assert move is not None


def test_display_commands():
    game = Game(Difficulty.EASY)
    game.play(1)  # Human move
    commands = game.display_commands()
    assert len(commands) == 9
    for idx, (_, piece) in enumerate(commands):
        if game.board.cell_is_empty(idx):
            assert piece == Piece.Empty
        else:
            assert piece != Piece.Empty


def test_win_loss_draw_detection():
    game = Game(Difficulty.EASY)
    assert not game.is_draw()
    assert game.is_victory_for() is None
    assert not game.has_player_won()
    assert not game.has_player_lost()

    game.board.board = [Piece.X, Piece.X, Piece.X, Piece.O, Piece.O, Piece.Empty, Piece.Empty, Piece.Empty, Piece.Empty]
    assert not game.is_draw()
    assert game.has_player_won()


def test_points_awarded():
    game = Game(Difficulty.EASY)

    # Loss by default
    assert game.points() == Difficulty.EASY.points.loss

    # Win condition
    game.board.board = [Piece.X, Piece.X, Piece.X, Piece.Empty, Piece.O, Piece.Empty, Piece.O, Piece.Empty, Piece.Empty]
    assert game.points() == Difficulty.EASY.points.win

    # Draw condition
    game.board.n_pieces = 9
    assert game.points() == Difficulty.EASY.points.draw
