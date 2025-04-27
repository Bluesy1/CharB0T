import pathlib
import random
import sys
from typing import Any

import discord
import pytest
from discord import Interaction
from PIL import Image
from pytest_mock import MockerFixture

from charbot import CBot
from charbot.programs import minesweeper
from charbot.programs._minesweeper.game import Cell, ChordResult, Game, RevealResult


@pytest.fixture
def game() -> Game:
    return Game(5, 1, (0, 0), (0, 0))


@pytest.fixture
def inter(mocker: MockerFixture):
    return mocker.AsyncMock(
        spec=Interaction[CBot],
        client=mocker.AsyncMock(spec=CBot),
        response=mocker.AsyncMock(spec=discord.InteractionResponse),
        edit_original_response=mocker.AsyncMock(),
        locale=discord.Locale.american_english,
    )


@pytest.mark.asyncio
async def test_minesweeper_init(game: Game):
    view = minesweeper.Minesweeper(game)
    assert view.game == game, "Game should be set to the passed game"
    assert len(view.row.options) == 5, "Row should have the number of rows as the game does, which is 5"
    assert len(view.column.options) == 5, "Col should have the number of cols as the game does, which is 5"


@pytest.mark.asyncio
async def test_minesweeper_draw(game: Game):
    view = minesweeper.Minesweeper(game)
    file = await view.draw("Minesweeper Board")
    assert isinstance(file, discord.File), "File should be a discord.File"
    assert file.filename == "minesweeper.png", "File should have the filename minesweeper.png"
    assert file.description == "Minesweeper Board", "File should have the description Minesweeper board"
    assert not file.spoiler, "File should not be marked as a spoiler"


@pytest.mark.asyncio
async def test_handle_lose(game: Game, inter):
    view = minesweeper.Minesweeper(game)
    await view.handle_lose(inter)
    inter.response.defer.assert_awaited_once_with(ephemeral=True)
    inter.edit_original_response.assert_awaited_once()
    kwargs: dict[str, Any] = inter.edit_original_response.await_args.kwargs
    embed: discord.Embed = kwargs["embed"]
    assert embed.image.url == "attachment://minesweeper.png", "Image should be a reference to the attachment"
    assert kwargs["view"] is None, "View should be None"
    assert view.is_finished(), "Game should be finished"
    assert "attachments" in kwargs, "Attachments should be in the kwargs"
    assert len(kwargs["attachments"]) == 1, "Attachments should have one element"
    assert len(kwargs) == 3, "Kwargs should have three elements"


@pytest.mark.asyncio
async def test_handle_win(game: Game, inter):
    view = minesweeper.Minesweeper(game)
    await view.handle_win(inter)
    inter.response.defer.assert_awaited_once_with(ephemeral=True)
    inter.edit_original_response.assert_awaited_once()
    kwargs: dict[str, Any] = inter.edit_original_response.await_args.kwargs
    embed: discord.Embed = kwargs["embed"]
    assert embed.image.url == "attachment://minesweeper.png", "Image should be a reference to the attachment"
    assert kwargs["view"] is None, "View should be None"
    assert view.is_finished(), "Game should be finished"
    assert "attachments" in kwargs, "Attachments should be in the kwargs"
    assert len(kwargs["attachments"]) == 1, "Attachments should have one element"
    assert len(kwargs) == 3, "Kwargs should have three elements"


@pytest.mark.asyncio
async def test_row(game: Game, inter):
    view = minesweeper.Minesweeper(game)
    view.row._refresh_state(inter, {"custom_id": "a", "component_type": 3, "values": ["0"]})
    await view.row.callback(inter)
    inter.response.edit_message.assert_awaited_once()
    kwargs: dict[str, Any] = inter.response.edit_message.await_args.kwargs
    assert game.y == 0, "Game x should be 0"
    assert "attachments" in kwargs, "Attachments should be in the kwargs"
    assert len(kwargs["attachments"]) == 1, "Attachments should have one element"
    assert len(kwargs) == 2, "Kwargs should have two elements"


@pytest.mark.asyncio
async def test_column(game: Game, inter):
    view = minesweeper.Minesweeper(game)
    view.column._refresh_state(inter, {"custom_id": "a", "component_type": 3, "values": ["0"]})
    await view.column.callback(inter)
    inter.response.edit_message.assert_awaited_once()
    kwargs: dict[str, Any] = inter.response.edit_message.await_args.kwargs
    assert game.x == 0, "Game x should be 0"
    assert "attachments" in kwargs, "Attachments should be in the kwargs"
    assert len(kwargs["attachments"]) == 1, "Attachments should have one element"
    assert len(kwargs) == 2, "Kwargs should have two elements"


