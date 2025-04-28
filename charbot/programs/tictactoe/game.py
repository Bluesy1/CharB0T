import random
from enum import IntEnum
from typing import NamedTuple, assert_never

from .board import Board, Offset, Piece
from .players import HumanPlayer, MinimaxPlayer, Player, RandomPlayer


class Points(NamedTuple):
    win: tuple[int, int]
    draw: tuple[int, int]
    loss: tuple[int, int]


class Difficulty(IntEnum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    RANDOM = 4

    @property
    def points(self):  # pragma: no cover
        match self:
            case self.EASY | self.RANDOM:
                return Points((1, 1), (1, 0), (0, 0))
            case self.MEDIUM:
                return Points((2, 2), (2, 0), (0, 0))
            case self.HARD:
                return Points((2, 3), (2, 1), (0, 0))
            case unexpected:  # pragma: no cover
                assert_never(unexpected)


class Game:
    player_x: Player
    player_o: Player

    def __init__(self, difficulty: Difficulty) -> None:
        rng = random.Random()
        self.board = Board()
        self.human_first = True
        self.difficulty = difficulty

        match difficulty:
            case Difficulty.EASY:
                self.player_x = HumanPlayer()
                self.player_o = RandomPlayer()
            case Difficulty.MEDIUM:
                if rng.random() < 0.5:
                    self.player_x = HumanPlayer()
                    self.player_o = MinimaxPlayer(alpha_beta=False)
                else:
                    self.player_x = MinimaxPlayer(alpha_beta=False)
                    self.player_o = HumanPlayer()
                    self.human_first = False
            case Difficulty.HARD:
                self.player_x = MinimaxPlayer(alpha_beta=True)
                self.player_o = HumanPlayer()
                self.human_first = False
            case Difficulty.RANDOM:
                comp_mode = random.choice(["m", "a", "r"])
                chance = {"m": 0.5, "a": 0.25, "r": 0.75}[comp_mode]
                if rng.random() < chance:  # pragma: no cover
                    if comp_mode == "r":
                        self.player_x = RandomPlayer()
                    else:
                        self.player_x = MinimaxPlayer(alpha_beta=comp_mode == "a")
                    self.player_o = HumanPlayer()
                    self.human_first = False
                else:
                    self.player_x = HumanPlayer()
                    if comp_mode == "r":  # pragma: no cover
                        self.player_o = RandomPlayer()
                    else:
                        self.player_o = MinimaxPlayer(alpha_beta=comp_mode == "a")
            case unexpected:  # pragma: no cover
                assert_never(unexpected)

        if not self.human_first and isinstance(self.player_x, MinimaxPlayer):
            action = self.player_x.play(self.board, Piece.X)
            self.board.place_piece(action, Piece.X)

    def points(self) -> tuple[int, int]:
        if self.is_draw():
            return self.difficulty.points.draw
        if self.has_player_won():
            return self.difficulty.points.win
        return self.difficulty.points.loss

    def play(self, index: int) -> int | None:
        human = Piece.X if self.human_first else Piece.O
        computer = self.player_o if self.human_first else self.player_x
        computer_piece = Piece.O if self.human_first else Piece.X

        self.board.place_piece(index, human)

        if self.board.is_victory_for_player(human) or self.board.is_draw():
            return None

        move = computer.play(self.board, computer_piece)
        self.board.place_piece(move, computer_piece)
        return move

    def display_commands(self):
        return [(offset.value, spot) for offset, spot in zip(Offset, self.board.board)]

    def is_draw(self) -> bool:
        return self.board.is_draw()

    def is_victory_for(self):
        return self.board.is_victory()

    def has_player_won(self) -> bool:
        return self.board.is_victory_for_player(Piece.X if self.human_first else Piece.O)

    def has_player_lost(self) -> bool:
        return self.board.is_victory_for_player(Piece.O if self.human_first else Piece.X)
