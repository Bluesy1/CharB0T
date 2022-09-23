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


@pytest.mark.parametrize("category", [(360814817457733635,), (360818916861280256,), (942578610336837632,)])
def test_url_allowed_category(category: int, mocker: MockerFixture):
    """Test if it properly short circuits on the category with the correct tag."""
    channel = mocker.AsyncMock(spec=discord.TextChannel)
    channel.category_id = category
    assert not events.url_posting_allowed(channel, [])


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
