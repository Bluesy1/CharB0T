import datetime

import pytest

from charbot import gcal


@pytest.fixture
def url_mock_response(monkeypatch):
    """os.env"""
    monkeypatch.setenv("CALKEY", "calenderkey")


def test_get_url(url_mock_response):
    date_min = datetime.datetime(1, 1, 1, 0, 0, 0, 0)
    date_max = datetime.datetime(10, 10, 10, 10, 10, 10, 10)

    assert (
        "https://www.googleapis.com/calendar/v3/calendars/u8n1onpbv9pb5du7gssv2md58s@group.calendar.google.com"
        "/events?key=calenderkey&timeMin=0001-01-01T00:00:00&timeMax=0010-10-10T10:10:10.000010"
        == gcal.getUrl(date_min, date_max)
    )


def test_half_hour_intervals():
    count = 0
    for interval in gcal.half_hour_intervals():
        hours = count // 2
        minutes = 30 * (count % 2)

        assert datetime.time(hours, minutes) == interval
        count += 1


def test_ceil_dt():
    dt = datetime.datetime(1, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
    delta = datetime.timedelta(15)
    assert dt + (datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo=datetime.timezone.utc) - dt) % delta == gcal.ceil_dt(
        dt, delta
    )
