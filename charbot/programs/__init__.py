# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

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
