# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
import aiohttp
import discord
import pytest
from aioresponses import aioresponses
from asyncpg import Pool
from pytest_mock import MockerFixture

from charbot import CBot
from charbot import errors
from charbot.programs.cog import Reputation

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_bot(mocker: MockerFixture):
    """Mock discord.Client."""
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_bot.CHANNEL_ID = CBot.CHANNEL_ID
    mock_bot.ALLOWED_ROLES = CBot.ALLOWED_ROLES
    return mock_bot


async def test_interaction_check_no_guild(mock_bot, mocker: MockerFixture):
    """Test the interaction check when the interaction is not in a guild."""
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.guild = None
    cog = Reputation(mock_bot)
    with pytest.raises(discord.app_commands.NoPrivateMessage) as exc:
        await cog.interaction_check(mock_interaction)
    assert exc.value.args[0] == "Programs can't be used in direct messages."


async def test_interaction_check_wrong_guild(mock_bot, mocker: MockerFixture):
    """Test the interaction check when the interaction is in the wrong guild."""
    cog = Reputation(mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.guild = mocker.AsyncMock(spec=discord.Guild)
    mock_interaction.guild.id = 0
    with pytest.raises(discord.app_commands.NoPrivateMessage) as exc:
        await cog.interaction_check(mock_interaction)
    assert exc.value.args[0] == "Programs can't be used in this server."


async def test_interaction_check_wrong_channel(mock_bot, mocker: MockerFixture):
    """Test the interaction check when the interaction is in the wrong channel."""
    cog = Reputation(mock_bot)
    mock_interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        locale=discord.Locale.american_english,
        channel=mocker.AsyncMock(spec=discord.TextChannel, id=0),
        guild=mocker.AsyncMock(spec=discord.Guild, id=225345178955808768),
    )
    with pytest.raises(errors.WrongChannelError) as exc:
        await cog.interaction_check(mock_interaction)
    assert exc.value._channel == 969972085445238784
    assert (
        str(exc.value).encode("ascii", "ignore").decode()
        == "This command can only be run in the channel <#969972085445238784> ."
    )


async def test_interaction_check_no_allowed_roles(mock_bot, mocker: MockerFixture):
    """Test the interaction check when the interaction is in the wrong channel."""
    cog = Reputation(mock_bot)
    mock_interaction = mocker.AsyncMock(
        spec=discord.Interaction,
        locale=discord.Locale.american_english,
        channel=mocker.AsyncMock(spec=discord.TextChannel, id=969972085445238784),
        guild=mocker.AsyncMock(spec=discord.Guild, id=225345178955808768),
    )
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    with pytest.raises(errors.MissingProgramRole) as exc:
        await cog.interaction_check(mock_interaction)
    assert (
        exc.value.args[0].encode("ascii", "ignore").decode()
        == "You are missing at least one of the required roles: '337743478190637077', '685331877057658888', "
        "'969629622453039104', '969629628249563166', '969629632028614699', '969628342733119518', "
        "'969627321239760967', or '969626979353632790'"
    )
    assert exc.value.missing_roles == [
        337743478190637077,
        685331877057658888,
        969629622453039104,
        969629628249563166,
        969629632028614699,
        969628342733119518,
        969627321239760967,
        969626979353632790,
    ]
    assert str(exc.value).encode("ascii", "ignore").decode() == (
        "You are missing at least one of the required roles: '337743478190637077', '685331877057658888', "
        "'969629622453039104', '969629628249563166', '969629632028614699', '969628342733119518', '969627321239760967', "
        "or '969626979353632790' - you must be at least level 1 to use this command/button."
    )


