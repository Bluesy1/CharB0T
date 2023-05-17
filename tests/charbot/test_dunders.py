# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

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

    caplog.set_level(logging.DEBUG)
    monkeypatch.setattr(builtins, "open", mock_open)
    assert Config["calendar"] == {"key": "key"}
    caplog.clear()
    assert Config.get("calendar", "key") == "key"
    log = caplog.record_tuples[0]
    assert log[0] == "charbot.config"
    assert log[1] == logging.INFO
    assert log[2] == "Got key calendar:key from config file."

    with pytest.raises(KeyError):
        caplog.clear()
        Config.get("calendar", "badkey")
    log = caplog.record_tuples[0]
    assert log[0] == "charbot.config"
    assert log[1] == logging.ERROR
    assert log[2] == "Tried to get key calendar:badkey from config file, but it was not found."

    class Test:  # skipcq: PY-D0002
        def __str__(self):
            return "Test"

    obj = Test()
    with pytest.raises(TypeError):
        caplog.clear()
        Config.get("calendar", obj)
    log = caplog.record_tuples[0]
    assert log[0] == "charbot.config"
    assert log[1] == logging.ERROR
    assert (
        log[2] == f"Tried to get key calendar:Test from config file, but a non string key {obj!r} of type "
        f"{type(obj)} was passed."
    )
