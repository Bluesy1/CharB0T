# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT
"""Rolls dice."""
import random

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Context

from charbot import CBot, translate


def roll(arg: str, user: str, locale: discord.Locale) -> str:
    """Dice roller.

    Parameters
    ----------
    arg : str
        Dice roll string
    user: str
        Name to attribute to the user
    locale: discord.Locale
        The locale to use for translation
    """
    dice = arg.split("+") if "+" in arg else [arg]
    # noinspection PyBroadException
    try:
        sums = 0
        rolls = []
        for die in dice:
            if "d" in die:
                try:
                    num_rolls = int(die[: die.find("d")])
                except ValueError:
                    num_rolls = 1
                for _ in range(1, num_rolls + 1):
                    # fmt: off
                    roll1 = random.randint(1, int(die[die.find("d") + 1:]))
                    # fmt: on
                    rolls.append(roll1)
                    sums += roll1
            else:
                try:
                    rolls.append(int(die))
                    sums += int(die)
                except ValueError:
                    return translate(locale.value, "error", {"user": user})
        output = ", ".join(f"{res}" for res in rolls)
        return translate(
            locale.value, "success", {"user": user, "dice": arg, "total": sums, "result": output, "locale": "en-US"}
        )
    except Exception:  # skipcq: PYL-W0703
        return translate(locale.value, "error", {"user": user})


class Roll(Cog):
    """Roll cog.

    Parameters
    ----------
    bot : Bot
        The bot object to bind the cog to.

    Attributes
    ----------
    bot : Bot
        The bot object the cog is attached to.

    Methods
    -------
    cog_check(ctx)
        Checks if the user has the required permissions to use the cog.
    roll(ctx, *, dice: str)
        Rolls dice.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        """Check to run for all cog commands.

        Parameters
        ----------
        ctx : Context
            The context of the command.
        """
        if ctx.guild is None:
            return False
        author = ctx.author
        assert isinstance(author, discord.Member)  # skipcq: BAN-B101
        return any(role.id in (338173415527677954, 253752685357039617, 225413350874546176) for role in author.roles)

    @commands.command()
    async def roll(self, ctx: Context[CBot], *, dice: str):
        """Dice roller.

        Parameters
        ----------
        ctx : Context
            The context of the command.
        dice : str
            The dice to roll.
        """
        await ctx.reply(
            roll(dice, ctx.author.mention, discord.Locale.american_english),
            mention_author=True,
        )


async def setup(bot: commands.Bot):
    """Load Roll cog.

    Parameters
    ----------
    bot : Bot
        The bot object to bind the cog to.
    """
    await bot.add_cog(Roll(bot))
