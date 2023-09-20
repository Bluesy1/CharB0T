# -*- coding: utf-8 -*-
"""Program classes and functions."""
from __future__ import annotations

from .cog import Reputation
from .. import CBot

__all__ = ("setup",)


async def setup(bot: CBot) -> None:  # pragma: no cover
    """Load the cog.

    Parameters
    ----------
    bot : CBot
    """
    await bot.add_cog(Reputation(bot), override=True)
