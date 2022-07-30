use super::Player;
use crate::tictactoe::board::{Board, Index, Piece};
use std::fmt::{Display, Error, Formatter};

#[derive(Debug, PartialEq)] // LCOV_EXCL_LINE
pub struct HumanPlayer;

impl Display for HumanPlayer {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> Result<(), Error> {
        formatter.write_str("Human player")
    }
}

impl Player for HumanPlayer {
    fn play(&self, board: &Board, _: Piece) -> Index {
        Board::VALID_INDECES
            .filter(|index| board.cell_is_empty(*index)).next().unwrap()
    }
}

// LCOV_EXCL_START
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_random_player() {
        let player = HumanPlayer;
        let board = Board::new();
        let index = player.play(&board, Piece::X);
        assert!(Board::VALID_INDECES.contains(&index));
        assert_eq!(0, index);
        assert_eq!("Human player", format!("{}", player));
    }
}
// LCOV_EXCL_STOP
