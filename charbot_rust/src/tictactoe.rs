mod board; // COV_EXCL_LINE
mod player;

use rand::prelude::*;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use crate::tictactoe::board::{Offset, Piece};
use crate::points::Points;

#[derive(Debug, PartialEq)] // COV_EXCL_LINE
pub enum Difficulty {
    Easy,
    Medium,
    Hard,
    Random,
}

impl Difficulty {
    fn extract(obj: i32) -> Result<Self, String> {
         match obj {
            1 => Ok(Difficulty::Easy),
            2 => Ok(Difficulty::Medium),
            3 => Ok(Difficulty::Hard),
            4 => Ok(Difficulty::Random),
            _ => Err("Invalid difficulty value".to_string()),
        }
    }
}

// COV_EXCL_START
#[pyclass(module = "tictactoe")]
#[derive(Debug)]
struct Game {
    pub board: board::Board,
    pub player_x: Box<dyn player::Player>,
    pub player_o: Box<dyn player::Player>,
    pub human_first: bool,
    points: Points,
}
// COV_EXCL_STOP

unsafe impl Send for Game {}

impl Game {
        fn new(difficulty: i32, mut rng: StdRng) -> Result<Self, String> {
        let difficulty = Difficulty::extract(difficulty)?; // COV_EXCL_LINE
        let points = Points::new(&difficulty);
        let x: Option<Box<dyn player::Player>>;
        let o: Option<Box<dyn player::Player>>;
        let mut human_first: bool = true;
        match difficulty {
            Difficulty::Easy => {
                x = player::choose_player("h");
                o = player::choose_player("r");
            },
            Difficulty::Medium => {
                if rng.gen_bool(0.5){ // COV_EXCL_LINE
                    x = player::choose_player("h");
                    o = player::choose_player("m");
                } else {
                    x = player::choose_player("m"); // COV_EXCL_LINE
                    o =player::choose_player("h"); // COV_EXCL_LINE
                    human_first = false; // COV_EXCL_LINE

                }
            },
            Difficulty::Hard => {
                x = player::choose_player("a");
                o = player::choose_player("h");
                human_first = false;
            },
            Difficulty::Random => {
                let comp_mode: &str = vec!["m", "a", "r"].choose(&mut rng).unwrap();
                let chance: f64 = match comp_mode {
                    "m" => {0.5}, // COV_EXCL_LINE
                    "a" => {0.25},
                    "r" => {0.75}, // COV_EXCL_LINE
                    _ => {0.0} // COV_EXCL_LINE
                };
                if rng.gen_bool(chance) { // COV_EXCL_LINE
                    x = player::choose_player(comp_mode);
                    o = player::choose_player("h");
                    human_first = false;

                } else {
                    x = player::choose_player("h"); // COV_EXCL_LINE
                    o = player::choose_player(comp_mode); // COV_EXCL_LINE
                }
            },
        };
        match (x, o) { // COV_EXCL_LINE
            (Some(player_x), Some(player_o)) => {
                let mut game = Game{
                    board: board::Board::new(),
                    player_x,
                    player_o,
                    human_first,
                    points
                    };
                if !human_first {
                    let action = game.player_x.play(&game.board, Piece::X);
                    game.board.place_piece(action, Piece::X);
                }
                Ok(game)
            },
            _ => {Err("Unexpected Logic Error".to_string())} // COV_EXCL_LINE
        }
    } // COV_EXCL_LINE
}

#[pymethods] // COV_EXCL_LINE
impl Game {
    #[getter]
    fn board(&self) -> PyResult<Vec<Piece>> {
        Ok(self.board.board.to_vec())
    }

    #[new]
    fn __new__(difficulty: i32) -> PyResult<Self> { // COV_EXCL_LINE
        Self::new(difficulty, StdRng::from_entropy())
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))
    }


    fn play(&mut self, index: board::Index) -> Option<board::Index> {
        let human = match self.human_first {
            true => Piece::X,
            false => Piece::O,
        };
        let computer = match self.human_first {
            true => &self.player_o,
            false => &self.player_x,
        };
        let computer_piece = match self.human_first {
            true => Piece::O,
            false => Piece::X,
        };
        self.board.place_piece(index, human);
        if self.board.is_victory_for_player(human) {
            return None;
        }
        let comp_move = computer.play(&self.board, computer_piece);
        self.board.place_piece(comp_move, computer_piece);
        Some(comp_move)
    }

    fn display_commands(&self) -> Vec<(Offset, Piece)> {
        let mut commands = Vec::new();
        for i in 0..9 { // COV_EXCL_LINE
            commands.push((Offset::new(i).unwrap(), self.board.board[i])); // COV_EXCL_LINE
        }
        commands
    }

    fn is_draw(&self) -> bool {
        self.board.is_draw()
    }

    fn is_victory_for(&self) -> Option<Piece> {
        self.board.is_victory()
    }

    fn has_player_won(&self) -> bool {
        if self.human_first{
            self.board.is_victory_for_player(Piece::X)
        } else {
            self.board.is_victory_for_player(Piece::O)
        }
    }

    fn has_player_lost(&self) -> bool {
        if self.human_first{
            self.board.is_victory_for_player(Piece::O)
        } else {
            self.board.is_victory_for_player(Piece::X)
        }
    }

    fn points(&self) -> (i8, i8) {
        if self.is_draw() {
            self.points.draw
        } else if self.has_player_won() {
            self.points.win
        } else {
            self.points.loss
        }
    }
}

