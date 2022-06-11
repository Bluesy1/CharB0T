# -*- coding: utf-8 -*-
#  ----------------------------------------------------------------------------
#  MIT License
#
# Copyright (c) 2022 Bluesy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#  ----------------------------------------------------------------------------
"""Tic-tac-toe hard class."""
from . import Points, TicTacEasy


class TicTacHard(TicTacEasy):
    """Adaptation of TicTacHard to an easier version.

    See Also
    --------
    :class:`TicTacEasy`
        For the full documentation and implementation.
    """

    @property
    def points(self) -> Points:
        """Return the points of the game.

        Returns
        -------
        Points
            The points of the game.
        """
        win_state = self.check_win()
        if win_state == 1:
            return Points(participation=2, bonus=3)
        if win_state == 0:
            return Points(participation=0, bonus=0)
        return Points(participation=2, bonus=1)

    def next(self) -> tuple[int, int]:
        """Make a move, and return the cell that was played.

        Returns
        -------
        tuple[int, int]
            The x and y position of the move.
        """
        move_x, move_y = self._next_move_easy()
        if isinstance(move_x, int) and isinstance(move_y, int):
            return move_x, move_y

    def _available_moves(self) -> list[tuple[int, int]]:
        """Return a list of available moves.

        Returns
        -------
        list[tuple[int, int]]
            A list of available moves.
        """
        return [(i, j) for i in range(0, self.dim_sz) for j in range(0, self.dim_sz) if self.board[i][j] == "blur"]

    def _win_spots(self, pick1: str, pick2: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        """Return a list of winning moves.

        Parameters
        ----------
        pick1 : str
            The pick to check for the player.
        pick2 : str
            The pick to check for the computer.

        Returns
        -------
        list[tuple[int, int]]
            A list of winning moves.
        """
        win_spots1 = []
        win_spots2 = []
        for i in range(0, self.dim_sz):
            for j in range(0, self.dim_sz):
                if self.board[i][j] == "blur":
                    self.board[i][j] = pick1
                    if self.check_win() == 1:
                        win_spots1.append((i, j))
                    self.board[i][j] = pick2
                    if self.check_win() == 0:
                        win_spots2.append((i, j))
                    self.board[i][j] = "blur"
        return win_spots1, win_spots2

    def _simple_move_checks(
        self,
        comp: list[tuple[int, int]],
        player: list[tuple[int, int]],
        available: list[tuple[int, int]],
        comp_pick: str,
    ) -> int | tuple[int, int]:
        """Check if there is a simple move.

        Parameters
        ----------
        comp : list[tuple[int, int]]
            The computer's moves that would win the game for the computer.
        player : list[tuple[int, int]]
            The player's moves that would win the game for the player.
        available : list[tuple[int, int]]
            The available moves.
        comp_pick : str
            The pick for the computer.

        Returns
        -------
        int | tuple[int, int]
            The move to make, or 0 if there is no simple move.
        """
        if len(comp) != 0:
            return comp[0]
        if len(player) != 0:
            self.board[player[0][0]][player[0][1]] = comp_pick
            return player[0]
        if len(available) == 1:
            self.board[available[0][0]][available[0][1]] = comp_pick
            return available[0]
        if len(available) == 0:
            return -1, -1
        if self.board[0][0] == self.pick and self.board[2][2] == self.pick:
            if self.board[0][2] == "blur":
                self.board[0][2] = comp_pick
                return 0, 2
            if self.board[2][0] == "blur":
                self.board[2][0] = comp_pick
                return 2, 0
        if self.board[0][2] == self.pick and self.board[2][0] == self.pick:
            if self.board[0][0] == "blur":
                self.board[0][0] = comp_pick
                return 0, 0
            if self.board[2][2] == "blur":
                self.board[2][2] = comp_pick
                return 2, 2
        return 0

    def _complex_move_checks(self, available: list[tuple[int, int]], comp_pick: str) -> int | tuple[int, int]:
        """Check if there is a complex move.

        Parameters
        ----------
        available : list[tuple[int, int]]
            The available moves.
        comp_pick : str
            The pick for the computer.

        Returns
        -------
        int | tuple[int, int]
            The move to make, or 0 if there is no complex move.
        """
        c1, c2 = self.dim_sz // 2, self.dim_sz // 2
        for i in range(c1 - 1, -1, -1):  # IN TO OUT
            gap = c1 - i
            # checking  - 4 possibilities at max
            # EDGES
            if (c1 - gap, c2 - gap) in available:
                self.board[c1 - gap][c2 - gap] = comp_pick
                return c1 - gap, c2 - gap
            if (c1 - gap, c2 + gap) in available:
                self.board[c1 - gap][c2 + gap] = comp_pick
                return c1 - gap, c2 + gap
            if (c1 + gap, c2 - gap) in available:
                self.board[c1 + gap][c2 - gap] = comp_pick
                return c1 + gap, c2 - gap
            if (c1 + gap, c2 + gap) in available:
                self.board[c1 + gap][c2 + gap] = comp_pick
                return c1 + gap, c2 + gap

            # Four Lines

            for j in range(0, gap):
                if (c1 - gap, c2 - gap + j) in available:  # TOP LEFT TO TOP RIGHT
                    self.board[c1 - gap][c2 - gap + j] = comp_pick
                    return c1 - gap, c2 - gap + j
                if (c1 + gap, c2 - gap + j) in available:  # BOTTOM LEFT TO BOTTOM RIGHT
                    self.board[c1 + gap][c2 - gap + j] = comp_pick
                    return c1 + gap, c2 - gap + j
                if (c1 - gap + j, c2 - gap) in available:  # LEFT TOP TO LEFT BOTTOM
                    self.board[c1 - gap + j][c2 - gap] = comp_pick
                    return c1 - gap + j, c2 - gap
                if (c1 - gap + j, c2 + gap) in available:  # RIGHT TOP TO RIGHT BOTTOM
                    self.board[c1 - gap + j][c2 + gap] = comp_pick
                    return c1 - gap + j, c2 + gap
        return 0

    def _next_move_easy(self) -> tuple[int, int]:
        """Make a move, and return the cell that was played.

        Returns
        -------
        tuple[int, int]
            The cell that was played.
        """
        available_moves = self._available_moves()  # will carry all available moves
        comp_pick = "O"
        if self.pick == "O":
            comp_pick = "X"
        # if player (user Wins), if computer (computer Wins)
        player_win_spot, comp_win_spots = self._win_spots(self.pick, comp_pick)
        simple_move = self._simple_move_checks(comp_win_spots, player_win_spot, available_moves, comp_pick)
        if isinstance(simple_move, tuple):
            return simple_move
        c1, c2 = self.dim_sz // 2, self.dim_sz // 2
        if (c1, c2) in available_moves:  # CENTER
            self.board[c1][c2] = comp_pick
            return c1, c2
        complex_move = self._complex_move_checks(available_moves, comp_pick)
        if isinstance(complex_move, tuple):
            return complex_move
        raise RuntimeError("No moves available")
