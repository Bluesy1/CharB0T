mod human_player;
mod minimax_player;
mod random_player;
// GCOVR_EXCL_START
use super::board::{Board, Index, Piece};
use std::fmt::{Debug, Display};

pub use human_player::HumanPlayer;
pub use minimax_player::MinimaxPlayer;
pub use random_player::RandomPlayer;
// GCOVR_EXCL_STOP

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


// GCOVR_EXCL_START
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_choose_player() {
        choose_player("human").expect("Could not create human player");
        choose_player("minimax").expect("Could not create minimax player");
        choose_player("alphabeta").expect("Could not create alphabeta player");
        choose_player("random").expect("Could not create random player");
        choose_player("h").expect("Could not create human player");
        choose_player("m").expect("Could not create minimax player");
        choose_player("a").expect("Could not create alphabeta player");
        choose_player("r").expect("Could not create random player");
        assert!(choose_player("not a player").is_none(), "Could create player");
    }
}
// GCOVR_EXCL_STOP
