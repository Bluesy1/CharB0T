import random

import lightbulb


async def roll(ctx: lightbulb.Context):  # pylint: disable=unused-variable
    """Dice roller"""
    roll_error = ("Error invalid argument: specified dice can only be d<int>, or if a constant modifier must be a "
                  "perfect integer, positive or negative, "
                  "connexted with `+`, and no spaces.")
    arg = ctx.options.dice
    if "+" in arg:
        dice = arg.split("+")
    else:
        dice = [str(arg)]
    try:
        sums = 0
        rolls = []
        for die in dice:
            if 'd' in die:
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
        if ctx.guild_id == 878426206561775676:
            await ctx.respond(f"Kethran rolled `{arg}` got {output}` for a total value of: {str(sums)}", reply=True)
        else:
            await ctx.respond(
                f"{ctx.member.display_name} rolled `{arg}` got {output}` for a total value of: {str(sums)}", reply=True)
    except Exception:  # pylint: disable=broad-except
        await ctx.respond(roll_error, reply=True)
