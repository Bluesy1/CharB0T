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

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn easy() {
        let points = Points::new(&Difficulty::Easy);
        assert_eq!(points.win, (1, 1));
        assert_eq!(points.draw, (1, 0));
        assert_eq!(points.loss, (0, 0));
    }
    #[test]
    fn medium() {
        let points = Points::new(&Difficulty::Medium);
        assert_eq!(points.win, (2, 2));
        assert_eq!(points.draw, (2, 0));
        assert_eq!(points.loss, (0, 0));
    }
    #[test]
    fn hard() {
        let points = Points::new(&Difficulty::Hard);
        assert_eq!(points.win, (2, 3));
        assert_eq!(points.draw, (2, 1));
        assert_eq!(points.loss, (0, 0));
    }
    #[test]
    fn random() {
        let points = Points::new(&Difficulty::Random);
        assert_eq!(points.win, (1, 1));
        assert_eq!(points.draw, (1, 0));
        assert_eq!(points.loss, (0, 0));
    }
}
