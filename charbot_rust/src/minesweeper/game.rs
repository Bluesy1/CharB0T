use pyo3::exceptions::PyValueError;
use crate::minesweeper::{field::{Field, Content, TILE_HEIGHT, TILE_WIDTH}, common::MoveDestination};
use pyo3::prelude::*;

#[pyclass(module = "minesweeper")]
pub enum RevealResult{
    Flagged = 0,
    Mine = 1,
    Empty = 2,
    Number = 3,
}

#[pyclass(module = "minesweeper")]
pub enum ChordResult{
    Failed = 0,
    Success = 1,
    Death = 2,
}

#[pyclass(module = "minesweeper")]
pub struct ReturnCell {
    #[pyo3(get)]
    pub revealed: bool,
    #[pyo3(get)]
    pub marked: bool,
}

#[pyclass(module = "minesweeper")]
pub struct Game {
    field: Field,
    win_points: (u8, u8),
    lose_points: (u8, u8),
}

#[pymethods]
impl Game {
    #[new]
    fn new(width: u32, height: u32, mines: u32) -> Self {
        Game {
            field: Field::new(width, height, mines),
            win_points: (1, 0),
            lose_points: (1, 0),
        }
    }

    #[staticmethod]
    fn beginner() -> Self {
        Game {
            field: Field::new(8, 8, 10),
            win_points: (1, 1),
            lose_points: (1, 0),
        }
    }

    #[staticmethod]
    fn intermediate() -> Self {
        Game {
            field: Field::new(16, 16, 40),
            win_points: (2, 3),
            lose_points: (2, 0),
        }
    }

    #[staticmethod]
    fn expert() -> Self {
        Game {
            field: Field::new(22, 22, 100),
            win_points: (2, 5),
            lose_points: (2, 0),
        }
    }

    #[staticmethod]
    fn super_expert() -> Self {
        Game {
            field: Field::new(25, 25, 130),
            win_points: (3, 6),
            lose_points: (1, 0),
        }
    }

    #[getter]
    fn points(&self) -> (u8, u8) {
        if self.is_win() {
            self.win_points
        } else {
            self.lose_points
        }
    }

    #[getter]
    fn flagged_count(&self) -> u32 {
        self.field.count_marked()
    }

    #[getter]
    fn mine_count(&self) -> u32 {
        self.field.total_mines()
    }

    #[getter]
    fn size(&self) -> u32 {
        self.field.get_size()
    }

    fn draw(&mut self) -> (Vec<u8>, (u32, u32)) {
        (
            self.field.draw().to_vec(),
            (
                (self.field.get_width() + 1) * TILE_WIDTH,
                (self.field.get_height() + 1) * TILE_HEIGHT,
            ),
        )
    }

    fn change_row(&mut self, row: u32) -> PyResult<ReturnCell> {
        if row > self.field.get_height() {
            return Err(PyValueError::new_err("Row index out of range"));
        }
        while self.field.get_y() < row {
            self.field.move_selection(MoveDestination::Down);
        }
        while self.field.get_y() > row {
            self.field.move_selection(MoveDestination::Up);
        }
        Ok(self.field.get_selected_cell().to_return_cell())
    }

    fn change_col(&mut self, col: u32) -> PyResult<ReturnCell> {
        if col > self.field.get_width() {
            return Err(PyValueError::new_err("Column index out of range"));
        }
        while self.field.get_x() < col {
            self.field.move_selection(MoveDestination::Right);
        }
        while self.field.get_x() > col {
            self.field.move_selection(MoveDestination::Left);
        }
        Ok(self.field.get_selected_cell().to_return_cell())
    }

    fn toggle_flag(&mut self) {
        let ind = self.field.get_selected_ind();
        self.field.toggle_mark(ind);
    }

    fn reveal(&mut self) -> RevealResult {
        let ind = self.field.get_selected_ind();
        self.field.reset_if_need(ind);
        if self.field.marked(ind) {
            self.toggle_flag();
            return RevealResult::Flagged;
        }
        match self.field.reveal(ind){
            &Content::None => {
                self.field.chain_reveal(ind);
                RevealResult::Empty
            },
            &Content::Mine(_) => {
                self.field.reveal_all();
                self.field.set_killer(ind);
                RevealResult::Mine
            },
            &Content::Number(_) => RevealResult::Number
        }
    }

    fn chord(&mut self) -> ChordResult {
        let ind = self.field.get_selected_ind();
        if let &Content::Number(n) = self.field.get_content(ind) {
            if !self.field.revealed(ind) {
                return ChordResult::Failed;
            }
            let surrounding = self.field.get_near_cells_ids(ind);
            let count = self.field.get_neighborhood_count(ind);
            if count == n {
                for id in surrounding {
                    if !self.field.marked(id) {
                        match self.field.reveal(id) {
                            &Content::Mine(_) => {
                                self.field.set_killer(id);
                                self.field.reveal_all();
                                return ChordResult::Death;
                            },
                            &Content::None => {
                                self.field.chain_reveal(id);
                            },
                            _ => {}
                        }
                    }
                }
                ChordResult::Success
            } else {
                ChordResult::Failed
            }
        } else {
            ChordResult::Failed
        }
    }

    fn is_win(&self) -> bool {
        self.field.is_victory()
    }

    fn quit(&mut self) {
        self.field.reveal_all();
    }

    fn restart(&mut self) {
        self.field.restart();
    }
}
