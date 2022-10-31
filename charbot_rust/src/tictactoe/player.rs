// SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
// SPDX-License-Identifier: MIT
mod human_player;
mod minimax_player;
mod random_player;
// COV_EXCL_START
use super::board::{Board, Index, Piece};
use std::fmt::{Debug, Display};

pub use human_player::HumanPlayer;
pub use minimax_player::MinimaxPlayer;
pub use random_player::RandomPlayer;
// COV_EXCL_STOP

pub trait Player: Display + Debug {
    fn play(&self, board: &Board, piece: Piece) -> Index;
}

pub fn choose_player(c: &str) -> Option<Box<dyn Player>> {
    match c.to_lowercase().as_str() {
        "human" | "h" => Some(Box::new(HumanPlayer)),
        "minimax" | "m" => Some(Box::new(MinimaxPlayer::new(false))),
        "alphabeta" | "a" => Some(Box::new(MinimaxPlayer::new(true))),
        "random" | "r" => Some(Box::new(RandomPlayer)),
        _ => None,
    }
}

//pub fn random_player() -> Box<dyn Player> {
//    let mut boxes: Vec<Box<dyn Player>> = vec![
//        Box::new(HumanPlayer),
//        Box::new(MinimaxPlayer::new(true)),
//        Box::new(RandomPlayer),
//    ];
//
//    let index = rand::thread_rng().gen_range(0..boxes.len());
//    boxes.remove(index)
//}

// pub fn random_player() -> Box<dyn Player> {
//     match rand::thread_rng().gen_range(0, 2) {
//         0 => Box::new(HumanPlayer),
//         1 => Box::new(MinimaxPlayer),
//         _ => unreachable!(),
//     }
// }


// COV_EXCL_START
#[cfg(test)]
mod tests {
    use super::*;
    use yare::parameterized;

    #[parameterized(
        human_long = {"human", "human"},
        human_short = {"h", "human"},
        minimax_long = {"minimax", "minimax"},
        minimax_short = {"m", "minimax"},
        alphabeta_long = {"alphabeta", "alphabeta"},
        alphabeta_short = {"a", "alphabeta"},
        random_long = {"random", "random"},
        random_short = {"r", "random"},
    )]
    fn test_choose_player(player: &str, expected: &str) {
        choose_player(player).unwrap_or_else(|| panic!("Could not create player {}", expected));
    }
    #[test]
    fn test_choose_player_invalid() {
        assert!(choose_player("not a player").is_none(), "Could create player");
    }
}
// COV_EXCL_STOP
