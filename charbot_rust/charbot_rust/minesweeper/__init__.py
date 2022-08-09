# -*- coding: utf-8 -*-
import sys as __sys

# noinspection PyUnresolvedReferences
from ..charbot_rust import minesweeper  # pyright: ignore[reportMissingImports]

if hasattr(minesweeper, "__doc__"):
    __doc__ = minesweeper.__doc__

if hasattr(minesweeper, "__all__"):
    __all__ = (*minesweeper.__all__,)  # pyright: ignore[reportUnsupportedDunderAll]
    __name: str
    for __name in minesweeper.__all__:
        setattr(__sys.modules[__name__], __name, getattr(minesweeper, __name))
    del __name
