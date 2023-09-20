# -*- coding: utf-8 -*-
"""Betas package."""
from .. import CBot
from .models import ColorOpts, COLORS
from .cog import Betas

__all__ = ("Betas", "ColorOpts", "COLORS")


async def setup(bot: CBot):  # pragma: no cover
    """Setup."""
    await bot.add_cog(Betas(bot))
