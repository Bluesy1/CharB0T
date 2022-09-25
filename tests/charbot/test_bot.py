# -*- coding: utf-8 -*-
import datetime
import zoneinfo

import pytest
from discord.utils import MISSING

from charbot.bot import CBot, Holder


@pytest.fixture
def unused_patch_datetime_now(monkeypatch: pytest.MonkeyPatch):
    """Patch the datetime.now() method to return a fixed time"""

    class MyDateTime(datetime.datetime):
        """A datetime class that returns a fixed time"""

        @classmethod
        def now(cls, tz: datetime.tzinfo | None = ...):
            """Return a fixed time"""
            return datetime.datetime(1, 1, 2, 1, 0, 0, 0, tzinfo=tz)

    monkeypatch.setattr(datetime, "datetime", MyDateTime)


def test_holder():
    """Test the Holder class"""
    holder = Holder()
    val = holder["value"]
    assert val is MISSING
    del holder["nonexistent"]
    assert holder.pop("nonexistent") is MISSING
    assert holder.get("nonexistent") is MISSING
    holder.setdefault("value", "default")
    assert holder["value"] == "default"
    holder.setdefault("value", "new")
    assert holder["value"] == "default"
    assert holder.get("value") == "default"
    assert holder.pop("value") == "default"
    assert holder.get("value") is MISSING
    holder["value"] = "new"
    del holder["value"]
    assert holder.get("value") is MISSING


def test_time(unused_patch_datetime_now):
    """Test the time classmethod"""
    assert CBot.TIME() == datetime.datetime(1, 1, 1, 9, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo(key="America/Detroit"))
