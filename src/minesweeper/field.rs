// COV_EXCL_START
use std::io::Cursor;
use std::collections::VecDeque;
use image::{ImageBuffer, RgbImage, imageops, Rgb, ImageReader};
use imageproc::{rect::Rect, drawing::{draw_filled_rect_mut, draw_hollow_rect_mut}};
use rand::rngs::StdRng;
use rand::prelude::SliceRandom;
use crate::minesweeper::common::MoveDestination;
use crate::minesweeper::common;
use crate::minesweeper::game::ReturnCell;
// COV_EXCL_STOP

pub const TILE_WIDTH: u32 = 50;
pub const TILE_HEIGHT: u32 = 50;

#[derive(Debug, PartialEq, Eq)] // COV_EXCL_LINE
pub enum Content {
    Number(u8), // COV_EXCL_LINE
    Mine(bool), // bool is true when this is the mine that caused you to loose the game.
    None,
}

pub struct Cell {
    content: Content,
    revealed: bool,
    marked: bool,
}

impl Cell {
    fn create_empty() -> Cell {
        Cell {
            content: Content::None,
            revealed: false,
            marked: false,
        }
    }

    fn create_with_mine() -> Cell {
        Cell {
            content: Content::Mine(false),
            revealed: false,
            marked: false,
        }
    }

    pub fn clear(&mut self) {
        self.content = Content::None;
        self.revealed = false;
        self.marked = false;
    }

    fn reveal(&mut self) -> &Content {
        self.revealed = true;
        &self.content
    }

    fn toggle_mark(&mut self) {
        self.marked = !self.marked;
    }

    pub fn to_return_cell(&self) -> ReturnCell {
        ReturnCell {
            revealed: self.revealed,
            marked: self.marked,
        }
    }
    #[allow(dead_code)]
    pub fn content(&self) -> &Content {
        &self.content
    }
}

pub struct Field {
    cells: Vec<Cell>,
    width: u32,
    height: u32,
    mines: u32,
    size: u32,
    selected_x: u32,
    selected_y: u32,
    numbers_total: u32,
    numbers_opened: u32,
    need_regen: bool,
    rng: StdRng,
}

impl Field {
    pub fn new(width: u32, height: u32, mines: u32, rng: StdRng) -> Field {
        let mut field = Field {
            width,
            height,
            cells: vec![],
            mines,
            size: width * height,
            selected_x: width / 2,
            selected_y: height / 2,
            numbers_total: 0,
            numbers_opened: 0,
            need_regen: true,
            rng
        };
        field.reinit_vec();
        field
    }

    pub fn restart(&mut self) {
        self.need_regen = true;
        self.reinit_vec();
    }

    fn reinit_vec(&mut self) {
        self.cells.clear();
        self.size = self.width * self.height;
        for _ in 0..self.size { // COV_EXCL_LINE
            self.cells.push(Cell::create_empty());
        }
        self.selected_x = self.width / 2;
        self.selected_y = self.height / 2;
    }

    fn reset(&mut self, cursor_ind: u32) {
        self.clear();

        let cursor_near_cells = self.get_near_cells_ids(cursor_ind);

        // reinit cells with mines
        let mut new_cells = Vec::new();
        for i in 0..self.size - cursor_near_cells.len() as u32 { // COV_EXCL_LINE
            let cell = if i < self.mines {
                Cell::create_with_mine()
            } else {
                Cell::create_empty()
            };

            new_cells.push(cell);
        }

        // shuffle them
        new_cells.shuffle(&mut self.rng);

        // push empty cells near with cursor to avoid mines in this positions
        for ind in cursor_near_cells { // COV_EXCL_LINE
            new_cells.insert(ind as usize, Cell::create_empty());
        }

        self.cells = new_cells;

        self.write_numbers_near_mines();
        self.need_regen = false;
    }

    pub fn get_near_cells_ids(&mut self, ind: u32) -> Vec<u32> {
        let (begin_x, end_x, begin_y, end_y) = self.get_3x3_bounds(ind);

        let mut cursor_neighbor_cells = Vec::new();
        for yi in begin_y..end_y + 1 { // COV_EXCL_LINE
            for xi in begin_x..end_x + 1 { // COV_EXCL_LINE
                let ind = self.get_cell_index(xi, yi);
                cursor_neighbor_cells.push(ind);
            }
        }

        cursor_neighbor_cells
    }

