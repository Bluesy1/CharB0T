// GCOVR_EXCL_START
use std::fmt::{Display, Error, Formatter, Write};
use std::ops::Deref;
use pyo3::{IntoPy, pyclass, pymethods, PyObject, PyResult, Python};
use pyo3::types::PyString;
// GCOVR_EXCL_STOP


#[pyclass(module = "tictactoe")] // GCOVR_EXCL_LINE
#[derive(PartialEq, Eq, Clone, Copy, Debug)] // GCOVR_EXCL_LINE
pub enum Piece {
    X,
    O,
    Empty
}

#[pymethods] // GCOVR_EXCL_LINE
impl Piece {
    pub fn swap(&self) -> Self {
        match self {
            Self::X => Self::O,
            Self::O => Self::X,
            Self::Empty => Self::Empty
        }
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(self.value())
    }

    #[getter] // GCOVR_EXCL_LINE
    fn value(&self) -> String {
        match self {
            Self::X => String::from("X"),
            Self::O => String::from("O"),
            Self::Empty => String::from(" ")
        }
    }

    #[getter] // GCOVR_EXCL_LINE
    fn name(&self) -> String {
        match self {
            Self::X => String::from("X"),
            Self::O => String::from("O"),
            Self::Empty => String::from("Empty")
        }
    }
}
impl Display for Piece {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> Result<(), Error> {
        match *self {
            Self::X => formatter.write_char('X')?,
            Self::O => formatter.write_char('O')?,
            Self::Empty => formatter.write_char(' ')?
        }
        Ok(())
    }
}
// GCOVR_EXCL_START
impl IntoPy<PyResult<String>> for Piece {
    fn into_py(self, _py: Python<'_>) -> PyResult<String> {
        match self {
            Self::X => Ok(String::from("X")),
            Self::O => Ok(String::from("O")),
            Self::Empty => Ok(String::from("Empty"))
        }
    }
}
impl IntoPy<PyResult<PyObject>> for Piece {
    fn into_py(self, py: Python) -> PyResult<PyObject> {
        match self {
            Piece::X => Ok(PyString::new(py, "X").deref().into_py(py)),
            Piece::O => Ok(PyString::new(py, "O").deref().into_py(py)),
            Piece::Empty => Ok(PyString::new(py, " ").deref().into_py(py))
        }
    }
}
// GCOVR_EXCL_STOP

/// Offsets for creating a graphical representation of the board.
#[pyclass(module = "tictactoe")] // GCOVR_EXCL_LINE
#[derive(PartialEq, Eq, Clone, Copy)] // GCOVR_EXCL_LINE
pub enum Offset  {
    TopLeft,
    TopMiddle,
    TopRight,
    MiddleLeft,
    MiddleMiddle,
    MiddleRight,
    BottomLeft,
    BottomMiddle,
    BottomRight
}

impl Offset {
    /// Returns the correct location for a given index.
    pub fn new(index: Index) -> Result<Self, String> {
        match index {
            0 => Ok(Offset::TopLeft),
            1 => Ok(Offset::TopMiddle),
            2 => Ok(Offset::TopRight),
            3 => Ok(Offset::MiddleLeft),
            4 => Ok(Offset::MiddleMiddle),
            5 => Ok(Offset::MiddleRight),
            6 => Ok(Offset::BottomLeft),
            7 => Ok(Offset::BottomMiddle),
            8 => Ok(Offset::BottomRight),
            _ => Err(String::from("Invalid index"))
        }
    }
}

#[pymethods] // GCOVR_EXCL_LINE
impl Offset {
    /// Name of the offset
    #[getter]
    fn name(&self) -> String {
        match self {
            Offset::TopLeft => String::from("TopLeft"),
            Offset::TopMiddle => String::from("TopMiddle"),
            Offset::TopRight => String::from("TopRight"),
            Offset::MiddleLeft => String::from("MiddleLeft"),
            Offset::MiddleMiddle => String::from("MiddleMiddle"),
            Offset::MiddleRight => String::from("MiddleRight"),
            Offset::BottomLeft => String::from("BottomLeft"),
            Offset::BottomMiddle => String::from("BottomMiddle"),
            Offset::BottomRight => String::from("BottomRight")
        }
    }

