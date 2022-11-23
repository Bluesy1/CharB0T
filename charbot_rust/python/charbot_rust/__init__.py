# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from importlib.metadata import metadata as __metadata

# noinspection PyUnresolvedReferences
from ._charbot_rust import *  # pyright: ignore # noqa: F403,F401

# noinspection PyUnresolvedReferences
from . import _charbot_rust

from . import tictactoe, minesweeper

__all__ = ("tictactoe", "minesweeper", "translate")

# noinspection PyUnresolvedReferences
__doc__ = _charbot_rust.__doc__
translate = _charbot_rust.translate
# noinspection PyUnresolvedReferences
del _charbot_rust
__charbot_metadata = __metadata("charbot_rust")
__version__ = __charbot_metadata["Version"]
__author__ = __charbot_metadata["Author"]
__author_email__ = __charbot_metadata["Author-email"]