    fn write_numbers_near_mines(&mut self) {
        let mut i: i32 = -1;
        let w = self.width as i32;
        while i < (self.size - 1) as i32 {
            i += 1;
            if let Some(&Content::None) = self.get_content_safe(i) { // COV_EXCL_LINE
                let ct_mine = |b| {
                    match b {
                        true => 1,
                        false => 0,
                    }
                };
                // don`t care about row
                let mut ct = ct_mine(self.is_mine_safe(i - w)) +
                             ct_mine(self.is_mine_safe(i + w));
                if i % w > 0 { // COV_EXCL_LINE
                    // check left side position
                    ct += ct_mine(self.is_mine_safe(i - w - 1)) +
                          ct_mine(self.is_mine_safe(i - 1)) +
                          ct_mine(self.is_mine_safe(i + w - 1));
                }
                if i % w < w - 1 { // COV_EXCL_LINE
                    // check right side position
                    ct += ct_mine(self.is_mine_safe(i - w + 1)) +
                          ct_mine(self.is_mine_safe(i + 1)) +
                          ct_mine(self.is_mine_safe(i + w + 1));
                }
                if ct > 0 {
                    self.get_cell_mut(i as u32).content = Content::Number(ct);
                    self.numbers_total += 1;
                }
            }
        }
    }

    pub fn get_cell_index(&mut self, x: u32, y: u32) -> u32 {
        x + y * self.width
    }

    // return coordinates of cell (x, y) by index in field
    pub fn get_coord(&mut self, ind: u32) -> (u32, u32) {
        (ind % self.width, ind / self.width) // COV_EXCL_LINE
    }

    pub fn get_neighborhood_count(&mut self, ind: u32) -> u8 {
        let (begin_x, end_x, begin_y, end_y) = self.get_3x3_bounds(ind);

        let mut marked_count = 0u8;
        for yi in begin_y..end_y + 1 { // COV_EXCL_LINE
            for xi in begin_x..end_x + 1 { // COV_EXCL_LINE
                let ind = self.get_cell_index(xi, yi);
                if self.marked(ind) {
                    marked_count += 1;
                }
            }
        }

        marked_count
    }

    // return (begin_x, end_x, begin_y, end_y) for specified position in field
    fn get_3x3_bounds(&mut self, ind: u32) -> (u32, u32, u32, u32) {
        let (x, y) = self.get_coord(ind);

        let begin_x = if x > 0 { // COV_EXCL_LINE
            x - 1
        } else {
            x // COV_EXCL_LINE
        };
        let end_x = if x + 1 < self.width {
            x + 1
        } else {
            x
        };
        let begin_y = if y > 0 { // COV_EXCL_LINE
            y - 1
        } else {
            y // COV_EXCL_LINE
        };
        let end_y = if y + 1 < self.height { // COV_EXCL_LINE
            y + 1
        } else {
            y // COV_EXCL_LINE
        };

        (begin_x, end_x, begin_y, end_y)
    }

    fn clear(&mut self) {
        for i in 0..self.size { // COV_EXCL_LINE
            self.get_cell_mut(i).clear();
        }
        self.numbers_opened = 0;
        self.numbers_total = 0;
    }

    pub fn reveal(&mut self, i: u32) -> &Content {
        if !self.revealed(i) {
            if let &Content::Number(_i) = self.get_cell_mut(i).reveal() {
                self.numbers_opened += 1;
            }
        }
        self.get_content(i)
    }

    pub fn revealed(&self, i: u32) -> bool {
        self.get_cell(i).revealed
    }

    pub fn marked(&self, i: u32) -> bool {
        self.get_cell(i).marked
    }

    pub fn set_killer(&mut self, i: u32) {
        self.get_cell_mut(i).content = Content::Mine(true);
    }

    fn get_cell_mut(&mut self, i: u32) -> &mut Cell {
        self.cells
            .get_mut(i as usize)
            .unwrap_or_else(|| panic!("Range check error at Field::get_cell_mut ({i})"))
    }

    fn get_cell(&self, i: u32) -> &Cell {
        self.cells
            .get(i as usize)
            .unwrap_or_else(|| panic!("Range check error at Field::get_cell ({i})"))
    }

    fn get_content_safe(&self, i: i32) -> Option<&Content> {
        if (i < 0) || ((i as u32) >= self.size) {
            None
        } else {
            Some(self.get_content(i as u32))
        }
    }

    pub fn get_content(&self, i: u32) -> &Content {
        &self.get_cell(i).content
    }

    pub fn count_marked(&self) -> u32 {
        (0..self.size).fold(0, |acc, i: u32| {
            if self.marked(i) { // COV_EXCL_LINE
                acc + 1 // COV_EXCL_LINE
            } else {
                acc
            }
        })
    }

    fn is_mine_safe(&self, i: i32) -> bool {
        matches!(self.get_content_safe(i), Some(&Content::Mine(_)))
    }

    pub fn get_width(&self) -> u32 {
        self.width
    }

    pub fn get_height(&self) -> u32 {
        self.height
    }

    pub fn get_size(&self) -> u32 {
        self.size
    }

    pub fn reset_if_need(&mut self, cursor_ind: u32) {
        if self.need_regen {
            self.reset(cursor_ind);
            self.need_regen = false;
        }
    }

