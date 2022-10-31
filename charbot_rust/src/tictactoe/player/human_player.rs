// SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
// SPDX-License-Identifier: MIT
use super::Player;
use crate::tictactoe::board::{Board, Index, Piece};
use std::fmt::{Display, Error, Formatter};

#[derive(Debug, PartialEq, Eq)] // COV_EXCL_LINE
pub struct HumanPlayer;

impl Display for HumanPlayer {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> Result<(), Error> {
        formatter.write_str("Human player")
    }
}

impl Player for HumanPlayer {
    #[allow(const_item_mutation)]
    fn play(&self, board: &Board, _: Piece) -> Index {
        Board::VALID_INDECES.find(|index| board.cell_is_empty(*index)).unwrap()
    }
}

// COV_EXCL_START
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
// COV_EXCL_STOP
