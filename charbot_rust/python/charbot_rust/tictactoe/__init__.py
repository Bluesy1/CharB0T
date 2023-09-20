# -*- coding: utf-8 -*-
import sys as __sys

from .enums import *  # noqa: F403,F401

# noinspection PyProtectedMember
from charbot_rust.charbot_rust import _tictactoe

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
