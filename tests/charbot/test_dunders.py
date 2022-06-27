# -*- coding: utf-8 -*-
import builtins
from io import BytesIO

from charbot import Config


def test_config(monkeypatch):
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

    monkeypatch.setattr(builtins, "open", mock_open)
    assert Config["calendar"] == {"key": "key"}
    assert Config("calendar", "key") == "key"
