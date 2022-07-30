mod board;
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

#[pyclass(module = "tictactoe")]
struct Game {
    pub board: board::Board,
    pub player_x: Box<dyn player::Player>,
    pub player_o: Box<dyn player::Player>,
    pub human_first: bool,
    points: Points,
}

unsafe impl Send for Game {}

impl Game {
        fn new(difficulty: i32, mut rng: StdRng) -> Result<Self, String> {
        let difficulty = Difficulty::extract(difficulty)?;
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
                if rng.gen_bool(0.5){
                    x = player::choose_player("h");
                    o = player::choose_player("m");
                } else {
                    x = player::choose_player("m");
                    o =player::choose_player("h");
                    human_first = false;

                }
            },
            Difficulty::Hard => {
                x = player::choose_player("a");
                o = player::choose_player("h");
                human_first = false;
            },
            Difficulty::Random => {
                let comp_mode: &str = match vec!["m", "a", "r"].choose(&mut rng){
                    Some(s) => {*s},
                    None => {return Err("Logic error occurred".to_string());}
                };
                let chance: f64 = match comp_mode {
                    "m" => {0.5},
                    "a" => {0.25},
                    "r" => {0.75},
                    _ => {0.0}
                };
                if rng.gen_bool(chance) {
                    x = player::choose_player("h");
                    o = player::choose_player(comp_mode);
                } else {
                    x = player::choose_player(comp_mode);
                    o = player::choose_player("h");
                }
            },
        };
        match (x, o) {
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
            _ => {Err("Unexpected Logic Error".to_string())}
        }
    }
}

#[pymethods]
impl Game {
    #[getter]
    fn board(&self) -> PyResult<Vec<Piece>> {
        Ok(self.board.board.to_vec())
    }

    #[new]
    fn __new__(difficulty: i32) -> PyResult<Self> {
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

    fn display_commands(&self) -> PyResult<Vec<(Offset, Piece)>> {
        let mut commands = Vec::new();
        for i in 0..9 {
            if let Ok(offset) = Offset::new(i) {
                commands.push((offset, self.board.board[i]));
            } else {
                return Err(PyErr::new::<PyException, _>("Too large board"));
            }
        }
        Ok(commands)
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
mod tests{
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
        let game = Game::__new__(1).expect("Failed to create game");
        let board_as_vec = game.board().expect("Failed to get board");
        assert_eq!(board_as_vec.len(), 9);
        for i in 0..9 {
            assert_eq!(board_as_vec[i as usize], Piece::Empty);
        }
    }
    #[test]
    fn creator() {
        let easy = Game::new(1, StdRng::from_entropy()).expect("Failed to create game");
        assert!(easy.human_first);
        let medium = Game::new(2,StdRng::from_entropy()).expect("Failed to create game");
        assert!(medium.human_first);
        let hard = Game::new(3, StdRng::from_seed([0; 32])).expect("Failed to create game");
        assert!(!hard.human_first);
        let random = Game::new(4, StdRng::from_seed([0; 32])).expect("Failed to create game");
        assert!(random.human_first);
    }
}
// COV_EXCL_END
