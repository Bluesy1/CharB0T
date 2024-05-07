import copy
import datetime

import discord
import pytest
from pytest_mock import MockerFixture

from charbot import CBot
from charbot.programs import sudoku


@pytest.fixture()
def puzzle_unsolved() -> sudoku.Puzzle:
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


@pytest.fixture()
def puzzle_solved() -> sudoku.Puzzle:
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


@pytest.mark.asyncio()
async def test_view_init(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku view init."""
    mock_bot = mocker.Mock(spec=CBot)
    mock_member = mocker.Mock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    assert view.bot is mock_bot
    assert view.puzzle is puzzle_unsolved
    assert view.author is mock_member


@pytest.mark.asyncio()
async def test_view_keypad_callback_enter_block(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku view update keypad."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_button = mocker.Mock(spec=discord.Button)
    await view.keypad_callback(mock_interaction, mock_button, 0)
    mock_interaction.response.defer.assert_called_once_with(ephemeral=True)
    assert view.block is puzzle_unsolved.blocks[0]
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
    mock_interaction.edit_original_response.assert_called_once()


@pytest.mark.asyncio()
async def test_view_keypad_callback_enter_cell(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku view update keypad."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_button = mocker.Mock(spec=discord.Button)
    await view.keypad_callback(mock_interaction, mock_button, 0)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.keypad_callback(mock_interaction, mock_button, 2)
    assert view.cell is puzzle_unsolved.blocks[0][2]
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
    mock_interaction.edit_original_response.assert_called_once()


@pytest.mark.asyncio()
async def test_view_keypad_callback_set_cell_value(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku view update keypad."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_button = mocker.Mock(spec=discord.Button)
    mock_button.label = "9"
    await view.keypad_callback(mock_interaction, mock_button, 0)
    await view.keypad_callback(mock_interaction, mock_button, 2)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.keypad_callback(mock_interaction, mock_button, 9)
    assert view.cell is discord.utils.MISSING
    assert view.puzzle.blocks[0][2].value == 9
    assert not view.puzzle.is_solved
    assert view.block is puzzle_unsolved.blocks[0]
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
    assert view.block is puzzle_unsolved.blocks[0]
    mock_interaction.edit_original_response.assert_called_once()


@pytest.mark.asyncio()
async def test_view_keypad_callback_remove_possible_cell_value(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku view update keypad."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    view.noting_mode = True
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_button = mocker.Mock(spec=discord.Button)
    mock_button.label = "9"
    await view.keypad_callback(mock_interaction, mock_button, 0)
    await view.keypad_callback(mock_interaction, mock_button, 2)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    with pytest.raises(NotImplementedError):
        await view.keypad_callback(mock_interaction, mock_button, 9)


@pytest.mark.asyncio()
async def test_view_keypad_callback_add_possible_cell_value(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku view update keypad."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    view.noting_mode = True
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_button = mocker.Mock(spec=discord.Button)
    mock_button.label = "9"
    await view.keypad_callback(mock_interaction, mock_button, 0)
    await view.keypad_callback(mock_interaction, mock_button, 2)
    view.cell.possible_values.remove(9)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    with pytest.raises(NotImplementedError):
        await view.keypad_callback(mock_interaction, mock_button, 9)


@pytest.mark.asyncio()
async def test_view_keypad_callback_try_set_static_cell(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku view update keypad."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_button = mocker.Mock(spec=discord.Button)
    await view.keypad_callback(mock_interaction, mock_button, 0)
    await view.keypad_callback(mock_interaction, mock_button, 1)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.keypad_callback(mock_interaction, mock_button, 2)
    mock_interaction.edit_original_response.assert_called_once()
    assert view.cell is discord.utils.MISSING
    assert view.block.selected


@pytest.mark.asyncio()
async def test_view_update_keypad_puzzle_level(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku view update keypad."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
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


@pytest.mark.asyncio()
async def test_view_block_choose_embed(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku view block choose embed."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    embed = view.block_choose_embed()
    assert embed.title == "Sudoku"
    assert embed.footer.text == "Start playing by typing /programs sudoku"
    assert embed.color == discord.Color.blurple()


@pytest.mark.asyncio()
async def test_view_on_win(puzzle_solved, mocker: MockerFixture, database):
    """Test Sudoku view on win."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_bot.pool = database
    mock_member = mocker.AsyncMock(spec=discord.Member)
    mock_member.id = 1
    puzzle_solved.blocks[0][0]._editable = True
    puzzle_solved.blocks[0][0].value = 0
    view = sudoku.Sudoku(puzzle_solved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.user = mock_member
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_button = mocker.AsyncMock(spec=discord.Button)
    mock_button.label = "7"
    await view.keypad_callback(mock_interaction, mock_button, 0)
    await view.keypad_callback(mock_interaction, mock_button, 0)
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.keypad_callback(mock_interaction, mock_button, 7)
    mock_interaction.edit_original_response.assert_called_once()
    assert view.is_finished()


@pytest.mark.asyncio()
async def test_view_back_button_callback(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku view back button callback."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    view.back.disabled = False
    await view.back.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()
    assert view.back.disabled
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    view.block = puzzle_unsolved.blocks[0]
    view.level = "Block"
    view.block.selected = True
    view.update_keypad()
    await view.back.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()
    assert view.back.disabled
    assert view.level == "Puzzle"
    assert view.block is discord.utils.MISSING
    assert not puzzle_unsolved.blocks[0].selected
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    view.block = puzzle_unsolved.blocks[0]
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


@pytest.mark.asyncio()
async def test_one_button_callback(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku one button callback."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.one.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_response.assert_called_once()


@pytest.mark.asyncio()
async def test_two_button_callback(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku two button callback."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.two.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_response.assert_called_once()


@pytest.mark.asyncio()
async def test_three_button_callback(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku three button callback."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.three.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_response.assert_called_once()


@pytest.mark.asyncio()
async def test_four_button_callback(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku four button callback."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.four.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_response.assert_called_once()


@pytest.mark.asyncio()
async def test_five_button_callback(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku five button callback."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.five.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_response.assert_called_once()


@pytest.mark.asyncio()
async def test_six_button_callback(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku six button callback."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.six.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_response.assert_called_once()


@pytest.mark.asyncio()
async def test_seven_button_callback(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku seven button callback."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.seven.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_response.assert_called_once()


@pytest.mark.asyncio()
async def test_eight_button_callback(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku eight button callback."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.eight.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_response.assert_called_once()


@pytest.mark.asyncio()
async def test_nine_button_callback(puzzle_unsolved, mocker: MockerFixture):
    """Test Sudoku nine button callback."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.nine.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.edit_original_response.assert_called_once()


@pytest.mark.asyncio()
async def test_mode_select(puzzle_unsolved, mocker: MockerFixture):
    """Test sudoku mode select."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    with pytest.raises(NotImplementedError):
        await view.mode.callback(mock_interaction)


@pytest.mark.asyncio()
async def test_cancel_callback(puzzle_unsolved, mocker: MockerFixture):
    """Test sudoku cancel callback."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    await view.cancel.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    view.start_time = discord.utils.utcnow() - datetime.timedelta(minutes=5)
    view.moves = 20
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.cancel.callback(mock_interaction)
    mock_interaction.response.edit_message.assert_called_once()


@pytest.mark.asyncio()
async def test_clear_callback(puzzle_unsolved, mocker: MockerFixture):
    """Test sudoku clear callback."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_member = mocker.AsyncMock(spec=discord.Member)
    view = sudoku.Sudoku(puzzle_unsolved, mock_member, mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
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


def test_puzzle_magic_methods(puzzle_unsolved, puzzle_solved):
    """Test sudoku puzzle magic methods."""
    assert isinstance(repr(puzzle_unsolved), str)
    assert puzzle_unsolved != puzzle_solved


def test_puzzle_solution(puzzle_solved):
    """Test sudoku puzzle solution."""
    puzzle_solved.blocks[0][1]._value = 9
    puzzle_solved.blocks[0][2]._value = 0
    with pytest.raises(AttributeError):
        print(puzzle_solved.solution)


def test_from_rows_and_cols_and_random(puzzle_unsolved):
    """Test sudoku from rows and cols and random."""
    rows = [sudoku.Row([sudoku.Cell(cell, cell == 0) for cell in row]) for row in puzzle_unsolved.as_list()]
    cols = [sudoku.Column([row.cells[i] for row in rows]) for i in range(9)]
    rows_puzzle = sudoku.Puzzle.from_rows(rows)
    cols_puzzle = sudoku.Puzzle.from_columns(cols)
    assert rows_puzzle.as_list() == cols_puzzle.as_list() == puzzle_unsolved.as_list()


def test_generator_function(puzzle_unsolved):
    """Test sudoku generator function."""
    generator = puzzle_unsolved.short_sudoku_solve(_board=puzzle_unsolved.as_list())
    assert next(generator, None) is not None
    assert next(generator, None) is None


def test_cell_location(puzzle_unsolved):
    """Test sudoku cell location."""
    assert puzzle_unsolved.location_of_cell(puzzle_unsolved.blocks[0][0]) == "row 1, column 1"
    test_cell = sudoku.Cell(0, True)
    with pytest.raises(ValueError, match="Cell not found in puzzle"):
        puzzle_unsolved.location_of_cell(test_cell)
    with pytest.raises(TypeError):
        puzzle_unsolved.location_of_cell("This is not a cell")  # skipcq


def test_row_of_cell(puzzle_unsolved):
    """Test sudoku row of cell."""
    assert puzzle_unsolved.row_of_cell(puzzle_unsolved.blocks[0][0]) is puzzle_unsolved.rows[0]
    test_cell = sudoku.Cell(0, True)
    with pytest.raises(ValueError, match="Cell not found in puzzle"):
        puzzle_unsolved.row_of_cell(test_cell)
    with pytest.raises(TypeError):
        puzzle_unsolved.row_of_cell("This is not a cell")  # skipcq


def test_column_of_cell(puzzle_unsolved):
    """Test sudoku column of cell."""
    assert puzzle_unsolved.column_of_cell(puzzle_unsolved.blocks[0][0]) is puzzle_unsolved.columns[0]
    test_cell = sudoku.Cell(0, True)
    with pytest.raises(ValueError, match="Cell not found in puzzle"):
        puzzle_unsolved.column_of_cell(test_cell)
    with pytest.raises(TypeError):
        puzzle_unsolved.column_of_cell("This is not a cell")  # skipcq


def test_block_of_cell(puzzle_unsolved):
    """Test sudoku block of cell."""
    assert puzzle_unsolved.block_of_cell(puzzle_unsolved.blocks[0][0]) is puzzle_unsolved.blocks[0]
    test_cell = sudoku.Cell(1, True)
    test_cell._value = 10
    with pytest.raises(ValueError, match="Cell not found in puzzle"):
        puzzle_unsolved.block_of_cell(test_cell)
    with pytest.raises(TypeError):
        puzzle_unsolved.block_of_cell("This is not a cell")  # skipcq


def test_block_index(puzzle_unsolved):
    """Test sudoku block index."""
    assert puzzle_unsolved.block_index(puzzle_unsolved.blocks[0]) == 0
    test_cell = sudoku.Block([sudoku.Cell(0, True) for _ in range(9)])
    with pytest.raises(ValueError, match="Block not found in puzzle"):
        puzzle_unsolved.block_index(test_cell)
    with pytest.raises(TypeError):
        puzzle_unsolved.block_index("This is not a block")  # skipcq


def test_row_init():
    """Test row validation"""
    with pytest.raises(ValueError, match="Row must have exactly 9 cells."):
        sudoku.Row([sudoku.Cell(0, True) for _ in range(10)])


@pytest.mark.parametrize(("editable", "expected"), [(True, 0), (False, 1)])
def test_row_clear(editable: bool, expected: int):
    """Test row clear"""
    row = sudoku.Row([sudoku.Cell(1, editable) for _ in range(9)])
    row_copy = copy.deepcopy(row)
    assert row == row_copy
    row.clear()
    for cell in row.cells:
        assert cell.value == expected


def test_column_init():
    """Test column validation"""
    with pytest.raises(ValueError, match="Column must have exactly 9 cells."):
        sudoku.Column([sudoku.Cell(0, True) for _ in range(10)])


@pytest.mark.parametrize(("editable", "expected"), [(True, 0), (False, 1)])
def test_column_clear(editable: bool, expected: int):
    """Test column clear"""
    col = sudoku.Column([sudoku.Cell(1, editable) for _ in range(9)])
    col_copy = copy.deepcopy(col)
    assert col == col_copy
    assert col[0].value == 1
    col.clear()
    for cell in col.cells:
        assert cell.value == expected


def test_block_init():
    """Test block validation"""
    with pytest.raises(ValueError, match="Block must have exactly 9 cells."):
        sudoku.Block([sudoku.Cell(0, True) for _ in range(10)])


def test_block_compare():
    """Test block compare"""
    block = sudoku.Block([sudoku.Cell(1, True) for _ in range(9)])
    block_copy = copy.deepcopy(block)
    assert block == block_copy
    assert block != sudoku.Block([sudoku.Cell(1, True) for _ in range(9)])


def test_block_select_toggle():
    """Test block select toggle"""
    block = sudoku.Block([sudoku.Cell(1, True) for _ in range(9)])
    with pytest.raises(TypeError):
        block.selected = "This is not a boolean"  # type: ignore  # skipcq


def test_cell_validation():
    """Test cell validation"""
    with pytest.raises(ValueError, match="Value must be between 0 and 9."):
        sudoku.Cell(10, True)


def test_cell_hash():
    """Test cell hash"""
    cell = sudoku.Cell(1, True)
    assert hash(cell) == hash(f"{cell.value}{cell.editable}")


def test_cell_validate_value_not_editable():
    """Test cell validate value not editable"""
    cell = sudoku.Cell(1, False)
    with pytest.raises(ValueError, match="Cannot set value of non-editable cell."):
        cell.value = 2


def test_cell_validate_value_editable():
    """Test cell validate value editable"""
    cell = sudoku.Cell(1, True)
    with pytest.raises(ValueError, match="Value must be between 0 and 9."):
        cell.value = 10


def test_possible_value_not_editable():
    """Test possible value not editable"""
    cell = sudoku.Cell(1, False)
    with pytest.raises(ValueError, match="Cannot set possible values of non-editable cell."):
        cell.possible_values = {2}


def test_cell_selected_state():
    """Test cell selected state"""
    cell = sudoku.Cell(1, True)
    with pytest.raises(TypeError, match="Selected must be a bool."):
        cell.selected = "This is not a boolean"  # type: ignore  # skipcq


def test_cell_validate_clear():
    """Test cell validate clear"""
    cell = sudoku.Cell(1, False)
    with pytest.raises(ValueError, match="Cannot clear non-editable cell."):
        cell.clear()
