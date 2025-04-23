import random
from typing import Final

from .cell import Cell


class Field:
    def __init__(self, width: int, mines: int) -> None:
        self.width: Final[int] = width
        self.mines: Final[int] = mines
        self.size = width**2
        self.cells: list[Cell] = []
        self.selected_x = init_selected = width // 2
        self.selected_y = init_selected
        self.numbers_total = self.numbers_needed = 0
        self.__initialized = False

    @property
    def height(self):
        return self.width

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
        cells_near_selected = self.get_neighbors(self.selected_x, self.selected_y)
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