@pytest.mark.asyncio
async def test_reveal_success(game, inter, mocker: MockerFixture):
    mock_game = mocker.Mock(spec=Game)
    mock_game.height = 5
    mock_game.width = 5
    mock_game.draw.return_value = game.draw()
    mock_game.reveal.return_value = RevealResult.Empty
    mock_game.is_win = lambda: False
    view = minesweeper.Minesweeper(mock_game)
    await view.reveal.callback(inter)
    inter.response.edit_message.assert_awaited_once()
    kwargs: dict[str, Any] = inter.response.edit_message.await_args.kwargs
    assert "attachments" in kwargs, "Attachments should be in the kwargs"
    assert len(kwargs["attachments"]) == 1, "Attachments should have one element"
    assert len(kwargs) == 2, "Kwargs should have two elements"


@pytest.mark.asyncio
async def test_reveal_fail(game, inter, mocker: MockerFixture):
    inter.followup = mocker.AsyncMock(spec=discord.Webhook)
    mock_game = mocker.Mock(spec=Game, height=5, width=5, is_win=lambda: False)
    mock_game.draw.return_value = game.draw()
    mock_game.reveal.return_value = RevealResult.Flagged
    view = minesweeper.Minesweeper(mock_game)
    await view.reveal.callback(inter)
    inter.response.edit_message.assert_awaited_once()
    kwargs: dict[str, Any] = inter.response.edit_message.await_args.kwargs
    assert "attachments" in kwargs, "Attachments should be in the kwargs"
    assert len(kwargs["attachments"]) == 1, "Attachments should have one element"
    assert len(kwargs) == 2, "Kwargs should have two elements"
    inter.followup.send.assert_awaited_once()
    assert inter.followup.send.await_args.kwargs["ephemeral"], "Ephemeral should be set as true"


@pytest.mark.asyncio
async def test_reveal_win(game, inter, mocker: MockerFixture):
    mock_game = mocker.Mock(spec=Game)
    mock_game.height = 5
    mock_game.width = 5
    mock_game.reveal.return_value = RevealResult.Empty
    mock_game.is_win = lambda: True
    mock_win = mocker.AsyncMock()
    view = minesweeper.Minesweeper(mock_game)
    view.handle_win = mock_win
    await view.reveal.callback(inter)
    mock_win.assert_awaited_once()


@pytest.mark.asyncio
async def test_reveal_lose(game, inter, mocker: MockerFixture):
    mock_game = mocker.Mock(spec=Game)
    mock_game.height = 5
    mock_game.width = 5
    mock_game.reveal.return_value = RevealResult.Mine
    mock_lose = mocker.AsyncMock()
    view = minesweeper.Minesweeper(mock_game)
    view.handle_lose = mock_lose
    await view.reveal.callback(inter)
    mock_lose.assert_awaited_once()


@pytest.mark.asyncio
async def test_chord_failure(game, inter, mocker: MockerFixture):
    mock_game = mocker.Mock(spec=Game)
    mock_game.height = 5
    mock_game.width = 5
    mock_game.chord.return_value = ChordResult.Failed
    view = minesweeper.Minesweeper(mock_game)
    await view.chord.callback(inter)
    inter.response.send_message.assert_awaited_once()
    assert inter.response.send_message.await_args.kwargs["ephemeral"], "Ephemeral should be set as true"


@pytest.mark.asyncio
async def test_chord_success_no_win(game, inter, mocker: MockerFixture):
    mock_game = mocker.Mock(spec=Game)
    mock_game.height = 5
    mock_game.width = 5
    mock_game.draw.return_value = game.draw()
    mock_game.chord.return_value = ChordResult.Success
    mock_game.is_win = lambda: False
    view = minesweeper.Minesweeper(mock_game)
    await view.chord.callback(inter)
    inter.response.edit_message.assert_awaited_once()
    kwargs: dict[str, Any] = inter.response.edit_message.await_args.kwargs
    assert "attachments" in kwargs, "Attachments should be in the kwargs"
    assert len(kwargs["attachments"]) == 1, "Attachments should have one element"
    assert len(kwargs) == 2, "Kwargs should have two elements"


@pytest.mark.asyncio
async def test_chord_success_win(game, inter, mocker: MockerFixture):
    mock_game = mocker.Mock(spec=Game)
    mock_game.height = 5
    mock_game.width = 5
    mock_game.draw.return_value = game.draw()
    mock_game.chord.return_value = ChordResult.Success
    mock_game.is_win = lambda: True
    mock_win = mocker.AsyncMock()
    view = minesweeper.Minesweeper(mock_game)
    view.handle_win = mock_win
    await view.chord.callback(inter)
    mock_win.assert_awaited_once()


