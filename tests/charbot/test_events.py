from datetime import timedelta

import discord
import pytest
from discord.utils import utcnow
from pytest_mock import MockerFixture

from charbot import CBot, constants, events


TILDE_SHORT = "~~:.|:;~~"
TILDE_LONG = "tilde tilde colon dot vertical bar colon semicolon tilde tilde"
URL_1 = "https://www.google.ca/?gws_rd=ssl"
URL_2 = "https://canvas.ubc.ca/courses/100236/modules"


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("Hello", False),
        (f"{TILDE_SHORT}", True),
        (f"prefix{TILDE_SHORT}", True),
        (f"{TILDE_SHORT}suffix", True),
        (f"prefix{TILDE_SHORT}suffix", True),
        (TILDE_LONG, True),
        (f"prefix{TILDE_LONG}", True),
        (f"{TILDE_LONG}suffix", True),
        (f"prefix{TILDE_LONG}suffix", True),
    ],
)
def test_tilde_regex(string: str, expected: bool, mocker: MockerFixture):
    """Test if the tilde regex hits expected cases"""
    bot = mocker.AsyncMock(spec=CBot)
    cog = events.Events(bot)
    assert bool(cog.tilde_regex.search(string)) == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("Hello", False),
        (f"{URL_1}", True),
        (f"<{URL_1}>", True),
        (f"\n{URL_1}", True),
        (f"{URL_2}", True),
        (f"<{URL_2}>", True),
        (f"\n{URL_2}", True),
    ],
)
def test_urlextract(string: str, expected: bool, mocker: MockerFixture):
    """Test if the url regex hits expected cases"""
    bot = mocker.AsyncMock(spec=CBot)
    cog = events.Events(bot)
    assert bool(cog.extractor.has_urls(string)) == expected


def test_url_allowed_forum_channel(mocker: MockerFixture):
    """Test if it properly it short circuits on the forum channel with the correct tag."""
    thread = mocker.AsyncMock(spec=discord.Thread)
    thread.parent_id = 1019647326601609338
    tag = mocker.AsyncMock(spec=discord.ForumTag)
    tag.id = 1019691620741959730
    thread.applied_tags = [tag]
    assert events.url_posting_allowed(thread, [])


@pytest.mark.parametrize("category", [360814817457733635, 360818916861280256, 942578610336837632])
def test_url_allowed_category(category: int, mocker: MockerFixture):
    """Test if it properly it short circuits on the category with the correct tag."""
    channel = mocker.AsyncMock(spec=discord.TextChannel)
    channel.category_id = category
    assert events.url_posting_allowed(channel, [])


@pytest.mark.parametrize("channel_id", [723653004301041745, 338894508894715904, 407185164200968203])
def test_url_allowed_channel_id(mocker: MockerFixture, channel_id: int):
    """Test if the allowed channels are whitelisted"""
    channel = mocker.AsyncMock(spec=discord.TextChannel)
    channel.id = channel_id
    assert events.url_posting_allowed(channel, [])


@pytest.mark.parametrize(
    ("role_ids", "expected"),
    [
        ([], False),
        ([0], False),
        *zip(
            (
                [337743478190637077],
                [685331877057658888],
                [969629622453039104],
                [969629628249563166],
                [969629632028614699],
                [969628342733119518],
                [969627321239760967],
                [406690402956083210],
                [387037912782471179],
                [338173415527677954],
                [725377514414932030],
                [253752685357039617],
                [225413350874546176],
                [729368484211064944],
            ),
            (True for _ in range(20)),
        ),
    ],
)
def test_url_no_early_exit(role_ids, expected, mocker: MockerFixture):
    """Test if the long exit case tests properly"""
    channel = mocker.AsyncMock(spec=discord.TextChannel)
    roles = []
    for role_id in role_ids:
        role = mocker.AsyncMock(spec=discord.Role)
        role.id = role_id
        roles.append(role)
    assert events.url_posting_allowed(channel, roles) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "0 Year(s), 0 Day(s), 0 Hour(s), 0 Min(s), 0.00 Sec(s)"),
        (10, "0 Year(s), 0 Day(s), 0 Hour(s), 0 Min(s), 10.00 Sec(s)"),
        ((2**15) * (3**8), "6 Year(s), 298 Day(s), 7 Hour(s), 40 Min(s), 48.00 Sec(s)"),
        ((2**7) * (3**3) * (5**3) * 73, "1 Year(s), 0 Day(s), 0 Hour(s), 0 Min(s), 0.00 Sec(s)"),
    ],
)
def test_time_string_from_seconds(value: float, expected: str):
    """Test that the conversion is done properly"""
    assert events.time_string_from_seconds(value) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("bot", [True, False])