    /// The value of the offset as a tuple of (x, y), 2 u16s
    #[getter] // GCOVR_EXCL_LINE
    pub(crate) fn value(&self) -> (u16, u16) {
        match self {
            Offset::TopLeft => (0, 0),
            Offset::TopMiddle => (179, 0),
            Offset::TopRight => (355, 0),
            Offset::MiddleLeft => (0, 179),
            Offset::MiddleMiddle => (179, 179),
            Offset::MiddleRight => (355, 179),
            Offset::BottomLeft => (0, 357),
            Offset::BottomMiddle => (179, 357),
            Offset::BottomRight => (355, 357)
        }
    }
}

pub type Index = usize;

static WINNING_INDECES: &[(Index, Index, Index)] = &[
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
];

#[pyclass(module = "tictactoe")] // GCOVR_EXCL_LINE
#[derive(Clone)] // GCOVR_EXCL_LINE
pub struct Board {
    pub(crate) board: [Piece; 9],
    n_pieces: u8,
}


#[pymethods] // GCOVR_EXCL_LINE
impl Board {
    #[getter]
    fn board(&self) -> PyResult<Vec<Piece>> {
        Ok(self.board.to_vec())
    }
}

impl Default for Board {
    fn default() -> Self {
        Self::new()
    }
}

impl Board {
    pub fn new() -> Self {
        Board {
            board: [Piece::Empty; 9],
            n_pieces: 0,
        }
    }

    pub fn cell_is_empty(&self, index: Index) -> bool {
        self.board[index] == Piece::Empty
    }

    pub fn place_piece(&mut self, index: Index, piece: Piece) -> bool {
        if !self.cell_is_empty(index) {
            panic!("Tried to place a piece on an occupied cell");
        }
        self.board[index] = piece;
        self.n_pieces += 1;
        true
    }

    pub const VALID_INDECES: std::ops::Range<usize> = 0..9;

    pub fn is_valid_index(index: Index) -> bool {
        Self::VALID_INDECES.contains(&index)
    }

    pub fn is_draw(&self) -> bool {
        self.n_pieces >= 9
    }

    pub fn is_victory_for_player(&self, player: Piece) -> bool {
        for &(a, b, c) in WINNING_INDECES {
            if self.board[a] == player
                && self.board[b] == player
                && self.board[c] == player
            {
                return true;
            }
        }
        false
    }

    pub fn is_victory(&self) -> Option<Piece> {
        if self.is_victory_for_player(Piece::X) {
            Some(Piece::X)
        } else if self.is_victory_for_player(Piece::O) {
            Some(Piece::O)
        } else {
            None
        }
    }

    fn format_cell(&self, index: Index, formatter: &mut Formatter<'_>) -> Result<(), Error> {
        match self.board[index] {
            Piece::Empty => write!(formatter, "{}", index),
            player => player.fmt(formatter),
        }
    }
}
impl Display for Board {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> Result<(), Error> {
        self.format_cell(0, formatter)?;
        self.format_cell(1, formatter)?;
        self.format_cell(2, formatter)?;
        writeln!(formatter)?;

        self.format_cell(3, formatter)?;
        self.format_cell(4, formatter)?;
        self.format_cell(5, formatter)?;
        writeln!(formatter)?;

        self.format_cell(6, formatter)?;
        self.format_cell(7, formatter)?;
        self.format_cell(8, formatter)?;

        Ok(())
    }
}

// GCOVR_EXCL_START
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn piece_swap() {
        assert_eq!(Piece::X.swap(), Piece::O);
        assert_eq!(Piece::O.swap(), Piece::X);
        assert_eq!(Piece::Empty.swap(), Piece::Empty);
    }
    #[test]
    fn piece_value() {
        assert_eq!(Piece::X.__str__().unwrap(), String::from("X"));
        assert_eq!(Piece::O.__str__().unwrap(), String::from("O"));
        assert_eq!(Piece::Empty.__str__().unwrap(), String::from(" "));
        assert_eq!(Piece::X.name(), String::from("X"));
        assert_eq!(Piece::O.name(), String::from("O"));
        assert_eq!(Piece::Empty.name(), String::from("Empty"));
        assert_eq!(Piece::X.value(), String::from("X"));
        assert_eq!(Piece::O.value(), String::from("O"));
        assert_eq!(Piece::Empty.value(), String::from(" "));
    }
}
// GCOVR_EXCL_STOP
