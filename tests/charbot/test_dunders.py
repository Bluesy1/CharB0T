# -*- coding: utf-8 -*-
import builtins
import logging
from io import BytesIO

import pytest

import charbot
from charbot import Config


def test_config(monkeypatch, caplog):
    """Test config."""

    class mock_open:
        """Mock of the open() function"""

        def __init__(self, path, mode, *args, **kwargs):
            self.path = path
            self.mode = mode

        def __enter__(self):
            return BytesIO(b"[calendar]\nkey='key'")

        def __exit__(self, exc_type, exc_val, exc_tb):  # skipcq
            pass

    caplog.set_level(logging.DEBUG)
    monkeypatch.setattr(builtins, "open", mock_open)
    assert Config["calendar"] == {"key": "key"}
    caplog.clear()
    assert Config("calendar", "key") == "key"
    log = caplog.record_tuples[0]
    assert log[0] == "charbot.config"
    assert log[1] == logging.INFO
    assert log[2] == "Got key calendar:key from config file."

    with pytest.raises(KeyError):
        caplog.clear()
        Config("calendar", "badkey")
    log = caplog.record_tuples[0]
    assert log[0] == "charbot.config"
    assert log[1] == logging.ERROR
    assert log[2] == "Tried to get key calendar:badkey from config file, but it was not found."

    class Test(object):
        def __str__(self):
            return "Test"

    obj = Test()
    with pytest.raises(TypeError):
        caplog.clear()
        Config("calendar", obj)
    log = caplog.record_tuples[0]
    assert log[0] == "charbot.config"
    assert log[1] == logging.ERROR
    assert (
        log[2] == f"Tried to get key calendar:Test from config file, but a non string key {obj!r} of type "
        f"{type(obj)} was passed."
    )


@pytest.mark.parametrize(
    ("name", "level", "text", "expected", "last", "expected_last"),
    [
        ("Info_Test_Non_Presence", logging.INFO, "Test", True, True, False),
        ("Info_Test_Presence", logging.INFO, "presence_update", True, False, False),
        ("Debug_Test_Non_Presence", logging.DEBUG, "Test", True, True, False),
        (
            "Debug_Test_Presence_1",
            logging.DEBUG,
            "[2022-07-12 01:16:13] [DEBUG   ] discord.gateway: For Shard ID None: WebSocket Event: "
            "{'t': 'PRESENCE_UPDATE', 's': 346863, 'op': 0, 'd': {'user': {'id': '147223093721563136'}, "
            "'status': 'online', 'guild_id': '225345178955808768', 'client_status': "
            "{'mobile': 'online', 'desktop': 'idle'}, 'activities': []}}",
            False,
            False,
            True,
        ),
        (
            "Debug_Test_Presence_2",
            logging.DEBUG,
            "[2022-07-12 01:16:13] [DEBUG   ] discord.client: Dispatching event socket_event_type",
            False,
            True,
            False,
        ),
        (
            "Debug_Test_Presence_3",
            logging.DEBUG,
            "[2022-07-12 01:16:13] [DEBUG   ] discord.client: Dispatching event presence_update",
            False,
            False,
            False,
        ),
    ],
)
def test_filter(name, level, text, expected, last, expected_last):
    """Test filter."""

    log_filter = charbot.PresenceFilter()
    log_filter.last_presence = last
    test_record = logging.LogRecord(name, level, __file__, 67, text, (), None)
    assert log_filter.filter(test_record) is expected
    assert log_filter.last_presence is expected_last
