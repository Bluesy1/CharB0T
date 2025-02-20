import sys as __sys
from contextlib import suppress as __suppress

from .._rust import _tictactoe
from .enums import Difficulty


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
    with __suppress(NameError):
        del __name  # pyright: ignore[reportPossiblyUnboundVariable]
else:
    __all__ = ("Difficulty",)

del _tictactoe