async def test_on_message_bot_user(bot: bool, mocker: MockerFixture):
    """Test on message where the message author is a bot"""
    message = mocker.AsyncMock(spec=discord.Message)
    message.author.bot = bot
    message.guild = None
    message.channel = mocker.AsyncMock(spec=discord.DMChannel)
    bot = mocker.AsyncMock(spec=CBot)
    bot.get_channel = lambda _: mocker.AsyncMock(spec=discord.TextChannel)
    cog = events.Events(bot)
    await cog.on_message(message)
    if not bot:
        assert message.channel.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_fail_everyone_ping(mocker: MockerFixture):
    """Test that the on message deletes everyone pings from non mods"""
    message = mocker.AsyncMock(spec=discord.Message)
    message.author = mocker.AsyncMock(spec=discord.Member)
    message.author.bot = False
    message.author.roles = []
    message.content = "@everyone"
    message.guild = mocker.AsyncMock(spec=discord.Guild)
    bot = mocker.AsyncMock(spec=CBot)
    cog = events.Events(bot)
    cog.webhook = mocker.AsyncMock(spec=discord.Webhook)
    await cog.on_message(message)
    message.delete.assert_awaited_once()
    message.author.add_roles.assert_awaited_once_with(
        discord.Object(id=676250179929636886), discord.Object(id=684936661745795088)
    )


@pytest.mark.asyncio
async def test_fail_telegram_link(mocker: MockerFixture):
    """Test that the on message deletes telegram links from non mods"""
    message = mocker.AsyncMock(spec=discord.Message)
    message.author = mocker.AsyncMock(spec=discord.Member)
    message.author.bot = False
    message.author.roles = []
    message.content = "https://t.me/abcd1234"
    message.guild = mocker.AsyncMock(spec=discord.Guild)
    bot = mocker.AsyncMock(spec=CBot)
    cog = events.Events(bot)
    cog.webhook = mocker.AsyncMock(spec=discord.Webhook)
    await cog.on_message(message)
    message.delete.assert_awaited_once()
    message.author.add_roles.assert_awaited_once_with(
        discord.Object(id=676250179929636886), discord.Object(id=684936661745795088)
    )


@pytest.mark.asyncio
async def test_fail_link(mocker: MockerFixture):
    """Test that the on message deletes everyone pings from non mods"""
    message = mocker.AsyncMock(spec=discord.Message)
    message.author = mocker.AsyncMock(spec=discord.Member)
    message.author.bot = False
    message.author.roles = []
    message.content = URL_2
    message.guild = mocker.AsyncMock(spec=discord.Guild)
    bot = mocker.AsyncMock(spec=CBot)
    cog = events.Events(bot)
    await cog.on_message(message)
    message.delete.assert_awaited_once()
    message.author.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_parse_timeout(mocker: MockerFixture):
    """Test that the on message deletes everyone pings from non mods"""
    member = mocker.AsyncMock(spec=discord.Member)
    member.id = 1
    member.timed_out_until = utcnow() + timedelta(seconds=694900)
    cog = events.Events(mocker.AsyncMock(spec=CBot))
    webhook = mocker.AsyncMock(spec=discord.Webhook)
    cog.webhook = webhook
    await cog.parse_timeout(member)
    assert 1 in cog.timeouts
    assert cog.timeouts[1] == member.timed_out_until
    webhook.send.assert_awaited_once()
    view = webhook.send.await_args.kwargs["view"]
    assert isinstance(view, discord.ui.LayoutView)
    container = view.children[0]
    assert isinstance(container, discord.ui.Container)
    title = container.children[0]
    assert isinstance(title, discord.ui.TextDisplay)
    assert "[TIMEOUT]" in title.content
    duration = container.children[2]
    assert isinstance(duration, discord.ui.TextDisplay)
    dur = duration.content
    assert dur is not None
    assert "1 Week" in dur
    assert "1 Day(s)" in dur
    assert "1 Hour(s)" in dur
    assert "1 Minute(s)" in dur
    assert "40 Second(s)" in dur


@pytest.mark.asyncio
async def test_on_member_join(mocker: MockerFixture):
    """Test members get properly added on join."""
    member = mocker.AsyncMock(spec=discord.Member)
    member.id = 1
    member.guild.id = constants.GUILD_ID
    cog = events.Events(mocker.AsyncMock(spec=CBot))
    await cog.on_member_join(member)
    assert 1 in cog.members


@pytest.mark.asyncio
async def test_thread_create(mocker: MockerFixture):
    """Test that thread creates get handled properly"""
    cog = events.Events(mocker.AsyncMock(spec=CBot))
    thread = mocker.AsyncMock(spec=discord.Thread)
    thread.id = 1
    thread.parent = mocker.AsyncMock(spec=discord.ForumChannel)
    message = mocker.AsyncMock(spec=discord.PartialMessage)
    thread.get_partial_message.return_value = message
    await cog.on_thread_create(thread)
    thread.get_partial_message.assert_called_once_with(thread.id)
    message.pin.assert_awaited_once()
