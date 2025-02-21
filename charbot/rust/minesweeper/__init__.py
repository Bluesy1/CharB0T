import sys as __sys
from contextlib import suppress as __suppress

from .._rust import _minesweeper


if hasattr(_minesweeper, "__doc__"):
    __doc__ = _minesweeper.__doc__

if hasattr(_minesweeper, "__all__"):
    __all__ = (*_minesweeper.__all__,)  # pyright: ignore[reportUnsupportedDunderAll]
    __name: str
    for __name in _minesweeper.__all__:
        setattr(__sys.modules[__name__], __name, getattr(_minesweeper, __name))
    with __suppress(NameError):
        del __name  # pyright: ignore[reportPossiblyUnboundVariable]

del _minesweeper