async def test_interaction_check_allowed(mock_bot, mocker: MockerFixture):
    """Test the interaction check when the interaction is in the right channel and guild."""
    cog = Reputation(mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.guild = mocker.AsyncMock(spec=discord.Guild)
    mock_interaction.guild.id = 225345178955808768
    mock_interaction.channel = mocker.AsyncMock(spec=discord.TextChannel)
    mock_interaction.channel.id = 969972085445238784
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.user.roles = [
        discord.Object(id=337743478190637077),
        discord.Object(id=685331877057658888),
    ]
    assert await cog.interaction_check(mock_interaction)


async def test_sudoku_command_no_puzzle(mock_bot, mocker: MockerFixture):
    """Test that the code for the sudoku command functions as expected when no puzzle is returned."""
    with aioresponses() as mocked:
        async with aiohttp.ClientSession() as session:
            mocked.get(
                "https://nine.websudoku.com/?level=2", status=200, content_type="text/html; charset=UTF-8", body=b""
            )
            cog = Reputation(mock_bot)
            mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
            mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
            mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
            mock_interaction.followup = mocker.AsyncMock(spec=discord.Webhook)
            mock_interaction.client = mock_bot
            mock_interaction.client.session = session
            await cog.sudoku.callback(cog, mock_interaction, False)  # pyright: ignore[reportGeneralTypeIssues]
            mock_interaction.response.defer.assert_awaited_once()
            mock_interaction.followup.send.assert_awaited_once_with("Couldn't find a puzzle.")


async def test_sudoku_command_with_puzzle(mock_bot, mocker: MockerFixture):
    """Test that the code for the sudoku command functions as expected when a puzzle is returned."""
    with aioresponses() as mocked:
        async with aiohttp.ClientSession() as session:
            # noinspection SpellCheckingInspection
            mocked.get(
                "https://nine.websudoku.com/?level=2",
                status=200,
                content_type="text/html; charset=UTF-8",
                body=b"""<INPUT NAME=prefix ID="prefix" TYPE=hidden VALUE="fm8jy"> <INPUT NAME=start TYPE=hidden
                VALUE="1666103758"> <INPUT NAME=inchallenge TYPE=hidden VALUE=""> <INPUT NAME=level TYPE=hidden
                VALUE="2"> <INPUT NAME=id ID="pid" TYPE=hidden VALUE="864770552"> <INPUT NAME=cheat ID="cheat"
                TYPE=hidden VALUE="381642579245973816967158234429537681673481952158296347514829763796315428832764195">
                 <INPUT ID="editmask" TYPE=hidden
                VALUE="101111110011111000111001111110110010101010101010011011111100111000111110011111101"> <INPUT
                NAME=options TYPE=hidden VALUE="2"> <INPUT NAME=errors TYPE=hidden VALUE="0" ID="errors"> <INPUT
                NAME=layout TYPE=hidden VALUE=""> """,
            )
            cog = Reputation(mock_bot)
            mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
            mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
            mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
            mock_interaction.followup = mocker.AsyncMock(spec=discord.Webhook)
            mock_interaction.client = mock_bot
            mock_interaction.client.session = session
            await cog.sudoku.callback(cog, mock_interaction, False)  # pyright: ignore[reportGeneralTypeIssues]
            mock_interaction.response.defer.assert_awaited_once()
            mock_interaction.followup.send.assert_awaited_once()
            _, kwargs = mock_interaction.followup.send.await_args
            assert "embed" in kwargs, "Expected an embed to be sent."
            assert "view" in kwargs, "Expected a view to be sent."


async def test_tictactoe_command(mock_bot, mocker: MockerFixture):
    """Test that the code for the tictactoe command functions as expected."""
    cog = Reputation(mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.followup = mocker.AsyncMock(spec=discord.Webhook)
    mock_interaction.client = mock_bot
    await cog.tictactoe.callback(cog, mock_interaction, 1)  # pyright: ignore[reportGeneralTypeIssues]
    mock_interaction.response.defer.assert_awaited_once()
    mock_interaction.followup.send.assert_awaited_once()
    _, kwargs = mock_interaction.followup.send.await_args
    assert "embed" in kwargs, "Expected an embed to be sent."
    assert kwargs["embed"].image.url == "attachment://tictactoe.png", "Expected an attachment reference to be sent."
    assert "view" in kwargs, "Expected a view to be sent."
    assert "file" in kwargs, "Expected a file to be sent."


async def test_shrugman_command(mock_bot, mocker: MockerFixture):
    """Test that the code for the shrugman command functions as expected"""
    cog = Reputation(mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.followup = mocker.AsyncMock(spec=discord.Webhook)
    mock_interaction.client = mock_bot
    await cog.shrugman.callback(cog, mock_interaction)  # pyright: ignore[reportGeneralTypeIssues]
    mock_interaction.response.defer.assert_awaited_once()
    mock_interaction.followup.send.assert_awaited_once()
    _, kwargs = mock_interaction.followup.send.await_args
    assert "embed" in kwargs, "Expected an embed to be sent."
    assert "view" in kwargs, "Expected a view to be sent."


@pytest.mark.parametrize("difficulty", ["Beginner", "Intermediate", "Expert", "Super Expert"])
async def test_minesweeper_command(mock_bot, mocker: MockerFixture, difficulty: str):
    """Test that the code for the minesweeper command functions as expected."""
    cog = Reputation(mock_bot)
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.followup = mocker.AsyncMock(spec=discord.Webhook)
    mock_interaction.client = mock_bot
    await cog.minesweeper.callback(cog, mock_interaction, difficulty)  # pyright: ignore[reportGeneralTypeIssues]
    mock_interaction.response.defer.assert_awaited_once()
    mock_interaction.followup.send.assert_awaited_once()
    _, kwargs = mock_interaction.followup.send.await_args
    assert "embed" in kwargs, "Expected an embed to be sent."
    assert kwargs["embed"].image.url == "attachment://minesweeper.png", "Expected an attachment reference to be sent."
    assert "view" in kwargs, "Expected a view to be sent."
    assert "file" in kwargs, "Expected a file to be sent."


async def test_reputation_command(mock_bot, mocker: MockerFixture, database: Pool):
    """Test that the code for the reputation command functions as expected."""
    cog = Reputation(mock_bot)
    mock_bot.pool = database
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.user = mocker.AsyncMock(spec=discord.Member)
    mock_interaction.user.id = 1
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.followup = mocker.AsyncMock(spec=discord.Webhook)
    mock_interaction.client = mock_bot
    await cog.query_points.callback(cog, mock_interaction)  # pyright: ignore[reportGeneralTypeIssues]
    mock_interaction.response.defer.assert_awaited_once()
    mock_interaction.followup.send.assert_awaited_once()
    args, _ = mock_interaction.followup.send.await_args
    assert (
        args[0]
        == "You have 50 reputation, you haven't claimed your daily bonus, and you haven't hit your daily program cap,"
        " and have 0/3 wins in the last month."
    ), "Expected the correct number of points to be sent."
