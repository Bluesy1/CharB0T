"""Game giveaway extension."""

__all__ = ("Giveaway", "BidModal", "GiveawayView", "setup")

from .. import CBot
from .cog import Giveaway
from .modal import BidModal
from .view import GiveawayView


async def setup(bot: CBot):  # pragma: no cover
    """Giveaway cog setup.

    Parameters
    ----------
    bot : CBot
        The bot to add the cog to.
    """
    import importlib
    import sys

    sys.modules["charbot.giveaway.cog"] = importlib.reload(sys.modules["charbot.giveaway.cog"])
    sys.modules["charbot.giveaway.modal"] = importlib.reload(sys.modules["charbot.giveaway.modal"])
    sys.modules["charbot.giveaway.view"] = importlib.reload(sys.modules["charbot.giveaway.view"])
    await bot.add_cog(Giveaway(bot), override=True)
