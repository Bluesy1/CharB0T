use super::Player;
use crate::tictactoe::board::{Board, Index, Piece};
use rand::seq::IteratorRandom;
use std::fmt::{Display, Error, Formatter};

#[derive(Debug, PartialEq, Eq)] // COV_EXCL_LINE
pub struct RandomPlayer;

impl Display for RandomPlayer {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> Result<(), Error> {
        formatter.write_str("Random player")
    }
}

impl Player for RandomPlayer {
    fn play(&self, board: &Board, _: Piece) -> Index {
        //println!("Random pick...");

        Board::VALID_INDICES
            .filter(|index| board.cell_is_empty(*index))
            .choose(&mut rand::rng())
            .unwrap()
    }
}

// COV_EXCL_START
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_random_player() {
        let player = RandomPlayer;
        let board = Board::new();
        let index = player.play(&board, Piece::X);
        assert!(Board::VALID_INDICES.contains(&index));
        assert_eq!("Random player", format!("{}", player));
    }
}
// COV_EXCL_STOP
