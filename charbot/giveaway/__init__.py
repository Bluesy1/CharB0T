# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Game giveaway extension."""

__all__ = ("Giveaway", "BidModal", "GiveawayView", "setup")

from .. import CBot
from .cog import Giveaway
from .modal import BidModal
from .view import GiveawayView


async def setup(bot: CBot):
    """Giveaway cog setup.

    Parameters
    ----------
    bot : CBot
        The bot to add the cog to.
    """
    await bot.add_cog(Giveaway(bot), override=True)
