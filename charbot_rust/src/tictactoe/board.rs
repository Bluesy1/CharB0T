// COV_EXCL_START
use std::fmt::{Display, Error, Formatter, Write};
use std::ops::Deref;
use pyo3::{IntoPy, pyclass, pymethods, PyObject, PyResult, Python};
use pyo3::types::PyString;
// COV_EXCL_STOP


#[pyclass(module = "tictactoe")] // COV_EXCL_LINE
#[derive(PartialEq, Eq, Clone, Copy, Debug)] // COV_EXCL_LINE
pub enum Piece { // COV_EXCL_LINE
    X,
    O,
    Empty
}

#[pymethods] // COV_EXCL_LINE
impl Piece {
    pub fn swap(&self) -> Self {
        match self { // COV_EXCL_LINE
            Self::X => Self::O,
            Self::O => Self::X,
            Self::Empty => Self::Empty
        }
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(self.value())
    }

    #[getter] // COV_EXCL_LINE
    fn value(&self) -> String {
        match self { // COV_EXCL_LINE
            Self::X => String::from("X"),
            Self::O => String::from("O"),
            Self::Empty => String::from(" ")
        }
    }

    #[getter] // COV_EXCL_LINE
    fn name(&self) -> String {
        match self { // COV_EXCL_LINE
            Self::X => String::from("X"),
            Self::O => String::from("O"),
            Self::Empty => String::from("Empty")
        }
    }
}
impl Display for Piece {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> Result<(), Error> {
        match *self { // COV_EXCL_LINE
            Self::X => formatter.write_char('X')?, // COV_EXCL_LINE
            Self::O => formatter.write_char('O')?, // COV_EXCL_LINE
            Self::Empty => formatter.write_char(' ')? // COV_EXCL_LINE
        }
        Ok(())
    }
}
// COV_EXCL_START
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
// COV_EXCL_STOP

