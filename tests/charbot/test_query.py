import discord
import pytest
from discord import Interaction
from discord.ext import commands
from pytest_mock import MockerFixture

from charbot import CBot, query


def test_cog_check_no_guild(mocker: MockerFixture):
    """Test cog_check when no guild is present."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_ctx.guild = None
    mock_bot = mocker.Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    assert cog.cog_check(mock_ctx) is False


def test_cog_check_not_allowed(mocker: MockerFixture):
    """Test cog_check when user is not allowed."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_ctx.guild = mocker.Mock(spec=discord.Guild)
    mock_ctx.author = mocker.Mock(spec=discord.Member)
    mock_role = mocker.Mock(spec=discord.Role)
    mock_role.id = 684936661745795088
    mock_ctx.author.roles = [mock_role]
    mock_bot = mocker.Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    assert cog.cog_check(mock_ctx) is False


def test_cog_check_allowed(mocker: MockerFixture):
    """Test cog_check when user is allowed."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_ctx.guild = mocker.Mock(spec=discord.Guild)
    mock_ctx.author = mocker.Mock(spec=discord.Member)
    mock_role = mocker.Mock(spec=discord.Role)
    mock_role.id = 338173415527677954
    mock_ctx.author.roles = [mock_role]
    mock_bot = mocker.Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    assert cog.cog_check(mock_ctx) is True


@pytest.mark.asyncio()
async def test_time_command(mocker: MockerFixture):
    """Test time command."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_bot = mocker.Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.time.__call__(mock_ctx, mock_ctx)  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once()


@pytest.mark.asyncio()
async def test_changelog_command(mocker: MockerFixture):
    """Test changelog command."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_bot = mocker.Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.changelog.__call__(mock_ctx, mock_ctx)  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once_with("Here's the changelog: https://bluesy1.github.io/CharB0T/changes")


@pytest.mark.asyncio()
async def test_faq_command(mocker: MockerFixture):
    """Test faq command."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_bot = mocker.Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.faq.__call__(mock_ctx, mock_ctx)  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once()


