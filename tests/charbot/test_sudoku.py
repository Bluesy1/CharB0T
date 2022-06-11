# -*- coding: utf-8 -*-
import datetime
from unittest.mock import AsyncMock, Mock

import asyncpg
import discord
import pytest

from charbot import sudoku


@pytest.fixture
def _unused_puzzle_unsolved():
    """Mock puzzle."""
    return sudoku.Puzzle(
        [
            [7, 1, 0, 0, 5, 0, 0, 8, 0],
            [2, 0, 0, 0, 0, 7, 0, 0, 0],
            [0, 4, 5, 0, 3, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 6, 7, 5],
            [0, 0, 0, 2, 9, 5, 0, 0, 0],
            [5, 8, 3, 0, 0, 6, 0, 0, 0],
            [0, 0, 0, 0, 2, 0, 5, 6, 0],
            [0, 0, 0, 7, 0, 0, 0, 0, 8],
            [0, 7, 0, 0, 4, 0, 0, 3, 1],
        ],
        mobile=True,
    )


@pytest.fixture
def _unused_puzzle_solved():
    """Mock puzzle."""
    return sudoku.Puzzle(
        [
            [7, 1, 9, 6, 5, 4, 3, 8, 2],
            [2, 3, 6, 8, 1, 7, 9, 5, 4],
            [8, 4, 5, 9, 3, 2, 7, 1, 6],
            [9, 2, 4, 1, 8, 3, 6, 7, 5],
            [1, 6, 7, 2, 9, 5, 8, 4, 3],
            [5, 8, 3, 4, 7, 6, 1, 2, 9],
            [4, 9, 1, 3, 2, 8, 5, 6, 7],
            [3, 5, 2, 7, 6, 1, 4, 9, 8],
            [6, 7, 8, 5, 4, 9, 2, 3, 1],
        ],
        mobile=True,
    )


@pytest.mark.asyncio
async def test_CBot_view_protocol():
    """Test CBot protocol."""
    mock_member = Mock(spec=discord.Member)
    mock_Proto = Mock(spec=sudoku.view.CBot)
    assert await sudoku.view.CBot.give_game_points(mock_Proto, mock_member, "mock", 1) is None


@pytest.mark.asyncio
async def test_view_init(_unused_puzzle_unsolved):
    """Test Sudoku view init."""
    mock_bot = Mock(spec=sudoku.view.CBot)
    mock_member = Mock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    assert view.bot is mock_bot
    assert view.puzzle is _unused_puzzle_unsolved
    assert view.author is mock_member


@pytest.mark.asyncio
async def test_view_keypad_callback_enter_block(_unused_puzzle_unsolved):
    """Test Sudoku view update keypad."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    mock_button = Mock(spec=discord.Button)
    await view.keypad_callback(mock_interaction, mock_button, 0)
    mock_interaction.response.defer.assert_called_once_with(ephemeral=True)
    assert view.block is _unused_puzzle_unsolved.blocks[0]
    assert not view.puzzle.is_solved
    assert view.one.disabled
    assert view.two.disabled
    assert not view.three.disabled
    assert view.four.disabled
    assert not view.five.disabled
    assert not view.six.disabled
    assert not view.seven.disabled
    assert view.eight.disabled
    assert view.nine.disabled
    mock_interaction.edit_original_message.assert_called_once()


@pytest.mark.asyncio
async def test_view_keypad_callback_enter_cell(_unused_puzzle_unsolved):
    """Test Sudoku view update keypad."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    mock_button = Mock(spec=discord.Button)
    await view.keypad_callback(mock_interaction, mock_button, 0)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.keypad_callback(mock_interaction, mock_button, 2)
    assert view.cell is _unused_puzzle_unsolved.blocks[0][2]
    assert not view.puzzle.is_solved
    assert not view.one.disabled
    assert not view.two.disabled
    assert not view.three.disabled
    assert not view.four.disabled
    assert not view.five.disabled
    assert not view.six.disabled
    assert not view.seven.disabled
    assert not view.eight.disabled
    assert not view.nine.disabled
    mock_interaction.edit_original_message.assert_called_once()


