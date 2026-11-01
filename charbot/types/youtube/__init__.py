"""Youtube API Models"""

from typing import TypedDict

from . import playlists


__all__ = (
    "Error",
    "playlists",
)


class Error(TypedDict):
    code: int
    message: str
    errors: dict[str, str]