@pytest.mark.asyncio()
async def test_source_command(mocker: MockerFixture):
    """Test source command."""
    mock_ctx = mocker.Mock(spec=commands.Context)
    mock_bot = mocker.Mock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.source.__call__(mock_ctx, mock_ctx)  # type: ignore  # skipcq: PYL-E1102
    mock_ctx.reply.assert_called_once_with(f"https://bluesy1.github.io/CharB0T/\n{query.__source__}\nMIT License")


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    ("rule", "member_id", "expected_key"), [(None, None, 1), (None, 1, 2), (1, None, 3), (1, 1, 4)]
)
async def test_rule_command(mocker: MockerFixture, rule: int | None, member_id: int | None, expected_key: int):
    """Test rule command."""
    mock_itx = mocker.AsyncMock(spec=Interaction[CBot])
    mock_itx.user = mocker.AsyncMock(spec=discord.Member)
    mock_itx.user.id = member_id
    mock_itx.user.mention = f"<@{member_id}>"
    mock_itx.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_bot = mocker.AsyncMock(spec=commands.Bot)
    cog = query.Query(mock_bot)
    await cog.rules.callback(
        cog,
        mock_itx,
        rule,
        mock_itx.user if member_id else None,  # pyright: ignore[reportCallIssue]
    )
    mock_itx.response.send_message.assert_awaited_once()
    res = mock_itx.response.send_message.await_args.args[0]
    assert (
        res
        == {
            1: "**1**: Be respectful to others. Being drunk is not an excuse for being stupid. Common-sense matters"
            ". Just because it isn't explicitly written here, doesn't mean it doesn't break the rules.\n**2**: Please"
            " utilize the text and voice channels as they are described and keep things on topic. Please be open to"
            " explaining and including others for any conversation you have here.\n**3**: Don't spam. Intentionally"
            " spamming gets you kicked or muted. Whether or not you are spamming is subject to interpretation of"
            " the moderator team. I will side with their judgment.\n**4**: Please do NOT use this as a venue for"
            " asking me when new videos will be released. I release stuff as fast as my schedule allows. "
            "See <#922613000047824956> for the breakdown\n**5**: In voice channels, please be courteous and do not hog"
            " the mic, scream, play background music, or other annoying things.\n**6**: Please no backseat gaming"
            " (we get enough of it on YouTube comments), and don't throw out spoilers to current things I or another"
            " person is working on.\n**7**: Feel free to use pictures in the chats, but nothing too crude,"
            " and nothing X rated. Insta-ban for anyone posting pornography, etc.\n**8**: Discord invites"
            " and promotions of your own content anywhere but <#298485559813210115> are restricted, if you wish"
            " to post one somewhere please check with Mods\n**9**: Please respect the Mods here. They are good people"
            " who sincerely want this environment to be awesome too. If they're advising you to change your behavior,"
            " it's the same as me doing it. Please listen.\n**10**: Some language will be deleted. I like the idea of"
            " maintaining a PG-13 community environment. Find a way to say it another way, if the bot kills your"
            " message.",
            2: "<@1>:\n**1**: Be respectful to others. Being drunk is not an excuse for being stupid. Common-sense "
            "matters. Just because it isn't explicitly written here, doesn't mean it doesn't break the rules.\n**2**: "
            "Please utilize the text and voice channels as they are described and keep things on topic. Please be open"
            " to explaining and including others for any conversation you have here.\n**3**: Don't spam. Intentionally"
            " spamming gets you kicked or muted. Whether or not you are spamming is subject to interpretation of"
            " the moderator team. I will side with their judgment.\n**4**: Please do NOT use this as a venue for"
            " asking me when new videos will be released. I release stuff as fast as my schedule allows. "
            "See <#922613000047824956> for the breakdown\n**5**: In voice channels, please be courteous and do not hog"
            " the mic, scream, play background music, or other annoying things.\n**6**: Please no backseat gaming"
            " (we get enough of it on YouTube comments), and don't throw out spoilers to current things I or another"
            " person is working on.\n**7**: Feel free to use pictures in the chats, but nothing too crude,"
            " and nothing X rated. Insta-ban for anyone posting pornography, etc.\n**8**: Discord invites"
            " and promotions of your own content anywhere but <#298485559813210115> are restricted, if you wish"
            " to post one somewhere please check with Mods\n**9**: Please respect the Mods here. They are good people"
            " who sincerely want this environment to be awesome too. If they're advising you to change your behavior,"
            " it's the same as me doing it. Please listen.\n**10**: Some language will be deleted. I like the idea of"
            " maintaining a PG-13 community environment. Find a way to say it another way, if the bot kills your"
            " message.",
            3: "**Rule 1** is Be respectful to others. Being drunk is not an excuse for being stupid. "
            "Common-sense matters. Just because it isn't explicitly written here, doesn't mean it doesn't break the "
            "rules.\n The rules can be found here: "
            "<https://cpry.net/DiscordRules>",
            4: "<@1>:\n**Rule 1** is Be respectful to others. Being drunk is not an excuse for being stupid. "
            "Common-sense matters. Just because it isn't explicitly written here, doesn't mean it doesn't break the "
            "rules.\n The rules can be found here: "
            "<https://cpry.net/DiscordRules>",
        }[expected_key]
    )


@pytest.mark.asyncio()
@pytest.mark.parametrize("ephemeral", [True, False])
async def test_leaderboard_command(mocker: MockerFixture, ephemeral: bool):
    """Test leaderboard command."""
    mock_itx = mocker.AsyncMock(spec=Interaction[CBot], response=mocker.AsyncMock(spec=discord.InteractionResponse))
    cog = query.Query(mocker.AsyncMock(spec=CBot))
    await cog.leaderboard.callback(cog, mock_itx, ephemeral)  # pyright: ignore[reportCallIssue]
    mock_itx.response.send_message.assert_awaited_once_with("https://cpry.net/leaderboard", ephemeral=ephemeral)