@pytest.mark.asyncio
async def test_view_keypad_callback_set_cell_value(_unused_puzzle_unsolved):
    """Test Sudoku view update keypad."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    mock_button = Mock(spec=discord.Button)
    mock_button.label = "9"
    await view.keypad_callback(mock_interaction, mock_button, 0)
    await view.keypad_callback(mock_interaction, mock_button, 2)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.keypad_callback(mock_interaction, mock_button, 9)
    assert view.cell is discord.utils.MISSING
    assert view.puzzle.blocks[0][2].value == 9
    assert not view.puzzle.is_solved
    assert view.block is _unused_puzzle_unsolved.blocks[0]
    assert not view.puzzle.is_solved
    assert view.one.disabled
    assert view.two.disabled
    assert not view.three.disabled
    assert view.four.disabled
    assert not view.five.disabled
    assert not view.six.disabled
    assert not view.seven.disabled
    assert view.eight.disabled
    assert view.nine.disabled
    assert view.block is _unused_puzzle_unsolved.blocks[0]
    mock_interaction.edit_original_message.assert_called_once()


@pytest.mark.asyncio
async def test_view_keypad_callback_remove_possible_cell_value(_unused_puzzle_unsolved):
    """Test Sudoku view update keypad."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    view.noting_mode = True
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    mock_button = Mock(spec=discord.Button)
    mock_button.label = "9"
    await view.keypad_callback(mock_interaction, mock_button, 0)
    await view.keypad_callback(mock_interaction, mock_button, 2)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    with pytest.raises(NotImplementedError):
        await view.keypad_callback(mock_interaction, mock_button, 9)


@pytest.mark.asyncio
async def test_view_keypad_callback_add_possible_cell_value(_unused_puzzle_unsolved):
    """Test Sudoku view update keypad."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    view.noting_mode = True
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    mock_button = Mock(spec=discord.Button)
    mock_button.label = "9"
    await view.keypad_callback(mock_interaction, mock_button, 0)
    await view.keypad_callback(mock_interaction, mock_button, 2)
    view.cell.possible_values.remove(9)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    with pytest.raises(NotImplementedError):
        await view.keypad_callback(mock_interaction, mock_button, 9)


@pytest.mark.asyncio
async def test_view_keypad_callback_try_set_static_cell(_unused_puzzle_unsolved):
    """Test Sudoku view update keypad."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    mock_button = Mock(spec=discord.Button)
    await view.keypad_callback(mock_interaction, mock_button, 0)
    await view.keypad_callback(mock_interaction, mock_button, 1)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.keypad_callback(mock_interaction, mock_button, 2)
    mock_interaction.edit_original_message.assert_called_once()
    assert view.cell is discord.utils.MISSING
    assert view.block.selected


@pytest.mark.asyncio
async def test_view_update_keypad_puzzle_level(_unused_puzzle_unsolved):
    """Test Sudoku view update keypad."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    view.disable_keypad()
    view.update_keypad()
    assert view.back.disabled
    assert not view.one.disabled
    assert not view.two.disabled
    assert not view.three.disabled
    assert not view.four.disabled
    assert not view.five.disabled
    assert not view.six.disabled
    assert not view.seven.disabled
    assert not view.eight.disabled
    assert not view.nine.disabled


@pytest.mark.asyncio
async def test_view_block_choose_embed(_unused_puzzle_unsolved):
    """Test Sudoku view block choose embed."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    embed = view.block_choose_embed()
    assert embed.title == "Sudoku"
    assert embed.footer.text == "Play Sudoku by Typing /programs sudoku"
    assert embed.color == discord.Color.blurple()


@pytest.mark.asyncio
async def test_view_on_win(_unused_puzzle_solved):
    """Test Sudoku view on win."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_bot.pool = AsyncMock(spec=asyncpg.Pool)
    mock_member = AsyncMock(spec=discord.Member)
    _unused_puzzle_solved.blocks[0][0]._editable = True
    _unused_puzzle_solved.blocks[0][0].value = 0
    view = sudoku.Sudoku(_unused_puzzle_solved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    mock_button = AsyncMock(spec=discord.Button)
    mock_button.label = "7"
    await view.keypad_callback(mock_interaction, mock_button, 0)
    await view.keypad_callback(mock_interaction, mock_button, 0)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.keypad_callback(mock_interaction, mock_button, 7)
    mock_interaction.edit_original_message.assert_called_once()
    assert view.is_finished()
    args = mock_bot.pool.execute.call_args.args
    assert args[0] == "UPDATE users SET sudoku_time = $1 WHERE id = $2 and sudoku_time > $1"
    mock_bot.give_game_points.assert_called_once_with(mock_member, "sudoku", 5, 10)


@pytest.mark.asyncio
async def test_view_back_button_callback(_unused_puzzle_unsolved):
    """Test Sudoku view back button callback."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    view.back.disabled = False
    await view.back.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()
    assert view.back.disabled
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    view.block = _unused_puzzle_unsolved.blocks[0]
    view.level = "Block"
    view.block.selected = True
    view.update_keypad()
    await view.back.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()
    assert view.back.disabled
    assert view.level == "Puzzle"
    assert view.block is discord.utils.MISSING
    assert not _unused_puzzle_unsolved.blocks[0].selected
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    view.block = _unused_puzzle_unsolved.blocks[0]
    view.cell = view.block[2]
    view.cell.selected = True
    view.level = "Cell"
    view.update_keypad()
    await view.back.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()
    assert not view.back.disabled
    assert view.level == "Block"
    assert view.cell is discord.utils.MISSING
    assert view.block.selected


