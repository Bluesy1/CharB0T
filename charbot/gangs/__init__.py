# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Gang war package."""
from .. import CBot
from .models import ColorOpts, GANGS, SQL_MONTHLY
from .dues import DuesButton
from .cog import Gangs
from . import actions

__all__ = ("Gangs", "DuesButton", "ColorOpts", "GANGS", "SQL_MONTHLY", "actions")


async def setup(bot: CBot):  # pragma: no cover
    """Setup."""
    await bot.add_cog(Gangs(bot))
