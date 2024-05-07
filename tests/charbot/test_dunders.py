import builtins
import logging
from io import BytesIO

import pytest

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

    Config.clear_cache()  # Ensure the cache is cleared before running the tests
    caplog.set_level(logging.DEBUG)
    monkeypatch.setattr(builtins, "open", mock_open)
    assert Config["calendar"] == {"key": "key"}
    caplog.clear()
    assert Config.get("calendar", "key") == "key"
    log = caplog.record_tuples[0]
    assert log[0] == "charbot.config"
    assert log[1] == logging.INFO
    assert log[2] == "Got key calendar:key from config file."

    caplog.clear()
    with pytest.raises(KeyError):
        Config.get("calendar", "badkey")
    log = caplog.record_tuples[0]
    assert log[0] == "charbot.config"
    assert log[1] == logging.ERROR
    assert log[2] == "Tried to get key calendar:badkey from config file, but it was not found."

    class Test:
        def __str__(self):
            return "Test"

    obj = Test()
    caplog.clear()
    with pytest.raises(TypeError):
        Config.get("calendar", obj)
    log = caplog.record_tuples[0]
    assert log[0] == "charbot.config"
    assert log[1] == logging.ERROR
    assert (
        log[2] == f"Tried to get key calendar:Test from config file, but a non string key {obj!r} of type "
        f"{type(obj)} was passed."
    )
    Config.clear_cache()  # Ensure the cache is cleared after running the tests