@pytest.mark.asyncio
async def test_one_button_callback(_unused_puzzle_unsolved):
    """Test Sudoku one button callback."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await view.one.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_message.assert_called_once()


@pytest.mark.asyncio
async def test_two_button_callback(_unused_puzzle_unsolved):
    """Test Sudoku two button callback."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await view.two.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_message.assert_called_once()


@pytest.mark.asyncio
async def test_three_button_callback(_unused_puzzle_unsolved):
    """Test Sudoku three button callback."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await view.three.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_message.assert_called_once()


@pytest.mark.asyncio
async def test_four_button_callback(_unused_puzzle_unsolved):
    """Test Sudoku four button callback."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await view.four.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_message.assert_called_once()


@pytest.mark.asyncio
async def test_five_button_callback(_unused_puzzle_unsolved):
    """Test Sudoku five button callback."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await view.five.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_message.assert_called_once()


@pytest.mark.asyncio
async def test_six_button_callback(_unused_puzzle_unsolved):
    """Test Sudoku six button callback."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await view.six.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_message.assert_called_once()


@pytest.mark.asyncio
async def test_seven_button_callback(_unused_puzzle_unsolved):
    """Test Sudoku seven button callback."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await view.seven.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_message.assert_called_once()


@pytest.mark.asyncio
async def test_eight_button_callback(_unused_puzzle_unsolved):
    """Test Sudoku eight button callback."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await view.eight.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_message.assert_called_once()


@pytest.mark.asyncio
async def test_nine_button_callback(_unused_puzzle_unsolved):
    """Test Sudoku nine button callback."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await view.nine.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_message.assert_called_once()


@pytest.mark.asyncio
async def test_mode_select(_unused_puzzle_unsolved):
    """Test sudoku mode select."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    with pytest.raises(NotImplementedError):
        await view.mode.callback(mock_interaction)


@pytest.mark.asyncio
async def test_cancel_callback(_unused_puzzle_unsolved):
    """Test sudoku cancel callback."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await view.cancel.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    view.start_time = discord.utils.utcnow() - datetime.timedelta(minutes=5)
    view.moves = 20
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.cancel.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()


@pytest.mark.asyncio
async def test_clear_callback(_unused_puzzle_unsolved):
    """Test sudoku clear callback."""
    mock_bot = AsyncMock(spec=sudoku.view.CBot)
    mock_member = AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(_unused_puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.response = AsyncMock(spec=discord.InteractionResponse)
    await view.clear.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()
    await view.one.callback(mock_interaction)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.clear.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()
    await view.three.callback(mock_interaction)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.clear.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()


def test_puzzle_magic_methods(_unused_puzzle_unsolved, _unused_puzzle_solved):
    """Test sudoku puzzle magic methods."""
    assert isinstance(repr(_unused_puzzle_unsolved), str)
    assert _unused_puzzle_unsolved != _unused_puzzle_solved


def test_puzzle_solution(_unused_puzzle_solved):
    """Test sudoku puzzle solution."""
    _unused_puzzle_solved.blocks[0][1]._value = 9
    _unused_puzzle_solved.blocks[0][2]._value = 0
    with pytest.raises(AttributeError):
        print(_unused_puzzle_solved.solution)


def test_from_rows_and_cols_and_random(_unused_puzzle_unsolved):
    """Test sudoku from rows and cols and random."""
    rows = [sudoku.Row([sudoku.Cell(cell, cell == 0) for cell in row]) for row in _unused_puzzle_unsolved.as_list()]
    cols = [sudoku.Column([row.cells[i] for row in rows]) for i in range(9)]
    rows_puzzle = sudoku.Puzzle.from_rows(rows)
    cols_puzzle = sudoku.Puzzle.from_columns(cols)
    assert rows_puzzle.as_list() == cols_puzzle.as_list() == _unused_puzzle_unsolved.as_list()


def test_generator_function(_unused_puzzle_unsolved):
    """Test sudoku generator function."""
    generator = _unused_puzzle_unsolved.shortSudokuSolve(_board=_unused_puzzle_unsolved.as_list())
    assert next(generator) is not None
    with pytest.raises(StopIteration):
        next(generator)