    pub fn reveal_all(&mut self) {
        for i in 0..self.size { // COV_EXCL_LINE
            self.get_cell_mut(i).revealed = true;
        }
    }

    pub fn chain_reveal(&mut self, u: u32) {
        if self.marked(u) { // COV_EXCL_LINE
            return;
        }
        let w = self.width as i32;
        // closure to check for blank cells
        let mut check = |x, d: &mut VecDeque<i32>| {
            match self.get_content_safe(x) { // COV_EXCL_LINE
                Some(&Content::None) => {
                    if !self.revealed(x as u32) {
                        d.push_back(x);
                        self.get_cell_mut(x as u32).marked = false;
                        self.reveal(x as u32);
                    }
                }
                Some(&Content::Number(_n)) => {
                    if !(self.revealed(x as u32)) {
                        self.get_cell_mut(x as u32).marked = false;
                        self.reveal(x as u32);
                    }
                }
                _ => {}
            }
        };
        // BFS initialize
        let deq = &mut VecDeque::new();
        deq.push_back(u as i32);
        // BFS
        while !deq.is_empty() {
            let i = deq.pop_front().unwrap();
            // don`t care about row
            check(i - w, deq);
            check(i + w, deq);
            if i % w > 0 { // COV_EXCL_LINE
                // check left side position
                check(i - w - 1, deq);
                check(i - 1, deq);
                check(i + w - 1, deq);
            }
            if i % w < w - 1 { // COV_EXCL_LINE
                // check right side position
                check(i - w + 1, deq);
                check(i + 1, deq);
                check(i + w + 1, deq);
            }
        }
    }

    pub fn draw(&self) -> RgbImage {
        let mut img: RgbImage = ImageBuffer::new(self.width * TILE_WIDTH + 50, self.height * TILE_HEIGHT + 50);
        let labels = vec![common::LABEL_A, common::LABEL_B, common::LABEL_C, common::LABEL_D, common::LABEL_E, common::LABEL_F, common::LABEL_G, common::LABEL_H, common::LABEL_I, common::LABEL_J, common::LABEL_K, common::LABEL_L, common::LABEL_M, common::LABEL_N, common::LABEL_O, common::LABEL_P, common::LABEL_Q, common::LABEL_R, common::LABEL_S, common::LABEL_T, common::LABEL_U, common::LABEL_V, common::LABEL_W, common::LABEL_X, common::LABEL_Y];
        //labels
        //cols
        for i in 0..self.height { // COV_EXCL_LINE
            let y = ((i + 1) * 50) as i64;
            let label = ImageReader::new(Cursor::new(labels[i as usize])).with_guessed_format().unwrap().decode().unwrap();
            imageops::replace(&mut img, &label.to_rgb8(), 0, y);
        }
        //rows
        for i in 0..self.width { // COV_EXCL_LINE
            let x = ((i + 1) * 50) as i64;
            let label = ImageReader::new(Cursor::new(labels[i as usize])).with_guessed_format().unwrap().decode().unwrap();
            imageops::replace(&mut img, &label.to_rgb8(), x, 0);
        }
        //cells
        for (i, cell) in self.cells.iter().enumerate().map(|(i, cell)| (i as u32, cell)) { // COV_EXCL_LINE
            let row = i / self.width; // COV_EXCL_LINE
            let col = i % self.width; // COV_EXCL_LINE
            let x = ((col + 1) * TILE_WIDTH) as i64;
            let y = ((row + 1) * TILE_HEIGHT) as i64;
            let cell_bytes: &[u8] = match cell.content { // COV_EXCL_LINE
                Content::None => {
                    if cell.revealed { // COV_EXCL_LINE
                        common::TILE_EMPTY // COV_EXCL_LINE
                    } else if cell.marked{ // COV_EXCL_LINE
                        common::TILE_FLAG // COV_EXCL_LINE
                    } else {
                        common::TILE_DEFAULT
                    }
                },
                Content::Number(n) => {
                    if cell.revealed  {
                        match n { // COV_EXCL_LINE
                            1 => common::TILE_1, // COV_EXCL_LINE
                            2 => common::TILE_2, // COV_EXCL_LINE
                            3 => common::TILE_3, // COV_EXCL_LINE
                            4 => common::TILE_4, // COV_EXCL_LINE
                            5 => common::TILE_5, // COV_EXCL_LINE
                            6 => common::TILE_6, // COV_EXCL_LINE
                            7 => common::TILE_7, // COV_EXCL_LINE
                            8 => common::TILE_8, // COV_EXCL_LINE
                            _ => common::TILE_DEFAULT // COV_EXCL_LINE
                        }
                    } else if cell.marked{
                        common::TILE_FLAG
                    } else {
                        common::TILE_DEFAULT
                    }
                },
                Content::Mine(trigger) => {
                    if trigger {
                        common::TILE_MINE_TRIGGER
                    } else if cell.revealed && cell.marked {
                        common::TILE_MINE_UNEXPLODED
                    } else if cell.revealed{
                        common::TILE_MINE_EXPLODED
                    }else if cell.marked {
                        common::TILE_FLAG
                    } else {
                        common::TILE_DEFAULT
                    }
                },
            };
            let tile = ImageReader::new(Cursor::new(cell_bytes)).with_guessed_format().unwrap().decode().unwrap();
            imageops::replace(&mut img, &tile.to_rgb8(), x, y);
        }
        //fill top corner
        draw_filled_rect_mut(&mut img, Rect::at(0, 0).of_size(50, 50), Rgb([21, 71, 52]));

        //highlight row
        let row_start = (self.selected_y + 1) * TILE_HEIGHT;
        draw_hollow_rect_mut(
            &mut img, Rect::at(0, row_start as i32).of_size((self.width + 1) * TILE_WIDTH, 50), Rgb([255, 255, 255])
        );

        //highlight col
        let col_start = (self.selected_x + 1) * TILE_WIDTH;
        draw_hollow_rect_mut(
            &mut img, Rect::at(col_start as i32, 0).of_size(50, (self.height + 1) * TILE_HEIGHT), Rgb([255, 255, 255])
        );
        img
    }

