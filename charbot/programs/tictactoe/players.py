import random
from enum import Enum
from typing import Protocol

from .board import Board, Piece


class GameResult(Enum):
    Defeat = 0
    Draw = 1
    Victory = 2


class Player(Protocol):
    def play(self, board: Board, piece: Piece) -> int: ...


class RandomPlayer(Player):
    def play(self, board: Board, piece: Piece) -> int:
        moves = [i for i in range(9) if board.cell_is_empty(i)]
        return random.choice(moves)


class HumanPlayer(Player):
    def play(self, board: Board, piece: Piece) -> int:
        return NotImplemented


class MinimaxPlayer(Player):
    def __init__(self, alpha_beta: bool) -> None:
        self.alpha_beta = alpha_beta

    def play(self, board: Board, piece: Piece) -> int:
        best_move, _ = self.minimax_search(board, piece)
        return best_move

    def minimax_search(self, board: Board, piece: Piece) -> tuple[int, int]:
        counter_ref = [0]
        best_move_ref = [0]
        indices = list(Board.VALID_INDICES)
        random.shuffle(indices)

        self.minimax_step(
            board=board,
            piece=piece,
            maximizing=True,
            level=0,
            alpha=GameResult.Defeat,
            beta=GameResult.Victory,
            indices=indices,
            best_move_ref=best_move_ref,
            counter_ref=counter_ref,
        )
        return best_move_ref[0], counter_ref[0]

    def minimax_step(
        self,
        board: Board,
        piece: Piece,
        maximizing: bool,
        level: int,
        alpha: GameResult,
        beta: GameResult,
        indices: list[int],
        best_move_ref: list[int],
        counter_ref: list[int],
    ) -> GameResult:
        counter_ref[0] += 1

        if board.is_victory_for_player(piece):
            return GameResult.Victory
        if board.is_victory_for_player(piece.swap()):
            return GameResult.Defeat
        if board.is_draw():
            return GameResult.Draw

        best_result = GameResult.Defeat if maximizing else GameResult.Victory

        for index in indices:
            if not board.cell_is_empty(index):
                continue

            new_board = Board()
            new_board.board = board.board.copy()
            new_board.n_pieces = board.n_pieces
            new_board.place_piece(index, piece if maximizing else piece.swap())

            result = self.minimax_step(
                new_board,
                piece,
                not maximizing,
                level + 1,
                alpha,
                beta,
                indices,
                best_move_ref,
                counter_ref,
            )

            if (maximizing and result.value > best_result.value) or (
                not maximizing and result.value < best_result.value
            ):
                best_result = result
                if level == 0:
                    best_move_ref[0] = index

            # Alpha-beta pruning
            if self.alpha_beta:
                if maximizing:
                    alpha = max(alpha, best_result, key=lambda x: x.value)
                    if alpha.value >= beta.value:
                        break
                else:
                    beta = min(beta, best_result, key=lambda x: x.value)
                    if beta.value <= alpha.value:
                        break

        return best_result