@pytest.mark.asyncio
async def test_chord_death(game, inter, mocker: MockerFixture):
    mock_game = mocker.Mock(spec=Game)
    mock_game.height = 5
    mock_game.width = 5
    mock_game.draw.return_value = game.draw()
    mock_game.chord.return_value = ChordResult.Death
    mock_lose = mocker.AsyncMock()
    view = minesweeper.Minesweeper(mock_game)
    view.handle_lose = mock_lose
    await view.chord.callback(inter)
    mock_lose.assert_awaited_once()


@pytest.mark.asyncio
async def test_flag(game, inter):
    view = minesweeper.Minesweeper(game)
    await view.flag.callback(inter)
    inter.response.edit_message.assert_awaited_once()
    kwargs: dict[str, Any] = inter.response.edit_message.await_args.kwargs
    assert len(kwargs["attachments"]) == 1, "Attachments should have one element"
    assert len(kwargs) == 2, "Kwargs should have two elements"


@pytest.mark.asyncio
async def test_quit(game, inter):
    view = minesweeper.Minesweeper(game)
    await view.quit.callback(inter)
    inter.response.edit_message.assert_awaited_once()
    kwargs: dict[str, Any] = inter.response.edit_message.await_args.kwargs
    embed: discord.Embed = kwargs["embed"]
    assert embed.image.url == "attachment://minesweeper.png", "Image should be a reference to the attachment"
    assert kwargs["view"] is None, "View should be None"
    assert view.is_finished(), "Game should be finished"
    assert "attachments" in kwargs, "Attachments should be in the kwargs"
    assert len(kwargs["attachments"]) == 1, "Attachments should have one element"
    assert len(kwargs) == 3, "Kwargs should have three elements"


@pytest.mark.asyncio
async def test_help(game, inter, mocker: MockerFixture):
    inter.followup = mocker.AsyncMock(spec=discord.Webhook)
    view = minesweeper.Minesweeper(game)
    await view.help.callback(inter)
    inter.response.defer.assert_awaited_once_with(ephemeral=True, thinking=True)
    inter.followup.send.assert_awaited_once()
    kwargs = inter.followup.send.await_args.kwargs
    assert "embed" in kwargs, "Embed should be in the kwargs"
    assert len(kwargs) == 2, "Kwargs should have two elements"
    file: discord.File = kwargs["file"]
    assert file._filename == "help.gif", "File name should be help.gif"


def test_cell_revealed_setter():
    cell = Cell()
    assert cell.revealed is False
    cell.revealed = True
    assert cell.revealed is True
    with pytest.raises(TypeError, match="Expected bool, got <class 'int'> instead!"):
        cell.revealed = 1  # pyright: ignore[reportAttributeAccessIssue]


def test_cell_marked_setter():
    cell = Cell()
    assert cell.marked is False
    cell.marked = True
    assert cell.marked is True
    with pytest.raises(TypeError, match="Expected bool, got <class 'int'> instead!"):
        cell.marked = 1  # pyright: ignore[reportAttributeAccessIssue]


@pytest.mark.xfail(sys.platform == "win32", reason="PIL not consistent between platforms due to various reasons")
def test_board_draw(monkeypatch):
    rand = random.Random(1234567890)
    monkeypatch.setattr(random, "shuffle", rand.shuffle)
    game = Game.beginner()
    assert game.reveal() is RevealResult.Empty
    game.reset()
    game.draw()
    with (
        Image.open(game.draw()) as got,
        Image.open(pathlib.Path(__file__).parent / "media/test_minesweeper_draw.png") as expected,
    ):
        assert got == expected, "Got unexpected banner"


@pytest.mark.xfail(sys.platform == "win32", reason="PIL not consistent between platforms due to various reasons")
def test_board_draw_after_fail(monkeypatch):
    rand = random.Random(1234567890)
    monkeypatch.setattr(random, "shuffle", rand.shuffle)
    game = Game.beginner()
    assert game.reveal() is RevealResult.Empty
    game.change_row(game.selected_row - 2)
    game.change_col(game.selected_col + 1)
    assert game.toggle_flag() is True
    game.change_row(game.selected_row - 1)
    game.change_col(game.selected_col + 1)
    assert game.reveal() == RevealResult.Mine
    assert game.is_win() is False
    with (
        Image.open(game.draw()) as got,
        Image.open(pathlib.Path(__file__).parent / "media/test_minesweeper_draw_after_fail.png") as expected,
    ):
        assert got == expected, "Got unexpected banner"
