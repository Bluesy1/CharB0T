# -*- coding: utf-8 -*-
from io import BytesIO

import discord
import pytest
from PIL import Image
from pytest_mock import MockerFixture

from charbot import CBot
from charbot.programs import tictactoe


@pytest.fixture()
def photo():
    """Return a mock photo."""
    grid = Image.open("charbot/media/tictactoe/grid.png", "r").convert("RGBA")
    cross = Image.open("charbot/media/tictactoe/X.png", "r")
    circle = Image.open("charbot/media/tictactoe/O.png", "r")
    grid.paste(cross, (0, 0), cross)
    grid.paste(circle, (179, 0), circle)
    img = BytesIO()
    grid.save(img, "PNG")
    img.seek(0)
    return discord.File(img, filename="tictactoe.png")


@pytest.fixture()
def _unused_mock_generator(monkeypatch, photo):
    """Patch tictactoe generator to return a fixed value."""
    monkeypatch.setattr(tictactoe.TicTacEasy, "display", lambda *args: photo)


@pytest.mark.asyncio
async def test_view_init(mocker: MockerFixture):
    """Test TicTacToe view init."""
    mock_bot = mocker.Mock(spec=CBot)
    view = tictactoe.TicTacView(mock_bot, "X")
    assert view.bot is mock_bot
    assert view.letter == "X"
    assert len(view._buttons) == 9


@pytest.mark.asyncio
async def test_view_stop_method(mocker: MockerFixture):
    """Test TicTacToe view stop method."""
    mock_bot = mocker.Mock(spec=CBot)
    view = tictactoe.TicTacView(mock_bot, "X")
    view.disable()
    assert view.is_finished()
    for button in view._buttons:
        assert button.disabled
    assert view.cancel.disabled


@pytest.mark.asyncio
async def test_view_move_method(_unused_mock_generator, photo, event_loop, mocker: MockerFixture):
    """Test TicTacToe view move method."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_bot.loop = event_loop
    view = tictactoe.TicTacView(mock_bot, "X", easy=True)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.move(mock_interaction, view._buttons[0], 0, 0)
    mock_interaction.response.edit_message.assert_called_once_with(view=None)
    mock_interaction.edit_original_message.assert_called_once()
    assert mock_interaction.edit_original_message.call_args.kwargs["attachments"][0] is photo
    assert view.top_left.disabled


@pytest.mark.asyncio
async def test_view_player_win(_unused_mock_generator, photo, event_loop, mocker: MockerFixture):
    """Test TicTacToe view player win method."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_bot.loop = event_loop
    view = tictactoe.TicTacView(mock_bot, "X", easy=True)
    view.puzzle.check_win = mocker.Mock(spec=tictactoe.TicTacEasy.check_win, return_value=1)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.move(mock_interaction, view._buttons[0], 0, 0)
    mock_interaction.response.edit_message.assert_called_once_with(view=None)
    mock_interaction.edit_original_message.assert_called_once()
    assert mock_interaction.edit_original_message.call_args.kwargs["attachments"][0] is photo
    assert view.top_left.disabled
    mock_bot.give_game_points.assert_called_once_with(mock_interaction.user, "tictactoe", 1, 1)


@pytest.mark.asyncio
async def test_view_bot_win(_unused_mock_generator, photo, event_loop, mocker: MockerFixture):
    """Test TicTacToe view bot win method."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_bot.loop = event_loop
    view = tictactoe.TicTacView(mock_bot, "X", easy=False)
    view.puzzle.board = [
        ["O", "blur", "blur"],  # top row
        ["X", "O", "blur"],  # middle row
        ["blur", "blur", "blur"],  # bottom row
    ]
    view.top_left.disabled = True
    view.mid_left.disabled = True
    view.mid_mid.disabled = True
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.move(mock_interaction, view._buttons[7], 2, 1)
    mock_interaction.response.edit_message.assert_called_once_with(view=None)
    mock_interaction.edit_original_message.assert_called_once()
    assert mock_interaction.edit_original_message.call_args.kwargs["attachments"][0] is photo
    mock_bot.give_game_points.assert_called_once_with(mock_interaction.user, "tictactoe", 0, 0)
    assert view.is_finished()
    for button in view._buttons:
        assert button.disabled
    assert view.cancel.disabled
    assert view.puzzle.check_win() == 0


@pytest.mark.asyncio
async def test_view_tie(_unused_mock_generator, photo, event_loop, mocker: MockerFixture):
    """Test TicTacToe view tie method."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_bot.loop = event_loop
    view = tictactoe.TicTacView(mock_bot, "X", easy=True)
    view.puzzle.board = [
        ["O", "blur", "O"],  # top row
        ["X", "O", "X"],  # middle row
        ["X", "O", "X"],  # bottom row
    ]
    for button in view._buttons:
        button.disabled = True
    view.top_mid.disabled = False
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.move(mock_interaction, view._buttons[1], 0, 1)
    mock_interaction.response.edit_message.assert_called_once_with(view=None)
    mock_interaction.edit_original_message.assert_called_once()
    assert mock_interaction.edit_original_message.call_args.kwargs["attachments"][0] is photo
    mock_bot.give_game_points.assert_called_once_with(mock_interaction.user, "tictactoe", 1, 0)
    assert view.is_finished()
    for button in view._buttons:
        assert button.disabled
    assert view.cancel.disabled
    assert view.puzzle.check_win() == -1


