mod human_player;
mod minimax_player;
mod random_player;
// GCOVR_EXCL_START
use super::board::{Board, Index, Piece};
use std::fmt::Display;

pub use human_player::HumanPlayer;
pub use minimax_player::MinimaxPlayer;
pub use random_player::RandomPlayer;
// GCOVR_EXCL_STOP

pub trait Player: Display {
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


// GCOVR_EXCL_START
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_choose_player() {
        assert_eq!(
            Some(Box::new(HumanPlayer)),
            choose_player("h")
        );
        assert_eq!(
            Some(Box::new(MinimaxPlayer::new(false))),
            choose_player("m")
        );
        assert_eq!(
            Some(Box::new(MinimaxPlayer::new(true))),
            choose_player("a")
        );
        assert_eq!(
            Some(Box::new(RandomPlayer)),
            choose_player("r")
        );
        assert_eq!(None, choose_player("x"));
    }
}
// GCOVR_EXCL_STOP
