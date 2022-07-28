mod board;
mod player;

use rand::prelude::*;
use pyo3::exceptions::{PyException, PyValueError};
use pyo3::prelude::*;
//use pyo3::types::PyTuple;
use crate::tictactoe::board::{Offset, Piece};
use crate::points::Points;

pub enum Difficulty {
    Easy,
    Medium,
    Hard,
    Random,
}

impl Difficulty {
    fn extract(obj: i32) -> PyResult<Self> {
         match obj {
            1 => Ok(Difficulty::Easy),
            2 => Ok(Difficulty::Medium),
            3 => Ok(Difficulty::Hard),
            4 => Ok(Difficulty::Random),
            _ => Err(PyErr::new::<PyValueError, _>("Invalid difficulty value")),
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

#[pymethods]
impl Game {
    #[getter]
    fn board(&self) -> PyResult<Vec<Piece>> {
        Ok(self.board.board.iter().cloned().collect())
    }

    #[new]
    fn __new__(difficulty: i32) -> PyResult<Self> {
        let difficulty = Difficulty::extract(difficulty)?;
        let points = Points::new(&difficulty);
        let x: Option<Box<dyn player::Player>>;
        let o: Option<Box<dyn player::Player>>;
        let mut human_first: bool = true;
        let mut rng = thread_rng();
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
                let comp_mode: &str;
                match vec!["m", "a", "r"].choose(&mut rng){
                    Some(s) => {comp_mode = *s;},
                    None => {return Err(PyErr::new::<PyException, _>("Logic error occurred"));}
                }
                let chance: f64;
                match comp_mode{
                    "m" => {chance = 0.5;},
                    "a" => {chance = 0.25;},
                    "r" => {chance = 0.75},
                    _ => {chance = 0.0}
                }
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
                    let action = game.player_x.play(&mut game.board, Piece::X);
                    game.board.place_piece(action, Piece::X);
                }
                Ok(game)
            },
            _ => {Err(PyErr::new::<PyException, _> ("Unexpected Logic Error"))}
        }
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
        let comp_move = computer.play(&mut self.board, computer_piece);
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

const DOCSTRING: &str = "Rust based reimplementation of tictactoe";

pub(crate) fn register_tictactoe(py: Python, m: &PyModule) -> PyResult<()> {
    let tictactoe = PyModule::new(py, "tictactoe")?;
    tictactoe.add_class::<Game>()?;
    tictactoe.add_class::<Piece>()?;
    tictactoe.add_class::<Offset>()?;
    //let all = [
    //    "Game",
    //    "Piece",
    //    "Offset",
    //];
    //let pyall = PyTuple::new(py, all.into_iter());
    //tictactoe.add("__all__", pyall)?;
    tictactoe.add("__doc__", DOCSTRING)?;
    m.add_submodule(tictactoe)?;
    Ok(())
}