@pytest.mark.asyncio
@pytest.mark.parametrize("button", [0, 1, 2, 3, 4, 5, 6, 7, 8])
async def test_move_buttons(button, _unused_mock_generator, photo, event_loop, mocker: MockerFixture):
    """Test TicTacToe move button methods."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_bot.loop = event_loop
    view = tictactoe.TicTacView(mock_bot, "X", easy=True)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view._buttons[button].callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once_with(view=None)
    mock_interaction.edit_original_message.assert_called_once()
    assert mock_interaction.edit_original_message.call_args.kwargs["attachments"][0] is photo
    assert view._buttons[button].disabled


@pytest.mark.asyncio
async def test_cancel_button(_unused_mock_generator, photo, mocker: MockerFixture):
    """Test TicTacToe cancel button method."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    view = tictactoe.TicTacView(mock_bot, "X", easy=True)
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


@pytest.mark.parametrize(
    "state,expected",
    [
        (1, {"participation": 1, "bonus": 1}),
        (0, {"participation": 0, "bonus": 0}),
        (-1, {"participation": 1, "bonus": 0}),
    ],
)
def test_easy_points(state, expected):
    """Test TicTacToe easy points method."""
    easy = tictactoe.TicTacEasy("X", 3)
    easy.check_win = lambda: state
    assert easy.points == tictactoe.abstract.Points(**expected)
    assert easy.check_win() == state


@pytest.mark.parametrize(
    "state,expected",
    [
        (1, {"participation": 2, "bonus": 3}),
        (0, {"participation": 0, "bonus": 0}),
        (-1, {"participation": 2, "bonus": 1}),
    ],
)
def test_hard_points(state, expected):
    """Test TicTacToe easy points method."""
    easy = tictactoe.TicTacHard("X", 3)
    easy.check_win = lambda: state
    assert easy.points == tictactoe.abstract.Points(**expected)
    assert easy.check_win() == state


@pytest.mark.parametrize(
    "board,pick,expected",
    [
        ([["X", "O", "X"], ["O", "X", "O"], ["X", "O", "X"]], "X", 1),
        ([["X", "O", "X"], ["O", "X", "O"], ["X", "O", "X"]], "O", 0),
        ([["X", "X", "X"], ["O", "O", "X"], ["X", "O", "O"]], "X", 1),
        ([["X", "X", "X"], ["O", "O", "X"], ["X", "O", "O"]], "O", 0),
        ([["O", "blur", "O"], ["X", "O", "X"], ["X", "O", "X"]], "X", -1),
        ([["O", "blur", "O"], ["X", "O", "X"], ["X", "O", "X"]], "O", -1),
    ],
)
def test_win_states(board, pick, expected):
    """Test TicTacToe win states method."""
    if pick not in ("X", "O"):
        raise ValueError(f"pick must be either 'X' or 'O', not '{pick}'")
    easy = tictactoe.TicTacEasy(pick, 3)
    easy.board = board
    assert easy.check_win() == expected


