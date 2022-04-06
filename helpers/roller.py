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
"""
Roller Module
"""
import random


def roll(arg: str) -> str:
    """Dice roller

    Parameters
    ----------
    arg : str
        Dice roll string
    """
    roll_error = (
        "Error invalid argument: specified dice can only be d<int>,"
        " or if a constant modifier must be a "
        "perfect integer, positive or negative, "
        "connected with `+`, and no spaces."
    )
    if "+" in arg:
        dice = arg.split("+")
    else:
        dice = [str(arg)]
    try:
        sums = 0
        rolls = []
        for die in dice:
            if "d" in die:
                try:
                    num_rolls = int(die[: die.find("d")])
                except ValueError:
                    num_rolls = 1
                i = 1
                while i <= num_rolls:
                    roll1 = random.randint(1, int(die[die.find("d") + 1 :]))
                    rolls.append(roll1)
                    sums += roll1
                    i += 1
            else:
                try:
                    rolls.append(int(die))
                    sums += int(die)
                except ValueError:
                    return roll_error
        output = "`"
        for roll1 in rolls:
            output += str(roll1) + ", "
        output = output[:-2]
        return f"rolled `{arg}` got {output}` for a total value of: {str(sums)}"
    except Exception:  # skipcq: PYL-W0703
        return roll_error
