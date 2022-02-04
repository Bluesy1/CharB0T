import random

import lightbulb


async def roll(ctx: lightbulb.Context):  # pylint: disable=unused-variable
    """Dice roller"""
    roll_error = ("Error invalid argument: specified dice can only be d2s, d4s, d6s, d8s, d10s, d12s, d20s, "
                  "or d100s, or if a constant modifier must be a perfect integer, positive or negative, "
                  "connexted with `+`, and no spaces.")
    arg = ctx.options.dice
    if "+" in arg:
        dice = arg.split("+")
    else:
        dice = [str(arg)]
    try:
        sums = 0
        rolls = []
        allowed_dice = [2, 4, 6, 8, 10, 12, 20, 100]
        for die in dice:
            if 'd' in die:
                if int(die[die.find('d') + 1:]) not in allowed_dice:
                    await ctx.respond(roll_error)
                    return
                try:
                    num_rolls = int(die[:die.find('d')])
                except ValueError:
                    num_rolls = 1
                i = 1
                while i <= num_rolls:
                    roll1 = random.randint(1, int(die[die.find('d') + 1:]))
                    rolls.append(roll1)
                    sums += roll1
                    i += 1
            else:
                try:
                    rolls.append(int(die))
                    sums += int(die)
                except ValueError:
                    await ctx.respond(roll_error, reply=True)
                    return
        output = '`'
        for roll1 in rolls:
            output += str(roll1) + ', '
        output = output[:-2]
        await ctx.respond(f"Kethran rolled `{arg}` got {output}` for a total value of: {str(sums)}", reply=True)
    except Exception:  # pylint: disable=broad-except
        await ctx.respond(roll_error, reply=True)
