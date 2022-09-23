# -*- coding: utf-8 -*-
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
