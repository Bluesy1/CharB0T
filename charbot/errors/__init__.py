# -*- coding: utf-8 -*-
"""Custom errors for the bot."""

from typing import Literal

__all__ = ("WrongChannelError", "NoPoolFound", "MissingProgramRole")

_LanguageTag = Literal["en-US", "es-ES", "fr", "nl"]

from .channel import WrongChannelError  # noqa: E402
from .pools import NoPoolFound  # noqa: E402
from .roles import MissingProgramRole  # noqa: E402
