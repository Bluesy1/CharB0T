# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Custom errors for the bot."""

from typing import Literal

__all__ = ("WrongChannelError", "NoPoolFound", "MissingProgramRole")

_LanguageTag = Literal["en-US", "es-ES", "fr", "nl"]

from .channel import WrongChannelError  # noqa: E402
from .pools import NoPoolFound  # noqa: E402
from .roles import MissingProgramRole  # noqa: E402
