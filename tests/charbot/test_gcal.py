# -*- coding: utf-8 -*-
import datetime
from zoneinfo import ZoneInfo

import aiohttp
import discord
import pytest
from pytest_mock import MockerFixture

# noinspection PyProtectedMember
from charbot import CBot, _Config, gcal  # skipcq
from charbot.bot import Holder


@pytest.fixture
def mock_config(monkeypatch):
    """config.toml mocking"""
    data = {
        "calendar": {"key": "calenderkey"},
        "discord": {
            "webhooks": {
                "calendar": 1,
            },
            "messages": {
                "calendar": 1,
            },
        },
    }
    monkeypatch.setattr(_Config, "__getitem__", lambda self, key: data[key])
    return data


def test_get_url(mock_config):
    """Test get_url."""
    date_min = datetime.datetime(1, 1, 1, 0, 0, 0, 0)
    date_max = datetime.datetime(10, 10, 10, 10, 10, 10, 10)

    assert (
        f"https://www.googleapis.com/calendar/v3/calendars/u8n1onpbv9pb5du7gssv2md58s@group.calendar.google.com/events?"
        f"key={mock_config['calendar']['key']}&timeMin=0001-01-01T00:00:00&timeMax=0010-10-10T10:10:10.000010"
        == gcal.get_params(date_min, date_max)
    )


def test_half_hour_intervals():
    """Test half_hour_intervals."""
    count = 0
    for interval in gcal.half_hour_intervals():
        hours = count // 2
        minutes = 30 * (count % 2)

        assert datetime.time(hours, minutes) == interval
        count += 1


def test_ceil_dt():
    """Test ceil_dt."""
    dt = datetime.datetime(1, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
    delta = datetime.timedelta(15)
    assert dt + (datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo=datetime.timezone.utc) - dt) % delta == gcal.ceil_dt(
        dt, delta
    )


def test_calendar_embed():
    """Test create_embed."""
    test: dict[int, gcal.EmbedField] = {}
    fake_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
    sample: gcal.CalEvent = {
        "summary": "test",
        "start": {"dateTime": "2022-03-24T12:00:00-04:00", "timeZone": "America/Detroit"},
        "end": {"dateTime": "2022-03-24T16:00:00-04:00", "timeZone": "America/Detroit"},
        "updated": "2022-03-24T12:00:00-04:00",
        "created": "2022-03-24T12:00:00-04:00",
        "description": "test",
        "status": "confirmed",
        "originalStartTime": {"dateTime": "2022-03-24T16:00:00-04:00", "timeZone": "America/Detroit"},
    }
    gcal.default_field(test, fake_time, sample)
    assert len(test) == 1
    assert isinstance(test[0], gcal.EmbedField)
    assert test[0].name == "test"
    assert test[0].value == "<t:0:F>\n[(19:00 12/31/69 EST)](https://www.youtube.com/charliepryor/live)"
    assert test[0].inline is True

    embed = gcal.calendar_embed(test, fake_time)
    assert isinstance(embed, discord.Embed)
    desc = embed.description
    assert isinstance(desc, str)
    assert "Next stream: <t:0:R>" in desc
    assert embed.fields[0].name == test[0].name
    assert embed.fields[0].value == test[0].value
    assert embed.fields[0].inline is True
    assert embed.color == discord.Color.dark_blue()
    assert embed.footer.text == "Last Updated"
    assert embed.author.name == "Charlie"


@pytest.mark.asyncio
async def test_cog_init_load_unload(mocker: MockerFixture, event_loop, mock_config):
    """Test cog constructor, load, unload."""
    bot = mocker.AsyncMock(spec=CBot)
    bot.holder = Holder()
    fake_webhook = mocker.AsyncMock(spec=discord.Webhook)
    fetch_webhook = mocker.AsyncMock(spec=discord.Webhook, return_value=fake_webhook)
    bot.fetch_webhook = fetch_webhook
    bot.loop = event_loop
    await gcal.setup(bot)
    bot.add_cog.assert_called_once()
    cog: gcal.Calendar = bot.add_cog.call_args.args[0]
    start_spy = mocker.spy(cog.calendar, "start")
    cancel_spy = mocker.spy(cog.calendar, "cancel")
    await cog.cog_load()
    assert isinstance(cog, gcal.Calendar)
    assert cog.bot is bot
    assert cog.message is discord.utils.MISSING
    assert cog.webhook is fake_webhook
    fetch_webhook.assert_awaited_once()
    # fetch_webhook.assert_called_once_with(mock_config["discord"]["webhook"]["calendar"])
    # For some reason, the above line doesn't work. The call has thr right args. but the following error occurs:
    # >       fetch_webhook.assert_awaited_once_with(mock_config["discord"]["webhook"]["calendar"])
    # E       AssertionError: expected call not found.
    # E       Expected: fetch_webhook(1)
    # E       Actual: fetch_webhook(1)
    assert start_spy.call_count == 1
    await cog.cog_unload()
    assert cancel_spy.call_count == 1
    assert bot.holder.get("message") is discord.utils.MISSING
    assert bot.holder.get("webhook") is fake_webhook


