// COV_EXCL_START
use pyo3::exceptions::PyValueError;
use crate::minesweeper::{field::{Field, Content, TILE_HEIGHT, TILE_WIDTH}, common::MoveDestination};
use pyo3::prelude::*;
use rand::rngs::StdRng;
use rand::SeedableRng;
// COV_EXCL_STOP

#[pyclass(module = "minesweeper")] // COV_EXCL_LINE
#[derive(PartialEq, Debug)] // COV_EXCL_LINE
pub enum RevealResult{ // COV_EXCL_LINE
    Flagged = 0,
    Mine = 1,
    Empty = 2,
    Number = 3,
}

#[pyclass(module = "minesweeper")] // COV_EXCL_LINE
#[derive(PartialEq, Debug)] // COV_EXCL_LINE
pub enum ChordResult{ // COV_EXCL_LINE
    Failed = 0,
    Success = 1,
    Death = 2,
}

#[pyclass(module = "minesweeper")] // COV_EXCL_LINE
#[derive(PartialEq, Debug)] // COV_EXCL_LINE
pub struct ReturnCell {
    #[pyo3(get)]
    pub revealed: bool,
    #[pyo3(get)]
    pub marked: bool, // COV_EXCL_LINE
}

#[pyclass(module = "minesweeper")] // COV_EXCL_LINE
pub struct Game {
    field: Field,
    win_points: (u8, u8),
    lose_points: (u8, u8),
    quit: bool,
}

#[pymethods] // COV_EXCL_LINE
impl Game {
    #[new] // COV_EXCL_LINE
    fn new(width: u32, height: u32, mines: u32) -> Self { // COV_EXCL_LINE
        let rng = StdRng::from_entropy();
        Game {
            field: Field::new(width, height, mines, rng,),
            win_points: (1, 0),
            lose_points: (1, 0),
            quit: false,
        }
    }

    #[staticmethod] // COV_EXCL_LINE
    fn beginner() -> Self {
        Game {
            field: Field::new(8, 8, 10, StdRng::from_entropy()),
            win_points: (1, 1),
            lose_points: (1, 0),
            quit: false
        }
    }

    #[staticmethod] // COV_EXCL_LINE
    fn intermediate() -> Self {
        Game {
            field: Field::new(16, 16, 40, StdRng::from_entropy()),
            win_points: (2, 3),
            lose_points: (2, 0),
            quit: false
        }
    }

    #[staticmethod] // COV_EXCL_LINE
    fn expert() -> Self {
        Game {
            field: Field::new(22, 22, 100, StdRng::from_entropy()),
            win_points: (2, 4),
            lose_points: (2, 0),
            quit: false
        }
    }

    #[staticmethod] // COV_EXCL_LINE
    fn super_expert() -> Self {
        Game {
            field: Field::new(25, 25, 130, StdRng::from_entropy()),
            win_points: (3, 5),
            lose_points: (3, 0),
            quit: false
        }
    }

    #[getter] // COV_EXCL_LINE
    fn points(&self) -> (u8, u8) {
        if self.is_win() {
            self.win_points
        } else {
            self.lose_points
        }
    }
    #[getter] // COV_EXCL_LINE
    fn flagged_count(&self) -> u32 {
        self.field.count_marked()
    }

    #[getter] // COV_EXCL_LINE
    fn mine_count(&self) -> u32 {
        self.field.total_mines()
    }

    #[getter] // COV_EXCL_LINE
    fn size(&self) -> u32 {
        self.field.get_size()
    }

    #[getter] // COV_EXCL_LINE
    fn width(&self) -> u32 {
        self.field.get_width()
    }

    #[getter] // COV_EXCL_LINE
    fn height(&self) -> u32 {
        self.field.get_height()
    }

    #[getter] // COV_EXCL_LINE
    fn x(&self) -> u32 {
        self.field.get_x()
    }

