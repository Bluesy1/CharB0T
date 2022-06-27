# -*- coding: utf-8 -*-
import builtins
from io import BytesIO

import pytest

from charbot import Config


@pytest.fixture
def unused_toml_bytes(monkeypatch):
    """Mock open() to return a static bytes object."""
    toml = b"""
[postgres]
hast = '0.0.0.0'
user='user'
password='password'
database='databse'

[discord]
token='token'

[discord.webhooks]
calendar = 0
program_logs = 1
errors = 2
giveaway = 3

[discord.messages]
calendar = 0

[discord.channels]
giveaway = 0

[github]
token = 'token'
headers = {'User-Agent' = 'user-agent', 'Accept' = 'application/vnd.github.v3+json'}

[sentry]
dsn = 'dsn'
environment = 'environment'
release = 'release'

[calendar]
key='key'
"""

    class mock_open:
        def __init__(self, path, mode, *args, **kwargs):
            self.path = path
            self.mode = mode

        def __enter__(self):
            return BytesIO(toml)

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(builtins, "open", mock_open)


def test_config(unused_toml_bytes):
    """Test config."""
    assert Config["calendar"] == {"key": "key"}
    assert Config("calendar", "key") == "key"
