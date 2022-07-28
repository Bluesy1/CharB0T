from enum import Enum, IntEnum

class Difficulty(IntEnum):
    EASY = ...
    MEDIUM = ...
    HARD = ...
    RANDOM = ...

class Piece(Enum):
    """Represents a piece in the game."""

    X: ...
    O: ...
    Empty: ...

    @property
    def value(self) -> str: ...

class Offset(Enum):
    """Represents an offset in the game."""

    TopLeft: ...
    TopMiddle: ...
    TopRight: ...
    MiddleLeft: ...
    MiddleMiddle: ...
    MiddleRight: ...
    BottomLeft: ...
    BottomMiddle: ...
    BottomRight: ...

    @property
    def value(self) -> tuple[int, int]: ...

class Game:
    """A rust based implementation of tictactoe

    Parameters
    ----------
    difficulty : Difficulty
        The difficulty of the game. The default is 'EASY'.
    """

    def __init__(self, difficulty: Difficulty): ...
    def __new__(cls, difficulty: Difficulty) -> "Game": ...
    @property
    def board(self) -> list[Piece]:
        """The board for the game, represented as a list of pieces.

        The grid is as follows::

            -----------
             0 | 1 | 2
            -----------
             3 | 4 | 5
            -----------
             6 | 7 | 8
            -----------
        """
        ...
    def play(self, index: int) -> int | None:
        """Have the player make a move, and have the computer maybe make a move too if the game is not complete.

        Parameters
        ----------
        index: int
            The index of the square to place the piece in.

        Returns
        -------
        int | None
            Return the coputer's move, or None if the computer didn't move
        """
        ...
    def display_commands(self) -> list[tuple[Offset, Piece]]:
        """Needed actions to create an image of teh game from a base empty grid.

        Returns
        -------
        list[tuple[Offset, Piece]]
            A list of tuples representing the commands to create the image of the game.
        """
        ...
    def is_draw(self) -> bool:
        """Check if the game is a draw.

        Returns
        -------
        bool
            True if the game is a draw, False otherwise.
        """
        ...
    def is_victory_for(self) -> Piece | None:
        """Check what piece, if any the game is a victory for.

        Returns
        -------
        Piece | None
            The piece that won the game, or None if the game has no winner..
        """
        ...
    def has_player_won(self) -> bool:
        """Check if the player has won the game.

        Returns
        -------
        bool
            True if the player has won, False otherwise.
        """
        ...
    def has_player_lost(self) -> bool:
        """Check if the player has lost the game.

        Returns
        -------
        bool
            True if the player has lost, False otherwise.
        """
        ...
    def points(self) -> tuple[int, int]:
        """The Participation and Bonus points for the player, or None if the game isn't finished.

        Returns
        -------
        tuple[int, int]
            The participation and bonus points for the player.
        """
        ...