    #[getter] // COV_EXCL_LINE
    fn y(&self) -> u32 {
        self.field.get_y()
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

    fn change_row(&mut self, row: u32) -> PyResult<ReturnCell> { // COV_EXCL_LINE
        if row >= self.field.get_height() {
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

    fn change_col(&mut self, col: u32) -> PyResult<ReturnCell> { // COV_EXCL_LINE
        if col >= self.field.get_width() {
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

    fn toggle_flag(&mut self) -> bool {
        let ind = self.field.get_selected_ind();
        self.field.toggle_mark(ind)
    }

    fn reveal(&mut self) -> RevealResult {
        let ind = self.field.get_selected_ind();
        self.field.reset_if_need(ind);
        if self.field.marked(ind) {
            self.toggle_flag();
            return RevealResult::Flagged;
        }
        match *self.field.reveal(ind){ // COV_EXCL_LINE
            Content::None => {
                self.field.chain_reveal(ind);
                RevealResult::Empty
            },
            Content::Mine(_) => {
                self.field.reveal_all();
                self.field.set_killer(ind);
                self.quit = true;
                RevealResult::Mine
            },
            Content::Number(_) => RevealResult::Number
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
            if count == n { // COV_EXCL_LINE
                for id in surrounding { // COV_EXCL_LINE
                    if !self.field.marked(id) {
                        match self.field.reveal(id) {
                            Content::Mine(_) => {
                                self.field.set_killer(id);
                                self.field.reveal_all();
                                return ChordResult::Death;
                            },
                            Content::None => {
                                self.field.chain_reveal(id);
                            },
                            _ => {}
                        }
                    }
                }
                ChordResult::Success
            } else {
                ChordResult::Failed // COV_EXCL_LINE
            }
        } else { // COV_EXCL_LINE
            ChordResult::Failed
        }
    }

    fn is_win(&self) -> bool {
        if self.quit {
            false
        } else {
            self.field.is_victory()
        }
    }

    fn quit(&mut self) {
        self.quit = true;
        self.field.reveal_all();
    }

    fn restart(&mut self) {
        self.field.restart();
    }
}

// COV_EXCL_START
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn custom() {
        let game = Game::new(10, 10, 10);
        assert_eq!(game.width(), 10);
        assert_eq!(game.height(), 10);
        assert_eq!(game.mine_count(), 10);
        assert_eq!(game.size(), 100);
        assert_eq!(game.points(), game.lose_points);
        assert_eq!(game.lose_points, (1, 0));
        assert_eq!(game.win_points, (1, 0));
    }
    #[test]
    fn beginner() {
        let game = Game::beginner();
        assert_eq!(game.size(), 64);
        assert_eq!(game.width(), 8);
        assert_eq!(game.height(), 8);
        assert_eq!(game.x(), 4);
        assert_eq!(game.y(), 4);
        assert_eq!(game.flagged_count(), 0);
        assert_eq!(game.mine_count(), 10);
        assert_eq!(game.points(), game.win_points);
        assert_eq!(game.lose_points, (1, 0));
        assert_eq!(game.win_points, (1, 1));
    }
    #[test]
    fn intermediate() {
        let game = Game::intermediate();
        assert_eq!(game.size(), 256);
        assert_eq!(game.width(), 16);
        assert_eq!(game.height(), 16);
        assert_eq!(game.x(), 8);
        assert_eq!(game.y(), 8);
        assert_eq!(game.flagged_count(), 0);
        assert_eq!(game.mine_count(), 40);
        assert_eq!(game.points(), game.win_points);
        assert_eq!(game.lose_points, (2, 0));
        assert_eq!(game.win_points, (2, 3));
    }
    #[test]
    fn expert() {
        let game = Game::expert();
        assert_eq!(game.size(), 484);
        assert_eq!(game.width(), 22);
        assert_eq!(game.height(), 22);
        assert_eq!(game.x(), 11);
        assert_eq!(game.y(), 11);
        assert_eq!(game.flagged_count(), 0);
        assert_eq!(game.mine_count(), 100);
        assert_eq!(game.points(), game.win_points);
        assert_eq!(game.lose_points, (2, 0));
        assert_eq!(game.win_points, (2, 4));
    }
    #[test]
    fn super_expert() {
        let game = Game::super_expert();
        assert_eq!(game.size(), 625);
        assert_eq!(game.width(), 25);
        assert_eq!(game.height(), 25);
        assert_eq!(game.x(), 12);
        assert_eq!(game.y(), 12);
        assert_eq!(game.flagged_count(), 0);
        assert_eq!(game.mine_count(), 130);
        assert_eq!(game.points(), game.win_points);
        assert_eq!(game.lose_points, (3, 0));
        assert_eq!(game.win_points, (3, 5));
    }
    #[test]
    fn change_row() {
        let mut game = Game::new(5, 5, 5);
        let out1 = game.change_row(4).expect("Saw row 4 as out of bounds incorrectly.");
        assert_eq!(game.y(), 4);
        assert_eq!(out1, ReturnCell{ revealed: false, marked: false });
        let out2 = game.change_row(0).expect("Saw row 0 as out of bounds incorrectly.");
        assert_eq!(game.y(), 0);
        assert_eq!(out2, ReturnCell{ revealed: false, marked: false });
        if let Ok(_) = game.change_row(5) {
            panic!("Saw row 5 as in bounds incorrectly.");
        }
    }
    #[test]
    fn change_col() {
        let mut game = Game::new(5, 5, 5);
        let out1 = game.change_col(4).expect("Saw col 4 as out of bounds incorrectly.");
        assert_eq!(game.x(), 4);
        assert_eq!(out1, ReturnCell{ revealed: false, marked: false });
        let out2 = game.change_col(0).expect("Saw col 0 as out of bounds incorrectly.");
        assert_eq!(game.x(), 0);
        assert_eq!(out2, ReturnCell{ revealed: false, marked: false });
        if let Ok(_) = game.change_col(5) {
            panic!("Saw col 5 as in bounds incorrectly.");
        }
    }
    #[test]
    fn toggle_flag() {
        let mut game = Game::beginner();
        let ind = game.field.get_selected_ind();
        assert!(!game.field.marked(ind));
        game.toggle_flag();
        assert!(game.field.marked(ind));
        game.toggle_flag();
        assert!(!game.field.marked(ind));
    }
    #[test]
    fn quit() {
        let mut game = Game::beginner();
        game.quit();
        assert!(!game.is_win());
        assert_eq!(game.points(), game.lose_points);
    }
    #[test]
    fn restart() {
        let mut game1 = Game::beginner();
        let mut game2 = Game::beginner();
        game2.reveal();
        game2.restart();
        for row in 0..8{
            if let Err(_) = game1.change_row(row) {
                panic!("Saw row {} as in bounds incorrectly.", row);
            }
            if let Err(_) = game2.change_row(row){
                panic!("Saw row {} as out of bounds incorrectly.", row);
            }
            for col in 0..8{
                if let Err(_) = game1.change_col(col) {
                    panic!("Saw col {} as in bounds incorrectly.", col);
                }
                if let Err(_) = game2.change_col(col){
                    panic!("Saw col {} as out of bounds incorrectly.", col);
                }
                assert_eq!(
                    game1.field.get_selected_cell().to_return_cell(),
                    game2.field.get_selected_cell().to_return_cell());
            }
        }
    }
    #[test]
    fn reveal() {
        let mut game = Game::new(5, 5, 10);
        let result = game.reveal();
        assert_ne!(result, RevealResult::Flagged);
        assert_ne!(result, RevealResult::Mine);
        for row in 0..5 {
            game.change_row(row).expect("In Bounds");
            for col in 0..5 {
                game.change_col(col).expect("In Bounds");
                if row== 0 && col == 0 {
                    game.toggle_flag();
                    assert_eq!(game.reveal(), RevealResult::Flagged);
                }
                if let RevealResult::Mine = game.reveal() {
                    let content = game.field.get_selected_cell().content();
                    assert_eq!(content, &Content::Mine(true));
                    assert!(!game.is_win());
                    assert_eq!(game.points(), game.lose_points);
                    break
                }
            }
        }
    }
    #[test]
    fn draw() {
        let mut game = Game::new(5, 5, 5);
        let field = Field::new(5, 5, 5, StdRng::from_entropy());
        let drawn_field = field.draw().to_vec();
        let (drawn_game, dims) = game.draw();
        assert_eq!(dims, (300, 300));
        assert_eq!(drawn_field, drawn_game);
    }
    #[test]
    fn chord() {
        //with the given seed, the board should be:
        // 1M11M1EE
        // 122211EE
        // E1M1E111
        // E111E1M1
        // EEEEE111
        // EEEEEEEE
        // EEEE111E
        // EEEE1M1E
        let mut game = Game {
            field: Field::new(8, 8, 5, StdRng::from_seed([0; 32])),
            win_points: (0, 0),
            lose_points: (0, 0),
            quit: false
        };
        let ind = game.field.get_selected_ind();
        game.field.reset_if_need(ind);
        game.change_row(3).unwrap();
        game.change_col(6).unwrap();
        game.toggle_flag();
        game.change_col(7).unwrap();
        game.change_row(2).unwrap();
        assert_eq!(game.chord(), ChordResult::Failed);
        game.reveal();
        assert_eq!(game.chord(), ChordResult::Success);
        game.change_row(1).unwrap();
        assert_eq!(game.chord(), ChordResult::Failed);
        game.change_col(6).unwrap();
        assert_eq!(game.chord(), ChordResult::Failed);
        game.change_col(4).unwrap();
        game.toggle_flag();
        game.change_col(5).unwrap();
        assert_eq!(game.chord(), ChordResult::Death);
    }
}
// GCOV_EXCL_STOP
