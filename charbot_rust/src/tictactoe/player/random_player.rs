use super::Player;
use crate::tictactoe::board::{Board, Index, Piece};
use rand::seq::IteratorRandom;
use std::fmt::{Display, Error, Formatter};

pub struct RandomPlayer;

impl Display for RandomPlayer {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> Result<(), Error> {
        formatter.write_str("Random player")
    }
}

impl Player for RandomPlayer {
    fn play(&self, board: &Board, _: Piece) -> Index {
        //println!("Random pick...");

        Board::VALID_INDECES
            .filter(|index| board.cell_is_empty(*index))
            .choose(&mut rand::thread_rng())
            .unwrap()
    }
}
