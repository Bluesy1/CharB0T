use super::Player;
use crate::tictactoe::board::{Board, Index, Piece};
use rand::seq::SliceRandom;
use std::fmt::{Display, Error, Formatter};

#[derive(Debug, PartialEq)] // COV_EXCL_LINE
pub struct MinimaxPlayer {
    alpha_beta: bool,
}
impl MinimaxPlayer {
    pub fn new(alpha_beta: bool) -> Self {
        MinimaxPlayer { alpha_beta }
    }
}

#[derive(PartialEq, Eq, PartialOrd, Ord, Clone, Copy, Debug)]
enum GameResult {
    Defeat,
    Draw,
    Victory,
}

impl Display for MinimaxPlayer {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> Result<(), Error> {
        formatter.write_str("Minimax player")
    }
}

// minimax
impl MinimaxPlayer {
    fn minimax_search(&self, board: &Board, piece: Piece) -> (Index, u32) {
        let mut counter = 0;
        let mut best_move = 0;
        let mut indeces: Vec<_> = Board::VALID_INDECES.collect();

        indeces.shuffle(&mut rand::thread_rng());

        self.minimax_step(
            board.clone(),
            piece,
            true,
            0,
            GameResult::Defeat,
            GameResult::Victory,
            &indeces[..],
            &mut best_move,
            &mut counter,
        );
        (best_move, counter)
    }

    #[allow(clippy::too_many_arguments)]
    fn minimax_step(
        &self,
        board: Board,
        piece: Piece,
        maximizing: bool,
        level: u8,
        mut alpha: GameResult,
        mut beta: GameResult,
        indeces: &[Index],
        best_move: &mut Index,
        counter: &mut u32,
    ) -> GameResult {
        use GameResult::*;

        *counter += 1;

        if board.is_victory_for_player(piece) {
            return Victory;
        }
        if board.is_victory_for_player(piece.swap()) {
            return Defeat;
        }
        if board.is_draw() {
            return Draw;
        }

        let mut best_result = if maximizing { Defeat } else { Victory };
        for &index in indeces {
            if !board.cell_is_empty(index) {
                continue;
            }

            let mut new_board = board.clone();
            new_board.place_piece(index, if maximizing { piece } else { piece.swap() });
            let result = self.minimax_step(
                new_board,
                piece,
                !maximizing,
                level + 1,
                alpha,
                beta,
                indeces,
                best_move,
                counter,
            );
            if maximizing && result > best_result || !maximizing && result < best_result {
                best_result = result;
                if level == 0 {
                    *best_move = index;
                }
            }

            // alpha beta pruning
            if self.alpha_beta {
                if maximizing {
                    alpha = std::cmp::max(alpha, best_result);
                    if alpha >= beta {
                        break;
                    }
                } else {
                    beta = std::cmp::min(beta, best_result);
                    if beta <= alpha {
                        break;
                    }
                }
            }
        }
        best_result
    }
}

impl Player for MinimaxPlayer {
    fn play(&self, board: &Board, piece: Piece) -> Index {
        let (best_move, _counter) = self.minimax_search(board, piece);
        //println!("searched {} possible games!", counter);

        best_move
    }
}

// COV_EXCL_START
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_player_no_alphabeta(){
        let player = MinimaxPlayer::new(false);
        let board = Board::new();
        let piece = Piece::X;
        let index = player.play(&board, piece);
        assert!(Board::VALID_INDECES.contains(&index));
        assert_eq!("Minimax player", format!("{}", player));
    }
    #[test]
    fn test_player_alphabeta(){
        let player = MinimaxPlayer::new(true);
        let board = Board::new();
        let piece = Piece::X;
        let index = player.play(&board, piece);
        assert!(Board::VALID_INDECES.contains(&index));
        assert_eq!("Minimax player", format!("{}", player));
    }
}
// COV_EXCL_STOP
