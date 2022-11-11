# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import Any

import discord
import pytest
from pytest_mock import MockerFixture

from charbot import CBot, GuildComponentInteraction as Interaction
from charbot.programs import minesweeper
from charbot_rust.minesweeper import Game, RevealResult, ChordResult  # pyright: ignore[reportGeneralTypeIssues]


@pytest.fixture()
def game() -> Game:
    return Game(5, 5, 1)


@pytest.fixture()
def inter(mocker: MockerFixture):
    return mocker.AsyncMock(
        spec=Interaction[CBot],
        client=mocker.AsyncMock(spec=CBot),
        response=mocker.AsyncMock(spec=discord.InteractionResponse),
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
