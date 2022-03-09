# coding=utf-8
import random


def roll(arg: str) -> str:
    """Dice roller"""
    roll_error = (
        "Error invalid argument: specified dice can only be d<int>, or if a constant modifier must be a "
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
    except Exception:
        return roll_error
