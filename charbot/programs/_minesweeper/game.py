import pathlib
import random
import string
from io import BytesIO
from typing import Final, assert_never

from PIL import Image, ImageDraw

from .cell import Cell


MEDIA_BASE = pathlib.Path(__file__).parent.parent.parent / "media/minesweeper"
LABEL_BASE = MEDIA_BASE / "labels"
TILE_BASE = MEDIA_BASE / "tiles"


class Game:
    def __init__(self, width: int, mines: int) -> None:
        self.width: Final[int] = width
        self.mines: Final[int] = mines
        self.size = width**2
        self.cells: list[Cell] = []
        self.selected_col = init_selected = width // 2
        self.selected_row = init_selected
        self.numbers_total = self.numbers_needed = 0
        self.__initialized = False
        self.points = (0, 0)  # TODO: implement points properly

    @property
    def height(self):
        return self.width

    @property
    def x(self):
        return self.selected_col

    @property
    def y(self):
        return self.selected_row

    @property
    def selected_cell(self) -> Cell:
        idx = self.selected_col + self.selected_row * self.width
        return self.cells[idx]

    def get_neighbors(self, x: int, y: int) -> list[int]:
        begin_x = x - 1 if x > 0 else x
        end_x = x - 1 if x < self.width else x
        begin_y = y - 1 if y > 0 else y
        end_y = y - 1 if y < self.height else y
        idxs: list[int] = []
        for new_x in range(begin_x, end_x + 1):
            for new_y in range(begin_y, end_y + 1):
                if new_x != x and new_y != y:
                    idxs.append(x + y * self.width)
        return idxs

    def reset(self):
        if self.__initialized:
            return
        self.numbers_total = self.numbers_needed = 0
        cells_near_selected = self.get_neighbors(self.selected_col, self.selected_row)
        cells = [Cell(False) if i < self.mines else Cell() for i in range(self.size - len(cells_near_selected))]
        random.shuffle(cells)
        for idx in cells_near_selected:
            cells.insert(idx, Cell())
        self.cells = cells
        self.write_numbers_near_mines()
        self.__initialized = True

    def write_numbers_near_mines(self):
        width = self.width

        def check_pos(idx: int) -> int:
            try:
                cell = self.cells[idx]
            except IndexError:
                return 0
            else:
                if isinstance(cell.content, bool):
                    return int(cell.content)
            return 0

        for pos in range(self.size):
            if self.cells[pos].content is not None:
                continue
            mines = 0
            # Above and below:
            mines += check_pos(pos - width)
            mines += check_pos(pos + width)
            # Left size
            if pos % width > 0:
                mines += check_pos(pos - 1 - width)
                mines += check_pos(pos - 1)
                mines += check_pos(pos - 1 + width)
            # Right size
            if pos % width < width - 1:
                mines += check_pos(pos + 1 - width)
                mines += check_pos(pos + 1)
                mines += check_pos(pos + 1 + width)
            if mines:
                # We know at this point mines is an int from 1 to 8
                self.cells[pos].content = mines  # pyright: ignore[reportAttributeAccessIssue]
                self.numbers_total += 1

    def draw(self) -> BytesIO:
        img_size = (self.width + 1) * 50
        img = Image.new("RGB", (img_size, img_size), color=(21, 71, 52))
        for i, letter in enumerate(string.ascii_uppercase[: self.width], start=1):
            i *= 50
            label = LABEL_BASE / f"{letter}.png"
            label = Image.open(label)
            img.paste(label, (i, 0))
            img.paste(label, (0, i))

        for i, cell in enumerate(self.cells):
            row = i // self.width
            col = i % self.width
            x = (row + 1) * 50
            y = (col + 1) * 50
            tile = TILE_BASE / "default.png"
            match cell.content:
                case bool(trigger):
                    if trigger:
                        tile = tile.with_stem("mine3")
                    elif cell.revealed and cell.marked:
                        tile = tile.with_stem("mine2")
                    elif cell.revealed:
                        tile = tile.with_stem("mine1")
                    elif cell.marked:
                        tile = tile.with_stem("flag")
                case 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 as mine_count:
                    if cell.revealed:
                        tile = tile.with_stem(str(mine_count))
                    elif cell.marked:
                        tile = tile.with_stem("flag")
                case None:
                    if cell.revealed:
                        tile = tile.with_stem("empty")
                    elif cell.marked:
                        tile = tile.with_stem("flag")
                case unexpected:
                    assert_never(unexpected)
            img.paste(Image.open(tile), (x, y))

        draw = ImageDraw.Draw(img)
        row_start = (self.selected_row + 1) * 50
        col_start = (self.selected_col + 1) * 50
        draw.rectangle([(0, row_start), (img_size, row_start + 50)], fill=None, outline=(255, 255, 255))
        draw.rectangle([(col_start, 0), (col_start + 50, img_size)], fill=None, outline=(255, 255, 255))

        result = BytesIO()
        img.save(result, "PNG")
        result.seek(0)
        return result

    def change_row(self, row: int) -> None:
        if 0 <= row < self.height and isinstance(row, int):
            self.selected_row = row
        else:
            raise ValueError(f"Expected an integer between 0 and {self.height}, got {row!r} instead.")

    def change_col(self, col: int) -> None:
        if 0 <= col < self.height and isinstance(col, int):
            self.selected_col = col
        else:
            raise ValueError(f"Expected an integer between 0 and {self.width}, got {col!r} instead.")

    def reveal(self):
        raise NotImplementedError()

    def chord(self):
        raise NotImplementedError()

    def toggle_flag(self):
        raise NotImplementedError()

    def quit(self):
        raise NotImplementedError()

    def is_win(self):
        raise NotImplementedError()
