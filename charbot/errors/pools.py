# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Wrong roles error."""
from typing import cast

import discord
from discord.app_commands import CheckFailure

from . import _LanguageTag
from charbot_rust import translate


class NoPoolFound(CheckFailure):
    """No pool found."""

    def __init__(self, pool: str, locale: discord.Locale):
        """Init."""
        message = translate(cast(_LanguageTag, locale.value), "no-pool-found", {"pool": pool})
        super().__init__(pool, message)
        self.message = message