/// Offsets for creating a graphical representation of the board.
#[pyclass(module = "tictactoe")] // COV_EXCL_LINE
#[derive(PartialEq, Eq, Clone, Copy, Debug)] // COV_EXCL_LINE
pub enum Offset  { // COV_EXCL_LINE
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

#[pymethods] // COV_EXCL_LINE
impl Offset {
    /// Name of the offset
    #[getter]
    fn name(&self) -> String {
        match self { // COV_EXCL_LINE
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
    #[getter] // COV_EXCL_LINE
    pub(crate) fn value(&self) -> (u16, u16) {
        match self { // COV_EXCL_LINE
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

static WINNING_INDICES: &[(Index, Index, Index)] = &[
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
];

#[pyclass(module = "tictactoe")] // COV_EXCL_LINE
#[derive(Clone, Debug)] // COV_EXCL_LINE
pub struct Board {
    pub(crate) board: [Piece; 9],
    pub(crate) n_pieces: u8,
}


#[pymethods] // COV_EXCL_START
impl Board {
    #[getter]
    fn board(&self) -> Vec<Piece> {
        self.board.to_vec()
    }
}

impl Default for Board {
    fn default() -> Self {
        Self::new()
    }
}

// COV_EXCL_STOP


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
            panic!("Tried to place a piece on an occupied cell, Index: {index}"); // COV_EXCL_LINE
        }
        self.board[index] = piece; // COV_EXCL_LINE
        self.n_pieces += 1;
        true
    }

    pub const VALID_INDICES: std::ops::Range<usize> = 0..9;

    pub fn is_valid_index(index: Index) -> bool {
        Self::VALID_INDICES.contains(&index)
    }

    pub fn is_draw(&self) -> bool {
        self.n_pieces >= 9
    }

    pub fn is_victory_for_player(&self, player: Piece) -> bool {
        for &(a, b, c) in WINNING_INDICES { // COV_EXCL_LINE
            if self.board[a] == player // COV_EXCL_LINE
                && self.board[b] == player // COV_EXCL_LINE
                && self.board[c] == player // COV_EXCL_LINE
            {
                return true;
            }
        }
        false
    }

    pub fn is_victory(&self) -> Option<Piece> {
        if self.is_victory_for_player(Piece::X) {
            Some(Piece::X)
        } else if self.is_victory_for_player(Piece::O) { // COV_EXCL_LINE
            Some(Piece::O) // COV_EXCL_LINE
        } else {
            None
        }
    }

    fn format_cell(&self, index: Index, formatter: &mut Formatter<'_>) -> Result<(), Error> { // COV_EXCL_LINE
        match self.board[index] {
            Piece::Empty => write!(formatter, "{index}"),
            player => player.fmt(formatter),
        }
    }
}
// COV_EXCL_START
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
// COV_EXCL_STOP

// COV_EXCL_START
#[cfg(test)]
mod tests {
    use super::*;
    use yare::parameterized;

    #[test]
    fn piece() {
        assert_eq!(Piece::X.swap(), Piece::O);
        assert_eq!(Piece::O.swap(), Piece::X);
        assert_eq!(Piece::Empty.swap(), Piece::Empty);
        assert_eq!(Piece::X.__str__().unwrap(), String::from("X"));
        assert_eq!(Piece::O.__str__().unwrap(), String::from("O"));
        assert_eq!(Piece::Empty.__str__().unwrap(), String::from(" "));
        assert_eq!(Piece::X.name(), String::from("X"));
        assert_eq!(Piece::O.name(), String::from("O"));
        assert_eq!(Piece::Empty.name(), String::from("Empty"));
        assert_eq!(Piece::X.value(), String::from("X"));
        assert_eq!(Piece::O.value(), String::from("O"));
        assert_eq!(Piece::Empty.value(), String::from(" "));
        assert_eq!(format!("{}", Piece::X), String::from("X"));
        assert_eq!(format!("{}", Piece::O), String::from("O"));
        assert_eq!(format!("{}", Piece::Empty), String::from(" "));
    }
    #[parameterized(
        pos_zero = { 0, (0, 0), String::from("TopLeft")},
        pos_one = { 1, (179, 0), String::from("TopMiddle")},
        pos_two = { 2, (355, 0), String::from("TopRight")},
        pos_three = { 3, (0, 179), String::from("MiddleLeft")},
        pos_four = { 4, (179, 179), String::from("MiddleMiddle")},
        pos_five = { 5, (355, 179), String::from("MiddleRight")},
        pos_six = { 6, (0, 357), String::from("BottomLeft")},
        pos_seven = { 7, (179, 357), String::from("BottomMiddle")},
        pos_eight = { 8, (355, 357), String::from("BottomRight")}
    )]
    fn offset(pos: Index, value: (u16, u16), name: String) {
        let zero = Offset::new(pos).unwrap_or_else(|_| panic!("Failed to create Offset::{}", &name));
        assert_eq!(zero.value(), value);
        assert_eq!(zero.name(), name);
    }
    #[test]
    fn bad_offset(){
        Offset::new(9).expect_err("Failed to reject index 9");
    }
    #[test]
    fn board() {
        let mut board = Board::new();
        assert_eq!(format!("{}", board), "012\n345\n678");
        assert_eq!(board.n_pieces, 0);
        assert!(!board.is_draw());
        for index in 0..9 {
            assert_eq!(board.board[index], Piece::Empty);
            assert!(Board::is_valid_index(index));
            assert!(board.place_piece(index, Piece::X), "Failed to place piece at index {}", index);
            assert_eq!(board.n_pieces, (index + 1) as u8);
        }
        assert_eq!(board.is_victory(), Some(Piece::X));
        assert!(board.is_victory_for_player(Piece::X));
        assert!(!board.is_victory_for_player(Piece::O));
        assert_eq!(format!("{}", board), "XXX\nXXX\nXXX");
    }
}
// COV_EXCL_STOP
