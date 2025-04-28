from enum import Enum, StrEnum


class Piece(StrEnum):
    X = "X"
    O = "O"
    Empty = " "

    def swap(self) -> "Piece":
        match self:
            case Piece.X:
                return Piece.O
            case Piece.O:
                return Piece.X
            case _:
                return Piece.Empty


class Offset(Enum):
    TopLeft = (0, 0)
    TopMiddle = (179, 0)
    TopRight = (355, 0)
    MiddleLeft = (0, 179)
    MiddleMiddle = (179, 179)
    MiddleRight = (355, 179)
    BottomLeft = (0, 357)
    BottomMiddle = (179, 357)
    BottomRight = (355, 357)


WINNING_INDICES: list[tuple[int, int, int]] = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]


class Board:
    VALID_INDICES = range(9)

    def __init__(self) -> None:
        self.board: list[Piece] = [Piece.Empty] * 9
        self.n_pieces: int = 0

    @property
    def get_board(self) -> list[Piece]:
        return self.board

    @staticmethod
    def is_valid_index(index: int) -> bool:
        return index in Board.VALID_INDICES

    def cell_is_empty(self, index: int) -> bool:
        return self.board[index] == Piece.Empty

    def place_piece(self, index: int, piece: Piece) -> bool:
        if not self.cell_is_empty(index):
            raise ValueError(f"Tried to place a piece on an occupied cell, int: {index}")
        self.board[index] = piece
        self.n_pieces += 1
        return True

    def is_draw(self) -> bool:
        return self.n_pieces >= 9

    def is_victory_for_player(self, player: Piece) -> bool:
        for a, b, c in WINNING_INDICES:
            if self.board[a] == player and self.board[b] == player and self.board[c] == player:
                return True
        return False

    def is_victory(self) -> Piece | None:
        if self.is_victory_for_player(Piece.X):
            return Piece.X
        elif self.is_victory_for_player(Piece.O):
            return Piece.O
        return None

    def format_cell(self, index: int) -> str:
        if self.board[index] == Piece.Empty:
            return str(index)
        return str(self.board[index])

    def __str__(self) -> str:
        rows = []
        for row in range(0, 9, 3):
            rows.append("".join(self.format_cell(i) for i in range(row, row + 3)))
        return "\n".join(rows)
