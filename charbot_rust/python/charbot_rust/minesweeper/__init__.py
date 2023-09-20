# -*- coding: utf-8 -*-
import sys as __sys

# noinspection PyProtectedMember
from charbot_rust.charbot_rust import _minesweeper

if hasattr(_minesweeper, "__doc__"):
    __doc__ = _minesweeper.__doc__

if hasattr(_minesweeper, "__all__"):
    __all__ = (*_minesweeper.__all__,)  # pyright: ignore[reportUnsupportedDunderAll]
    __name: str
    for __name in _minesweeper.__all__:
        setattr(__sys.modules[__name__], __name, getattr(_minesweeper, __name))
    try:
        del __name  # pyright: ignore[reportUnboundVariable]
    except NameError:
        pass

del _minesweeper
