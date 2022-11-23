# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT
import sys as __sys

from .enums import *  # noqa: F403,F401

from .. import _tictactoe  # type: ignore

if hasattr(_tictactoe, "__doc__"):
    __doc__ = _tictactoe.__doc__

if hasattr(_tictactoe, "__all__"):
    __all__ = (
        "Difficulty",
        *_tictactoe.__all__,
    )  # pyright: ignore[reportUnsupportedDunderAll]
    __name: str
    for __name in _tictactoe.__all__:
        setattr(__sys.modules[__name__], __name, getattr(_tictactoe, __name))
    try:
        del __name  # pyright: ignore[reportUnboundVariable]
    except NameError:
        pass
else:
    __all__ = ("Difficulty",)  # noqa: F405

del _tictactoe