    pub fn move_selection(&mut self, dest: MoveDestination) {
        match dest { // COV_EXCL_LINE
            MoveDestination::Up => {
                if self.selected_y > 0 { // COV_EXCL_LINE
                    self.selected_y -= 1;
                }
            }
            MoveDestination::Down => {
                if self.selected_y < self.height - 1 { // COV_EXCL_LINE
                    self.selected_y += 1;
                }
            }
            MoveDestination::Left => {
                if self.selected_x > 0 { // COV_EXCL_LINE
                    self.selected_x -= 1;
                }
            }
            MoveDestination::Right => {
                if self.selected_x < self.width - 1 { // COV_EXCL_LINE
                    self.selected_x += 1;
                }
            }
        }
    }

    pub fn get_selected_ind(&mut self) -> u32 {
        let x = self.selected_x;
        let y = self.selected_y;
        self.get_cell_index(x, y)
    }

    pub fn is_victory(&self) -> bool {
        self.numbers_total == self.numbers_opened
    }

    pub fn get_x(&self) -> u32 {
        self.selected_x
    }

    pub fn get_y(&self) -> u32 {
        self.selected_y
    }

    /*
    pub fn reinit_field(&mut self, num: u32, param: ParamType) {
        let mut restart_needed = false;
        match param {
            ParamType::Height => {
                if self.height != num {
                    self.height = num;
                    self.reinit_vec();
                    restart_needed = true;
                }
            }
            ParamType::Width => {
                if self.width != num {
                    self.width = num;
                    self.reinit_vec();
                    restart_needed = true;
                }
            }
            ParamType::Mines => {
                if self.mines != num {
                    self.mines = num;
                    restart_needed = true;
                }
            }
        }
        if restart_needed {
            self.restart();
        }
    }
    */

    pub fn toggle_mark(&mut self, i: u32) -> bool {
        let cell = self.get_cell_mut(i);
        if cell.revealed {
            false // COV_EXCL_LINE
        } else {
            cell.toggle_mark();
            true
        }
    }

    pub fn total_mines(&self) -> u32 {
        self.mines
    }

    pub fn get_selected_cell(&mut self) -> &Cell {
        let x = self.selected_x;
        let y = self.selected_y;
        let ind = self.get_cell_index(x, y);
        self.get_cell_mut(ind)
    }
}

// COV_EXCL_START
#[cfg(test)]
mod tests {
    use rand::SeedableRng;
    use super::*;
    #[test]
    fn draw() {
        let mut field = Field::new(10, 10, 10, StdRng::from_os_rng());
        for i in 0..9 {
            field.get_cell_mut(i).content = Content::Number(i as u8);
        }
        field.get_cell_mut(9).content = Content::Number(9);
        field.get_cell_mut(10).content = Content::Mine(false);
        field.get_cell_mut(11).content = Content::Mine(true);
        field.get_cell_mut(12).content = Content::Mine(false);
        field.get_cell_mut(13).content = Content::Mine(false);
        field.get_cell_mut(14).content = Content::Mine(false);
        field.get_cell_mut(15).content = Content::Number(9);
        field.get_cell_mut(16).content = Content::Mine(false);
        field.toggle_mark(12);
        field.toggle_mark(13);
        field.toggle_mark(15);
        field.get_cell_mut(10).revealed = true;
        field.get_cell_mut(12).revealed = true;
        field.draw();
    }
}
//COV_EXCL_STOP
