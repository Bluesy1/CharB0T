# -*- coding: utf-8 -*-
import discord
import pytest
from pytest_mock import MockerFixture

from charbot import CBot, events

TILDE_SHORT = "~~:.|:;~~"
TILDE_LONG = "tilde tilde colon dot vertical bar colon semicolon tilde tilde"
URL_1 = "https://www.google.ca/?gws_rd=ssl"
URL_2 = "https://canvas.ubc.ca/courses/100236/modules"


@pytest.mark.parametrize(
    "string,expected",
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
    "string,expected",
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
    """Test if it properly short circuits on the forum channel with the correct tag."""
    thread = mocker.AsyncMock(spec=discord.Thread)
    thread.parent_id = 1019647326601609338
    tag = mocker.AsyncMock(spec=discord.ForumTag)
    tag.id = 1019647326601609338
    thread.applied_tags = [tag]
    assert events.url_posting_allowed(thread, [])


@pytest.mark.parametrize("category", [360814817457733635, 360818916861280256, 942578610336837632])
def test_url_allowed_category(category: int, mocker: MockerFixture):
    """Test if it properly short circuits on the category with the correct tag."""
    channel = mocker.AsyncMock(spec=discord.TextChannel)
    channel.category_id = category
    assert events.url_posting_allowed(channel, [])


@pytest.mark.parametrize("role_ids,expected", [([], False), ([0], False), ([337743478190637077], True)])
def test_url_no_early_exit(role_ids, expected, mocker: MockerFixture):
    """Test if the long exit case tests properly"""
    channel = mocker.AsyncMock(spec=discord.TextChannel)
    roles = []
    for role_id in role_ids:
        role = mocker.AsyncMock(spec=discord.Role)
        role.id = role_id
        roles.append(role)
    assert events.url_posting_allowed(channel, roles) is expected


def test_sensitive_embed(mocker: MockerFixture, monkeypatch):
    """Test that the sensitive embed is constructed properly"""
    message = mocker.AsyncMock(spec=discord.Message)
    message.content = "a"
    message.author = mocker.AsyncMock(spec=discord.Member)
    message.author.display_name = "A"
    message.author.__str__ = lambda self: "a#1000"  # pyright: ignore[reportGeneralTypeIssues]
    message.jump_url = "https://discord.com/channels/0/1/2"
    monkeypatch.setattr(events, "utcnow", lambda: None)
    expected = discord.Embed(
        title="Probable Sensitive Topic Detected",
        description="Content:\n a",
        color=discord.Color.red(),
        timestamp=None,
    )
    expected.add_field(name="Words Found:", value="a", inline=True)
    expected.add_field(name="Author:", value="A: a#1000", inline=True)
    expected.add_field(name="Message Link:", value="[Link](https://discord.com/channels/0/1/2)", inline=True)
    actual = events.sensitive_embed(message, {"a"})
    assert expected == actual


@pytest.mark.parametrize(
    "value,expected",
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
async def test_return_on_sensitive_fail(mocker: MockerFixture, monkeypatch):
    """Test that the on message short circuits when sensitive scan fails"""
    message = mocker.AsyncMock(spec=discord.Message)
    message.author.bot = False
    message.guild = mocker.AsyncMock(spec=discord.Guild)
    bot = mocker.AsyncMock(spec=CBot)
    cog = events.Events(bot)
    fake_scan = mocker.AsyncMock()
    fake_scan.return_value = False
    monkeypatch.setattr(cog, "sensitive_scan", fake_scan)
    await cog.on_message(message)
    fake_scan.assert_awaited_once()


@pytest.mark.asyncio
async def test_fail_everyone_ping(mocker: MockerFixture, monkeypatch):
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
    fake_scan = mocker.AsyncMock()
    fake_scan.return_value = True
    monkeypatch.setattr(cog, "sensitive_scan", fake_scan)
    await cog.on_message(message)
    message.delete.assert_awaited_once()
    message.author.add_roles.assert_awaited_once_with(
        discord.Object(id=676250179929636886), discord.Object(id=684936661745795088)
    )
