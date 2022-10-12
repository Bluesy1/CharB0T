# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT
from enum import IntEnum

__all__ = ("Difficulty",)


class Difficulty(IntEnum):
    """Represents the difficulty level of the game."""

    EASY = 1
    MEDIUM = 2
    HARD = 3
    RANDOM = 4
