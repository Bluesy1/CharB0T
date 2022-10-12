# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""Betas package."""
from .. import CBot
from .models import ColorOpts, COLORS
from .cog import Betas

__all__ = ("Betas", "ColorOpts", "COLORS")


async def setup(bot: CBot):
    """Setup."""
    await bot.add_cog(Betas(bot))
