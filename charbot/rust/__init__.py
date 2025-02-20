from importlib import metadata as _metadata

from . import _rust, minesweeper, tictactoe


__doc__ = _rust.__doc__
__title__ = "charbot_rust"
__author__ = "Bluesy1"
__license__ = "MIT"
__copyright__ = "Copyright 2022-present Bluesy1"
__version__ = _metadata.version(__title__)
__all__ = ("tictactoe", "minesweeper")

del _rust
