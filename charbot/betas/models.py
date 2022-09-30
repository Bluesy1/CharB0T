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
