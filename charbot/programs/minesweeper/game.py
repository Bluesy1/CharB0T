import enum
import pathlib
import random
import string
from collections import deque
from io import BytesIO
from typing import Final, assert_never

from PIL import Image, ImageDraw

from .cell import Cell


MEDIA_BASE = pathlib.Path(__file__).parent.parent.parent / "media/minesweeper"
LABEL_BASE = MEDIA_BASE / "labels"
TILE_BASE = MEDIA_BASE / "tiles"


class RevealResult(enum.Enum):
    """An enum that represents the result of a reveal operation.

    Flagged:
        The cell was flagged, the flag was removed, but to reveal the cell, call again.
    Mine:
        The cell was a mine, the game is over.
    Empty:
        The cell was empty, floodfill has occurred.
    Number:
        The cell was adjacent to mines.
    """

    Flagged = 0
    Mine = 1
    Empty = 2
    Number = 3


class ChordResult(enum.Enum):
    """An enum that represents the result of a chard operation.

    Failed:
        The cell was not revealed, not a number, or didn't have the appropriate amount of flags.
    Success:
        The chord was performed properly and no mines were revealed.
    Death:
        The chord was performed, but a mine was revealed, ending the game.
    """

    Failed = 0
    Success = 1
    Death = 2


type ResultPoints = tuple[int, int]


class Game:
    def __init__(self, width: int, mines: int, on_win: ResultPoints, on_lose: ResultPoints) -> None:
        self.width: Final[int] = width
        self.mines: Final[int] = mines
        self.__win_points: Final[ResultPoints] = on_win
        self.__lose_points: Final[ResultPoints] = on_lose
        self.size = size = width**2
        self.cells = [Cell()] * size
        self.selected_col = init_selected = width // 2
        self.selected_row = init_selected
        self.numbers_total = self.numbers_opened = 0
        self.__initialized = False
        self._quit = False

    @classmethod
    def beginner(cls):
        return cls(8, 10, (1, 1), (1, 0))

    @classmethod
    def intermediate(cls):
        return cls(8, 10, (2, 3), (2, 0))

    @classmethod
    def expert(cls):
        return cls(8, 10, (2, 4), (2, 0))

    @classmethod
    def super_expert(cls):
        return cls(8, 10, (3, 5), (3, 0))

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
    def points(self) -> tuple[int, int]:
        return self.__win_points if self.is_win() else self.__lose_points

    @property
    def selected_cell(self) -> Cell:
        idx = self.selected_col + (self.selected_row * self.width)
        return self.cells[idx]

    def get_neighbors(self, x: int, y: int, /) -> list[int]:
        begin_x = x - 1 if x > 0 else x
        end_x = x + 1 if x < self.width - 1 else x
        begin_y = y - 1 if y > 0 else y
        end_y = y + 1 if y < self.height - 1 else y
        idxs: list[int] = []
        for new_x in range(begin_x, end_x + 1):
            for new_y in range(begin_y, end_y + 1):
                if new_x != x or new_y != y:
                    idxs.append(new_x + (new_y * self.width))
        return idxs

    def get_neighbors_for_idx(self, idx: int) -> list[int]:
        x = idx % self.width
        y = idx // self.width
        return self.get_neighbors(x, y)

    def reset(self):
        if self.__initialized:
            return
        self.numbers_total = self.numbers_opened = 0
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
                pass
            else:
                if isinstance(cell.content, bool):
                    return 1
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
            x = (col + 1) * 50
            y = (row + 1) * 50
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
                case unexpected:  # pragma: no cover
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
        else:  # pragma: no cover
            raise ValueError(f"Expected an integer between 0 and {self.height}, got {row!r} instead.")

    def change_col(self, col: int) -> None:
        if 0 <= col < self.height and isinstance(col, int):
            self.selected_col = col
        else:  # pragma: no cover
            raise ValueError(f"Expected an integer between 0 and {self.width}, got {col!r} instead.")

    def reveal(self) -> RevealResult:
        if not self.__initialized:
            self.reset()
        if self.selected_cell.marked:
            self.selected_cell.marked = False
            return RevealResult.Flagged
        self.selected_cell.revealed = True
        content = self.selected_cell.content
        match content:
            case bool(_):
                self._reveal_all()
                self.selected_cell.content = True
                self._quit = True
                return RevealResult.Mine
            case 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8:
                self.numbers_opened += 1
                return RevealResult.Number
            case None:
                self._chain_reveal(self.selected_col + (self.selected_row * self.width))
                return RevealResult.Empty
            case unexpected:  # pragma: no cover
                assert_never(unexpected)

    def _chain_reveal(self, idx: int):
        if self.cells[idx].marked:
            return
        queue = deque([idx])

        def check_idx(i: int):
            if 0 <= i < self.size:
                cell = self.cells[i]
                if cell.revealed:
                    return
                content = cell.content
                if not isinstance(content, bool):
                    cell.marked = False
                    cell.revealed = True
                    if cell.content is None:
                        queue.append(i)
                    else:
                        self.numbers_opened += 1

        while queue:
            for neighbor in self.get_neighbors_for_idx(queue.popleft()):
                check_idx(neighbor)

    def _reveal_all(self):
        for cell in self.cells:
            cell.revealed = True

    def chord(self) -> ChordResult:
        if self.selected_cell.revealed is False:  # Cell must be revealed
            return ChordResult.Failed
        content = self.selected_cell.content
        # Cell must be a number
        if not isinstance(content, int) or isinstance(content, bool):
            return ChordResult.Failed
        marked_count = 0
        neighbors = self.get_neighbors(self.selected_col, self.selected_row)
        for idx in neighbors:
            cell = self.cells[idx]
            if cell.marked and not cell.revealed:
                marked_count += 1
        if marked_count != content:
            return ChordResult.Failed

        for idx in neighbors:
            cell = self.cells[idx]
            if cell.marked:
                continue
            cell.revealed = True
            if isinstance(cell.content, bool):
                cell.content = True
                self._reveal_all()
                return ChordResult.Death
            if cell.content is None:
                self._chain_reveal(idx)

        return ChordResult.Success

    def toggle_flag(self):
        if self.selected_cell.revealed is True:
            return False
        self.selected_cell.marked = not self.selected_cell.marked
        return True

    def quit(self):
        self._quit = True
        self._reveal_all()

    def is_win(self):
        if self._quit:
            return False
        return self.numbers_total == self.numbers_opened
