"""Betas package."""

from .. import CBot  # isort: skip
from .models import COLORS, ColorOpts  # isort: skip
from .cog import Betas


__all__ = ("Betas", "ColorOpts", "COLORS")


async def setup(bot: CBot):  # pragma: no cover
    """Setup."""
    await bot.add_cog(Betas(bot))
