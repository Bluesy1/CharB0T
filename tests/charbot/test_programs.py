import datetime
from typing import Literal

import discord
import pytest
from asyncpg import Pool
from pytest_mock import MockerFixture

from charbot import CBot, errors
from charbot.programs.cog import Reputation


pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_bot(mocker: MockerFixture):
    """Mock discord.Client."""
    return mocker.AsyncMock(spec=CBot, CHANNEL_ID=CBot.CHANNEL_ID, ALLOWED_ROLES=CBot.ALLOWED_ROLES, TIME=CBot.TIME)


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


async def test_interaction_check_no_guild(mock_inter):
    """Test the interaction check when the interaction is not in a guild."""
    mock_inter.guild = None
    with pytest.raises(discord.app_commands.NoPrivateMessage) as exc:
        await Reputation().interaction_check(mock_inter)
    assert exc.value.args[0] == "Programs can't be used in direct messages."


async def test_interaction_check_wrong_guild(mock_inter, mocker: MockerFixture):
    """Test the interaction check when the interaction is in the wrong guild."""
    mock_inter.guild = mocker.AsyncMock(spec=discord.Guild, id=0)
    with pytest.raises(discord.app_commands.NoPrivateMessage) as exc:
        await Reputation().interaction_check(mock_inter)
    assert exc.value.args[0] == "Programs can't be used in this server."


async def test_interaction_check_wrong_channel(mock_inter, mocker: MockerFixture):
    """Test the interaction check when the interaction is in the wrong channel."""
    mock_inter.channel = mocker.AsyncMock(spec=discord.TextChannel, id=0)
    mock_inter.guild = mocker.AsyncMock(spec=discord.Guild, id=225345178955808768)
    with pytest.raises(errors.WrongChannelError) as exc:
        await Reputation().interaction_check(mock_inter)
    assert exc.value._channel == 969972085445238784
    assert str(exc.value) == "This command can only be run in the channel <#969972085445238784> ."


async def test_interaction_check_no_allowed_roles(mock_inter, mocker: MockerFixture):
    """Test the interaction check when the interaction is in the wrong channel."""
    mock_inter.channel = mocker.AsyncMock(spec=discord.TextChannel, id=969972085445238784)
    mock_inter.guild = mocker.AsyncMock(spec=discord.Guild, id=225345178955808768)
    with pytest.raises(errors.MissingProgramRole) as exc:
        await Reputation().interaction_check(mock_inter)
    assert (
        exc.value.args[0]
        == "You are missing at least one of the required roles: '337743478190637077', '685331877057658888', "
        "'969629622453039104', '969629628249563166', '969629632028614699', '969628342733119518', "
        "'969627321239760967' or '969626979353632790'"
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
    assert str(exc.value) == (
        "You are missing at least one of the required roles: '337743478190637077', '685331877057658888', "
        "'969629622453039104', '969629628249563166', '969629632028614699', '969628342733119518', '969627321239760967' "
        "or '969626979353632790' - you must be at least level 1 to use this command/button."
    )


async def test_interaction_check_allowed(mock_inter, mocker: MockerFixture):
    """Test the interaction check when the interaction is in the right channel and guild."""
    mock_inter.channel = mocker.AsyncMock(spec=discord.TextChannel, id=969972085445238784)
    mock_inter.guild = mocker.AsyncMock(spec=discord.Guild, id=225345178955808768)
    mock_inter.user = mocker.AsyncMock(
        spec=discord.Member,
        roles=[
            discord.Object(id=337743478190637077),
            discord.Object(id=685331877057658888),
        ],
    )
    assert await Reputation().interaction_check(mock_inter) is True, "interaction_check should return True"


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


async def test_reputation_command(mock_inter, database: Pool):
    """Test that the code for the reputation command functions as expected."""
    cog = Reputation()
    mock_inter.client.pool = database
    await cog.query_points.callback(cog, mock_inter)  # pyright: ignore[reportCallIssue]
    mock_inter.response.defer.assert_awaited_once()
    mock_inter.followup.send.assert_awaited_once()
    args, _ = mock_inter.followup.send.await_args
    assert (
        args[0]
        == "You have 50 reputation, you haven't claimed your daily bonus, and you haven't hit your daily program cap,"
        " and have 0/3 wins in the last month."
    ), "Expected the correct number of points to be sent."


async def test_rollcall_new_user(mock_inter, database: Pool):
    """Test the rollcall command for a user who hasn't interacted with the system before."""
    mock_inter.user.id = 10
    mock_inter.client.pool = database
    cog = Reputation()
    await cog.rollcall.callback(cog, mock_inter)  # pyright: ignore[reportCallIssue]
    mock_inter.response.defer.assert_awaited_once_with(ephemeral=True)
    mock_inter.followup.send.assert_awaited_once_with("You got some Rep today, inmate")
    assert await database.fetchval("SELECT points FROM users WHERE id=10") == 20, (
        "Points should be 20 after the first rollcall"
    )
    daily_points = await database.fetchrow("SELECT * FROM daily_points WHERE id=10")
    assert daily_points is not None, "Expected a row to be created in the daily_points table."
    assert daily_points["particip"] == daily_points["won"] == 0, "Programs points should be set to 0"
    assert daily_points["last_claim"] == mock_inter.client.TIME(), "Last claim time should be now"
    await database.execute("DELETE FROM users WHERE id=10")


async def test_rollcall_existing_user_no_gain(mock_inter, database: Pool):
    """Test the rollcall command for a user who has interacted with the system before."""
    mock_inter.user.id = 10
    mock_inter.client.pool = database
    cog = Reputation()
    await database.execute("INSERT INTO users (id, points) VALUES (10, 20)")
    await database.execute(
        "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won) VALUES (10, $1, $1, 0, 0)",
        mock_inter.client.TIME(),
    )
    await cog.rollcall.callback(cog, mock_inter)  # pyright: ignore[reportCallIssue]
    mock_inter.response.defer.assert_awaited_once_with(ephemeral=True)
    mock_inter.followup.send.assert_awaited_once_with("No more Rep for you yet, get back to your cell")
    assert await database.fetchval("SELECT points FROM users WHERE id=10") == 20, (
        "Points should be 20 after the rejected rollcall"
    )
    await database.execute("DELETE FROM users WHERE id=10")


async def test_rollcall_existing_user_gain(mock_inter, database: Pool):
    """Test the rollcall command for a user who has interacted with the system before."""
    mock_inter.user.id = 10
    mock_inter.client.pool = database
    cog = Reputation()
    await database.execute("INSERT INTO users (id, points) VALUES (10, 20)")
    await database.execute(
        "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won) VALUES (10, $1, $1, 0, 0)",
        mock_inter.client.TIME() - datetime.timedelta(days=1),
    )
    await cog.rollcall.callback(cog, mock_inter)  # pyright: ignore[reportCallIssue]
    mock_inter.response.defer.assert_awaited_once_with(ephemeral=True)
    mock_inter.followup.send.assert_awaited_once_with("You got some Rep today, inmate")
    assert await database.fetchval("SELECT points FROM users WHERE id=10") == 40, (
        "Points should be 40 after the accepted rollcall"
    )
    await database.execute("DELETE FROM users WHERE id=10")
