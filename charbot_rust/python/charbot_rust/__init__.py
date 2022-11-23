# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
# noinspection PyProtectedMember
from charbot_rust import _charbot_rust

from . import tictactoe, minesweeper

__doc__ = _charbot_rust.__doc__
__title__ = "charbot_rust"
__author__ = "Bluesy1"
__license__ = "MIT"
__copyright__ = "Copyright 2022-present Bluesy1"
__version__ = __import__("importlib.metadata").metadata.version(__title__)
__all__ = ("tictactoe", "minesweeper", "translate")
translate = _charbot_rust.translate

# noinspection PyUnresolvedReferences
del _charbot_rust
