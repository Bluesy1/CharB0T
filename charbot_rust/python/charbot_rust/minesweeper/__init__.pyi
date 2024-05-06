# -*- coding: utf-8 -*-
import typing as __typing
import enum as __enum

@__typing.type_check_only
class Selected:
    """Represents an internally selected cell.

    It has 2 attributes::

        marked: bool
            Whether the cell is flagged or not.
        revealed: bool
            Whether the cell is revealed or not.
    """

    marked: bool
    revealed: bool

class RevealResult(__enum.Enum):
    """An enum that represents the result of a reveal operation.

    Flagged:
        The cell was flagged, the flag was removed, but to reveal the cell, call again.
    Mine:
        The cell was a mine, the game is over.
    Empty:
        The cell was empty, floodfill has occurred.
    Number:
        The cell was adjacent to mines.
    """

    Flagged: int = ...
    Mine: int = ...
    Empty: int = ...
    Number: int = ...

class ChordResult(__enum.Enum):
    """An enum that represents the result of a chard operation.

    Failed:
        The cell was not revealed, not a number, or didn't have the appropriate amount of flags.
    Success:
        The chord was performed properly and no mines were revealed.
    Death:
        The chord was performed, but a mine was revealed, ending the game.
    """

    Failed: int = ...
    Success: int = ...
    Death: int = ...

class Game:
    """A class that represents a game of minesweeper.

    Parameters
    ----------
    width: int
        The width of the game board.
    height: int
        The height of the game board.
    mines: int
        The number of mines in the game.
    """

    def __init__(self, width: int, height: int, mines: int) -> None: ...
    def __new__(cls, width: int, height: int, mines: int) -> "Game": ...
    @classmethod
    def beginner(cls) -> "Game":
        """Returns a beginner game, 8x8, 10 mines."""
        ...

    @classmethod
    def intermediate(cls) -> "Game":
        """Returns an intermediate game, 16x16, 40 mines."""
        ...

    @classmethod
    def expert(cls) -> "Game":
        """Returns an expert game, 22x22, 100 mines."""
        ...

    @classmethod
    def super_expert(cls) -> "Game":
        """Returns a super expert game, 25x25, 130 mines."""
        ...

    @property
    def points(self) -> tuple[int, int]:
        """Returns the number of points the player has.

        Returns
        -------
        points: tuple[int, int]
            The number of points the player gets as (participation, bonus).
        """
        ...

    @property
    def flagged_count(self) -> int:
        """Returns the number of flagged cells.

        Returns
        -------
        flagged: int
            The number of flagged cells.
        """
        ...

    @property
    def mine_count(self) -> int:
        """Returns the number of mines in the game.

        Returns
        -------
        mines: int
            The number of mines in the game.
        """
        ...

    @property
    def size(self) -> int:
        """Returns the size of the game board.

        Returns
        -------
        size: int
            The size of the game board.
        """
        ...

    @property
    def width(self) -> int:
        """Returns the width of the game board.

        Returns
        -------
        width: int
            The width of the game board.
        """
        ...

    @property
    def height(self) -> int:
        """Returns the height of the game board.

        Returns
        -------
        height: int
            The height of the game board.
        """
        ...

    @property
    def x(self) -> int:
        """Returns the x coordinate of the selected cell.

        Returns
        -------
        x: int
            The x coordinate of the selected cell.
        """
        ...

    @property
    def y(self) -> int:
        """Returns the y coordinate of the selected cell.

        Returns
        -------
        y: int
            The y coordinate of the selected cell.
        """
        ...

    def draw(self) -> tuple[list[int], tuple[int, int]]:
        """Draws the board and returns it alongside its size.

        The return is in the form of a tuple of the form::

            (board: list[int], (width: int, height: int))

        The `list[int]` is effectively an array of bytes, it just needs a cast to `bytes` or `bytearray`.

        Returns
        -------
        tuple[list[int], tuple[int, int]]
            The board and its size.
        """
        ...

    def change_row(self, row: int) -> Selected:
        """Change the row the internal cursor is on.

        Parameters
        ----------
        row: int
            The row to change to.

        Returns
        -------
        cell: Selected
            The important properties of the cell that is now selected.
        """
        ...

    def change_col(self, col: int) -> Selected:
        """CHange the column the internal cursor is on.

        Parameters
        ----------
        col: int
            The column to change to.

        Returns
        -------
        cell: Selected
            The important properties of the cell that is now selected.
        """
        ...

    def toggle_flag(self) -> bool:
        """Toggles the flag on the cell the internal cursor is on.

        Returns
        -------
        success: bool
            Whether the flag was toggled or not. If false, the cell was already revealed.
        """
        ...

    def reveal(self) -> RevealResult:
        """Reveals the cell the internal cursor is on.

        Returns
        -------
        result: RevealResult
            The result of the reveal operation.
        """
        ...

    def chord(self) -> ChordResult:
        """Attempt to chord the cell the internal cursor is on.

        Returns
        -------
        result: ChordResult
            The result of the chord operation.
        """
        ...

    def is_win(self) -> bool:
        """Check if the game is won.

        Returns
        -------
        win: bool
            True if the game is won, False otherwise.
        """
        ...

    def quit(self) -> None:
        """Quit the game.

        Functionally all this does is reveal all cells, ending the game.
        """
        ...

    def restart(self) -> None:
        """Restart the game.

        Functionally all this does is reset the game, clearing all moves.
        """
        ...