// COV_EXCL_START
const DOCSTRING: &str = "Rust based reimplementation of tictactoe";

pub(crate) fn register_tictactoe(py: Python, m: &PyModule) -> PyResult<()> {
    let tictactoe = PyModule::new(py, "tictactoe")?;
    tictactoe.add_class::<Game>()?;
    tictactoe.add_class::<Piece>()?;
    tictactoe.add_class::<Offset>()?;
    tictactoe.add("__doc__", DOCSTRING)?;
    m.add_submodule(tictactoe)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dificulty() {
        Difficulty::extract(0).expect_err("Expected error");
        let difficulty = Difficulty::extract(1).unwrap();
        assert_eq!(difficulty, Difficulty::Easy);
        let difficulty = Difficulty::extract(2).unwrap();
        assert_eq!(difficulty, Difficulty::Medium);
        let difficulty = Difficulty::extract(3).unwrap();
        assert_eq!(difficulty, Difficulty::Hard);
        let difficulty = Difficulty::extract(4).unwrap();
        assert_eq!(difficulty, Difficulty::Random);
        Difficulty::extract(5).expect_err("Expected error");
    }

    #[test]
    fn board() {
        Game::__new__(0).expect_err("Expected error");
        Game::__new__(5).expect_err("Expected error");
        let game = Game::__new__(1).expect("Failed to create game");
        let board_as_vec = game.board().expect("Failed to get board");
        assert_eq!(board_as_vec.len(), 9);
        for i in 0..9 {
            assert_eq!(board_as_vec[i as usize], Piece::Empty);
        }
    }

    #[test]
    fn creator() {
        Game::new(5, StdRng::from_entropy()).expect_err("Created game with invalid difficulty");
        Game::new(0, StdRng::from_entropy()).expect_err("Created game with invalid difficulty");
        let easy = Game::new(1, StdRng::from_entropy()).expect("Failed to create game");
        assert!(easy.human_first);
        let medium = Game::new(2, StdRng::from_seed([0; 32])).expect("Failed to create game");
        assert!(medium.human_first);
        let hard = Game::new(3, StdRng::from_seed([0; 32])).expect("Failed to create game");
        assert!(!hard.human_first);
        let random = Game::new(4, StdRng::from_seed([0; 32])).expect("Failed to create game");
        assert!(!random.human_first);
        let random = Game::new(4, StdRng::from_seed([1; 32])).expect("Failed to create game");
        assert!(!random.human_first);
    }

    #[test]
    fn play() {
        let mut human_first = Game::new(1, StdRng::from_entropy()).expect("Failed to create game");
        let mut computer_first = Game::new(3, StdRng::from_entropy()).expect("Failed to create game");
        human_first.board.board = [Piece::X, Piece::X, Piece::Empty, Piece::Empty, Piece::O, Piece::Empty, Piece::O, Piece::Empty, Piece::Empty];
        assert_eq!(None, human_first.play(2));
        if computer_first.board.cell_is_empty(0) {
            computer_first.play(0).expect("Failed to play");
        } else {
            computer_first.play(1).expect("Failed to play");
        }

    }
    #[test]
    fn display() {
        let mut game = Game::new(1, StdRng::from_entropy()).expect("Failed to create game");
        game.play(1).expect("Failed to play");
        let commands = game.display_commands();
        assert_eq!(commands.len(), 9);
        for (i ,(_, command)) in commands.iter().enumerate() {
            if game.board.cell_is_empty(i) {
                assert_eq!(command, &Piece::Empty);
            } else {
                assert_ne!(command, &Piece::Empty);
            }
        }
    }
    #[test]
    fn win_cases() {
        let human_first = Game::new(1, StdRng::from_entropy()).expect("Failed to create game");
        let computer_first = Game::new(3, StdRng::from_entropy()).expect("Failed to create game");
        assert!(!human_first.is_draw());
        assert!(!computer_first.is_draw());
        assert_eq!(None, human_first.is_victory_for());
        assert_eq!(None, computer_first.is_victory_for());
        assert!(!human_first.has_player_won());
        assert!(!computer_first.has_player_won());
        assert!(!human_first.has_player_lost());
        assert!(!computer_first.has_player_lost());
    }
    #[test]
    fn points() {
        let mut game = Game::new(1, StdRng::from_entropy()).expect("Failed to create game");
        assert_eq!(game.points(), game.points.loss, "1");
        game.board.board = [Piece::X, Piece::X, Piece::X, Piece::Empty, Piece::O, Piece::Empty, Piece::O, Piece::Empty, Piece::Empty];
        assert_eq!(game.points(), game.points.win, "2");
        game.board.n_pieces = 9;
        assert_eq!(game.points(), game.points.draw, "3");
    }
}
// COV_EXCL_END
