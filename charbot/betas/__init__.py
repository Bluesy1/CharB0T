# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Betas package."""
from .. import CBot
from .models import ColorOpts, COLORS
from .cog import Betas

__all__ = ("Betas", "ColorOpts", "COLORS")


async def setup(bot: CBot):  # pragma: no cover
    """Setup."""
    await bot.add_cog(Betas(bot))