@pytest.mark.parametrize(
    "pick,expected,board",
    [
        ((-1, -1), False, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((0, 0), True, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((0, 0), False, [["X", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((0, 1), True, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((0, 2), True, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((0, 3), False, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((1, 0), True, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((1, 1), True, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((1, 2), True, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((1, 3), False, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((2, 0), True, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((2, 1), True, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((2, 2), True, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((2, 3), False, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((3, 0), False, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((3, 1), False, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((3, 2), False, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
        ((3, 3), False, [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]),
    ],
)
def test_check_valid_move(pick, expected, board):
    """Test TicTacToe check valid move method."""
    easy = tictactoe.TicTacEasy("X", 3)
    easy.board = board
    assert easy.move(*pick) is expected


def test_display_board(photo):
    """Test TicTacToe display board method."""
    easy = tictactoe.TicTacEasy("X", 3)
    easy.board = [["X", "O", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]]
    assert easy.display().fp.read() == photo.fp.read()


def test_win_spots_hard():
    """Test TicTacToe win spots method."""
    hard = tictactoe.TicTacHard("X", 3)
    hard.board = [["X", "blur", "X"], ["O", "blur", "O"], ["X", "O", "X"]]
    assert hard._win_spots("X", "O") == ([(0, 1), (1, 1)], [(1, 1)])


def test_next_move_hard():
    """Test TicTacToe win spots method."""
    hard = tictactoe.TicTacHard("O", 3)
    hard.board = [["X", "blur", "X"], ["O", "blur", "O"], ["X", "O", "X"]]
    assert hard._next_move_easy() == (0, 1)


@pytest.mark.parametrize(
    "board,computer,player,available,expected",
    [
        (
            [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]],
            [(0, 0)],
            [],
            [(0, 0)],
            (0, 0),
        ),
        (
            [["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]],
            [],
            [(0, 0)],
            [(0, 0)],
            (0, 0),
        ),
        ([["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]], [], [], [(0, 0)], (0, 0)),
        ([["blur", "blur", "blur"], ["blur", "blur", "blur"], ["blur", "blur", "blur"]], [], [], [], (-1, -1)),
        ([["X", "blur", "blur"], ["blur", "O", "blur"], ["blur", "blur", "X"]], [], [], [(0, 2), (2, 0)], (0, 2)),
        ([["X", "blur", "X"], ["blur", "O", "blur"], ["blur", "blur", "X"]], [], [], [(0, 2), (2, 0)], (2, 0)),
        ([["blur", "blur", "X"], ["blur", "O", "blur"], ["X", "blur", "blur"]], [], [], [(0, 0), (2, 2)], (0, 0)),
        ([["O", "blur", "X"], ["blur", "O", "blur"], ["X", "blur", "blur"]], [], [], [(0, 0), (2, 2)], (2, 2)),
        ([["blur", "blur", "X"], ["blur", "X", "blur"], ["O", "blur", "blur"]], [], [], [(0, 0), (2, 2)], 0),
    ],
)
def test_simple_move_checks_hard(board, computer, player, available, expected):
    """Test TicTacToe simple move method."""
    hard = tictactoe.TicTacHard("X", 3)
    hard.board = board
    assert hard._simple_move_checks(computer, player, available, "O") == expected


@pytest.mark.parametrize(
    "available,expected",
    [
        ([(1, 1), (1, 3), (3, 1), (2, 2)], (1, 1)),
        ([(1, 3), (3, 1), (2, 2)], (1, 3)),
        ([(3, 1), (2, 2)], (3, 1)),
        ([(3, 3), (2, 2)], (3, 3)),
        ([(0, 1), (4, 1), (1, 0), (1, 4)], (0, 1)),
        ([(4, 1), (1, 0), (1, 4)], (4, 1)),
        ([(1, 0), (1, 4)], (1, 0)),
        ([(1, 4)], (1, 4)),
        ((2, 2), 0),
    ],
)
def test_complex_move_checks_hard(available, expected):
    """Test TicTacToe complex move method."""
    hard = tictactoe.TicTacHard("X", 5)
    assert hard._complex_move_checks(available, "O") == expected


def test_next_move_hard_center():
    """Test TicTacToe next move method."""
    hard = tictactoe.TicTacHard("O", 3)
    assert hard._next_move_easy() == (1, 1)


def test_next_move_hard_force_complex():
    """Test TicTacToe next move method."""
    hard = tictactoe.TicTacHard("X", 3)
    hard.board = [["blur", "blur", "blur"], ["blur", "X", "blur"], ["blur", "blur", "blur"]]
    assert hard._next_move_easy() == (0, 0)


def test_next_move_hard_force_complex_2():
    """Test TicTacToe next move method."""
    hard = tictactoe.TicTacHard("X", 3)
    hard.board = [["X", "blur", "O"], ["O", "O", "X"], ["X", "blur", "O"]]
    with pytest.raises(RuntimeError):
        hard._next_move_easy()