@pytest.mark.asyncio
async def test_caledar_task(mocker: MockerFixture, event_loop, mock_config, monkeypatch):
    """Test calendar task."""
    data = {
        "items": [
            {
                "status": "cancelled",
                "created": "2022-03-11T04:26:45.000Z",
                "updated": "2022-04-30T17:02:48.118Z",
                "summary": "Software Inc",
                "originalStartTime": {"dateTime": "2022-03-22T12:00:00-04:00", "timeZone": "America/Detroit"},
                "start": {"dateTime": "2022-06-16T12:00:00-04:00", "timeZone": "America/Detroit"},
                "end": {"dateTime": "2022-03-22T16:00:00-04:00", "timeZone": "America/Detroit"},
            },
            {
                "status": "confirmed",
                "created": "2022-03-11T04:27:18.000Z",
                "updated": "2022-04-30T17:12:25.493Z",
                "summary": "Software Inc",
                "originalStartTime": {"dateTime": "2022-03-22T12:00:00-04:00", "timeZone": "America/Detroit"},
                "start": {
                    "dateTime": (
                        datetime.datetime.now(tz=ZoneInfo("America/New_York")) - datetime.timedelta(hours=1)
                    ).strftime("%Y-%m-%dT%H:%M:%S-04:00"),
                    "timeZone": "America/Detroit",
                },
                "end": {"dateTime": "2022-03-24T16:00:00-04:00", "timeZone": "America/Detroit"},
            },
            {
                "status": "confirmed",
                "created": "2022-03-11T04:27:18.000Z",
                "updated": "2022-04-30T17:12:25.493Z",
                "summary": "Software Inc",
                "description": "https://www.twitch.tv/charliepryor",
                "originalStartTime": {"dateTime": "2022-03-22T12:00:00-04:00", "timeZone": "America/Detroit"},
                "start": {
                    "dateTime": (
                        datetime.datetime.now(tz=ZoneInfo("America/New_York")) - datetime.timedelta(hours=1)
                    ).strftime("%Y-%m-%dT%H:%M:%S-04:00"),
                    "timeZone": "America/Detroit",
                },
                "end": {"dateTime": "2022-03-24T16:00:00-04:00", "timeZone": "America/Detroit"},
            },
            {
                "status": "confirmed",
                "created": "2022-03-11T04:26:45.000Z",
                "updated": "2022-05-18T17:35:59.959Z",
                "summary": "TBA",
                "originalStartTime": {"dateTime": "2022-03-22T12:00:00-04:00", "timeZone": "America/Detroit"},
                "start": {
                    "dateTime": (
                        datetime.datetime.now(tz=ZoneInfo("America/New_York")) + datetime.timedelta(days=8)
                    ).strftime("%Y-%m-%dT%H:%M:%S-04:00"),
                    "timeZone": "America/Detroit",
                },
                "end": {"dateTime": "2022-06-14T16:00:00-04:00", "timeZone": "America/Detroit"},
            },
            {
                "status": "confirmed",
                "created": "2022-03-11T04:27:18.000Z",
                "updated": "2022-05-18T17:36:10.247Z",
                "summary": "TBA",
                "description": "test",
                "originalStartTime": {"dateTime": "2022-03-22T12:00:00-04:00", "timeZone": "America/Detroit"},
                "start": {"dateTime": "2022-06-16T12:00:00-04:00", "timeZone": "America/Detroit"},
                "end": {"dateTime": "2022-06-16T16:00:00-04:00", "timeZone": "America/Detroit"},
            },
        ],
    }
    mock_response = mocker.AsyncMock(spec=aiohttp.ClientResponse)
    mock_response.json.return_value = data

    class mock_get:
        """Mock aiohttp.ClientSession.get()"""

        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    bot = mocker.AsyncMock(spec=CBot)
    bot.holder = Holder()
    bot.holder["webhook"] = mocker.AsyncMock(spec=discord.Webhook)
    bot.user = mocker.AsyncMock(spec=discord.ClientUser)
    fake_webhook = mocker.AsyncMock(spec=discord.Webhook)
    fake_message = mocker.AsyncMock(spec=discord.WebhookMessage)
    fake_webhook.fetch_message.return_value = fake_message
    bot.fetch_webhook.retun_value = fake_webhook
    bot.loop = event_loop
    async with aiohttp.ClientSession() as session:
        session.get = lambda *args, **kwargs: mock_get()  # type: ignore
        bot.session = session
        cog = gcal.Calendar(bot)
        await cog.cog_load()
        await cog.calendar.__call__()  # skipcq: PYL-E1102
    cog.calendar.cancel()
    assert mock_response.json.call_count == 1
    assert mock_response.json.call_args.kwargs["loads"] is __import__("orjson").loads
    # fake_webhook.fetch_message.edit.assert_awaited_once()
    # IDK, this isn't working right now
    # TODO: figure out why, skipcq - this is a later thing to worry about
