# -*- coding: utf-8 -*-
"""Game giveaway extension."""

__all__ = ("Giveaway", "BidModal", "GiveawayView", "setup")

from .. import CBot
from .modal import BidModal
from .view import GiveawayView
from .cog import Giveaway


async def setup(bot: CBot):  # pragma: no cover
    """Giveaway cog setup.

    Parameters
    ----------
    bot : CBot
        The bot to add the cog to.
    """
    import sys
    import importlib

    sys.modules["charbot.giveaway.cog"] = importlib.reload(sys.modules["charbot.giveaway.cog"])
    sys.modules["charbot.giveaway.modal"] = importlib.reload(sys.modules["charbot.giveaway.modal"])
    sys.modules["charbot.giveaway.view"] = importlib.reload(sys.modules["charbot.giveaway.view"])
    await bot.add_cog(Giveaway(bot), override=True)
