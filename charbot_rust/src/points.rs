use crate::tictactoe::Difficulty;
use pyo3::prelude::*;

#[pyclass(module = "charbot_rust")]
pub struct Points {
    #[pyo3(get)]
    pub win: (i8, i8),
    #[pyo3(get)]
    pub draw: (i8, i8),
    #[pyo3(get)]
    pub loss: (i8, i8),
}

impl Points {
    pub fn new(difficulty: &Difficulty) -> Self {
        match difficulty {
            Difficulty::Easy | Difficulty::Random => Points {
                win: (1, 1),
                draw: (1, 0),
                loss: (0, 0),
            },
            Difficulty::Medium => Points {
                win: (2, 2),
                draw: (2, 0),
                loss: (0, 0),
            },
            Difficulty::Hard => Points {
                win: (2, 3),
                draw: (2, 1),
                loss: (0, 0),
            },
        }
    }
}
