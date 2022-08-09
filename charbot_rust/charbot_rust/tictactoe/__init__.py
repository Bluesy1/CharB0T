# -*- coding: utf-8 -*-
import sys as __sys

from .enums import *  # noqa: F403,F401

# noinspection PyUnresolvedReferences
from ..charbot_rust import tictactoe  # pyright: ignore[reportMissingImports]

if hasattr(tictactoe, "__doc__"):
    __doc__ = tictactoe.__doc__

if hasattr(tictactoe, "__all__"):
    __all__ = (
        "Difficulty",
        *tictactoe.__all__,
    )  # pyright: ignore[reportUnsupportedDunderAll]
    __name: str
    for __name in tictactoe.__all__:
        setattr(__sys.modules[__name__], __name, getattr(tictactoe, __name))  # pyright: ignore[reportUnboundVariable]
    del __name
else:
    __all__ = ("Difficulty",)  # noqa: F405
