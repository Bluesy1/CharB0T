from typing import Literal


__all__ = ("Cell",)

type ContentType = None | bool | Literal[1, 2, 3, 4, 5, 6, 7, 8]


class Cell:
    __slots__ = ("_revealed", "_marked", "content")

    def __init__(self, content: ContentType = None) -> None:
        self._revealed = False
        self._marked = False
        self.content: ContentType = content

    @property
    def revealed(self) -> bool:
        return self._revealed

    @revealed.setter
    def revealed(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f"Expected bool, got {type(value)!r} instead!")
        self._revealed = value

    @property
    def marked(self) -> bool:
        return self._marked

    @marked.setter
    def marked(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f"Expected bool, got {type(value)!r} instead!")
        self._marked = value
