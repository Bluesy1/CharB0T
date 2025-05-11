# import datetime
from typing import Literal

import discord
import pytest
from pytest_mock import MockerFixture

from charbot import CBot  # ,constants ,errors
from charbot.programs.cog import Reputation


pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_bot(mocker: MockerFixture):
    """Mock discord.Client."""
    return mocker.AsyncMock(spec=CBot, CHANNEL_ID=CBot.CHANNEL_ID, TIME=CBot.TIME)


@pytest.fixture
def mock_inter(mock_bot, mocker: MockerFixture):
    """Mock discord.Interaction"""
    return mocker.AsyncMock(
        spec=discord.Interaction,
        locale=discord.Locale.american_english,
        user=mocker.AsyncMock(spec=discord.Member),
        response=mocker.AsyncMock(spec=discord.InteractionResponse),
        followup=mocker.AsyncMock(spec=discord.Webhook),
        client=mock_bot,
    )


async def test_sudoku_command_no_puzzle(mock_inter, mocker: MockerFixture):
    """Test that the code for the sudoku command functions as expected when no puzzle is returned."""
    mockedRequest = mocker.AsyncMock(return_value="", spec=Reputation._get_sudoku)
    cog = Reputation()
    cog._get_sudoku = mockedRequest
    await cog.sudoku.callback(cog, mock_inter, False)  # pyright: ignore[reportCallIssue]
    mock_inter.response.defer.assert_awaited_once()
    mockedRequest.assert_awaited_once()
    mock_inter.followup.send.assert_awaited_once_with("Couldn't find a puzzle.")


async def test_sudoku_command_with_puzzle(mock_inter, mocker: MockerFixture):
    """Test that the code for the sudoku command functions as expected when a puzzle is returned."""
    # cspell:disable
    mock_resp = """<INPUT NAME=prefix ID="prefix" TYPE=hidden VALUE="fm8jy"> <INPUT NAME=start TYPE=hidden
VALUE="1666103758"> <INPUT NAME=inchallenge TYPE=hidden VALUE=""> <INPUT NAME=level TYPE=hidden
VALUE="2"> <INPUT NAME=id ID="pid" TYPE=hidden VALUE="864770552"> <INPUT NAME=cheat ID="cheat"
TYPE=hidden VALUE="381642579245973816967158234429537681673481952158296347514829763796315428832764195">
    <INPUT ID="editmask" TYPE=hidden
VALUE="101111110011111000111001111110110010101010101010011011111100111000111110011111101"> <INPUT
NAME=options TYPE=hidden VALUE="2"> <INPUT NAME=errors TYPE=hidden VALUE="0" ID="errors"> <INPUT
NAME=layout TYPE=hidden VALUE="">"""
    # cspell:enable
    mockedRequest = mocker.AsyncMock(return_value=mock_resp, spec=Reputation._get_sudoku)
    cog = Reputation()
    cog._get_sudoku = mockedRequest
    await cog.sudoku.callback(cog, mock_inter, False)  # pyright: ignore[reportCallIssue]
    mockedRequest.assert_awaited_once()
    mock_inter.response.defer.assert_awaited_once()
    mock_inter.followup.send.assert_awaited_once()
    _, kwargs = mock_inter.followup.send.await_args
    assert "embed" in kwargs, "Expected an embed to be sent."
    assert "view" in kwargs, "Expected a view to be sent."


async def test_tictactoe_command(mock_inter, mocker: MockerFixture):
    """Test that the code for the tictactoe command functions as expected."""
    cog = Reputation()
    await cog.tictactoe.callback(cog, mock_inter, 1)  # pyright: ignore[reportCallIssue,reportArgumentType]
    mock_inter.response.defer.assert_awaited_once()
    mock_inter.followup.send.assert_awaited_once()
    _, kwargs = mock_inter.followup.send.await_args
    assert "embed" in kwargs, "Expected an embed to be sent."
    assert kwargs["embed"].image.url == "attachment://tictactoe.png", "Expected an attachment reference to be sent."
    assert "view" in kwargs, "Expected a view to be sent."
    assert "file" in kwargs, "Expected a file to be sent."


async def test_shrugman_command(mock_bot, mocker: MockerFixture):
    """Test that the code for the shrugman command functions as expected"""
    cog = Reputation()
    mock_interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        user=mocker.AsyncMock(spec=discord.Member),
        response=mocker.AsyncMock(spec=discord.InteractionResponse),
        followup=mocker.AsyncMock(spec=discord.Webhook),
        client=mock_bot,
    )
    await cog.shrugman.callback(cog, mock_interaction)  # pyright: ignore[reportCallIssue]
    mock_interaction.response.defer.assert_awaited_once()
    mock_interaction.followup.send.assert_awaited_once()
    _, kwargs = mock_interaction.followup.send.await_args
    assert "embed" in kwargs, "Expected an embed to be sent."
    assert "view" in kwargs, "Expected a view to be sent."


@pytest.mark.parametrize("difficulty", ["Beginner", "Intermediate", "Expert", "Super Expert"])
async def test_minesweeper_command(
    mock_inter, difficulty: Literal["Beginner", "Intermediate", "Expert", "Super Expert"]
):
    """Test that the code for the minesweeper command functions as expected."""
    cog = Reputation()
    await cog.minesweeper.callback(cog, mock_inter, difficulty)  # pyright: ignore[reportCallIssue]
    mock_inter.response.defer.assert_awaited_once()
    mock_inter.followup.send.assert_awaited_once()
    _, kwargs = mock_inter.followup.send.await_args
    assert "embed" in kwargs, "Expected an embed to be sent."
    assert kwargs["embed"].image.url == "attachment://minesweeper.png", "Expected an attachment reference to be sent."
    assert "view" in kwargs, "Expected a view to be sent."
    assert "file" in kwargs, "Expected a file to be sent."
