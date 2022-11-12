# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Gang war package."""
from .. import CBot
from .utils import ColorOpts, rep_to_control, BASE_GANG_COST, GANGS, SQL_MONTHLY
from .dues import DuesButton
from .cog import Gangs
from . import actions, types

__all__ = (
    "Gangs",
    "DuesButton",
    "ColorOpts",
    "BASE_GANG_COST",
    "GANGS",
    "SQL_MONTHLY",
    "actions",
    "rep_to_control",
    "types",
)


async def setup(bot: CBot):  # pragma: no cover
    """Setup."""
    import sys
    import importlib

    sys.modules["charbot.gangs.banner"] = importlib.reload(sys.modules["charbot.gangs.banner"])
    sys.modules["charbot.gangs.cog"] = importlib.reload(sys.modules["charbot.gangs.cog"])
    sys.modules["charbot.gangs.dues"] = importlib.reload(sys.modules["charbot.gangs.dues"])
    sys.modules["charbot.gangs.enums"] = importlib.reload(sys.modules["charbot.gangs.enums"])
    sys.modules["charbot.gangs.types"] = importlib.reload(sys.modules["charbot.gangs.types"])
    sys.modules["charbot.gangs.shakedowns"] = importlib.reload(sys.modules["charbot.gangs.shakedowns"])
    sys.modules["charbot.gangs.utils"] = importlib.reload(sys.modules["charbot.gangs.utils"])
    sys.modules["charbot.gangs.actions"] = importlib.reload(sys.modules["charbot.gangs.actions"])
    sys.modules["charbot.gangs.actions.banner"] = importlib.reload(sys.modules["charbot.gangs.actions.banner"])
    sys.modules["charbot.gangs.actions.create"] = importlib.reload(sys.modules["charbot.gangs.actions.create"])
    sys.modules["charbot.gangs.actions.gang_items"] = importlib.reload(sys.modules["charbot.gangs.actions.gang_items"])
    sys.modules["charbot.gangs.actions.join"] = importlib.reload(sys.modules["charbot.gangs.actions.join"])
    sys.modules["charbot.gangs.actions.raid"] = importlib.reload(sys.modules["charbot.gangs.actions.raid"])
    sys.modules["charbot.gangs.actions.user_items"] = importlib.reload(sys.modules["charbot.gangs.actions.user_items"])
    await bot.add_cog(Gangs(bot))
