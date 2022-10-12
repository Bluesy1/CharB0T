# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Custom errors for the bot."""

__all__ = ("WrongChannelError", "NoPoolFound", "MissingProgramRole")

from .channel import WrongChannelError
from .pools import NoPoolFound
from .roles import MissingProgramRole
