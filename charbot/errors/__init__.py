# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""Custom errors for the bot."""

__all__ = ("WrongChannelError", "NoPoolFound", "MissingProgramRole")

from .channel import WrongChannelError
from .pools import NoPoolFound
from .roles import MissingProgramRole
