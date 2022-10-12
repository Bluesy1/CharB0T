# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""Betas models."""
from enum import Enum
from typing import Literal

from discord import Color


__all__ = ("ColorOpts", "COLORS")


class ColorOpts(Enum):
    """Enum mapping of color name to discord colors"""

    Black = Color(0x36454F)  # actually called charcoal, but is close enough to black
    Red = Color.dark_red()
    Green = Color.green()
    Blue = Color(0x0000FF)
    Purple = Color(0x800080)
    Violet = Color(0xEE82EE)
    Yellow = Color(0xFFD700)
    Orange = Color(0xFF6200)
    White = Color(0xC0C0C0)  # actually called silver, but is close enough to white


COLORS = Literal["Black", "Red", "Green", "Blue", "Purple", "Violet", "Yellow", "Orange", "White"]
