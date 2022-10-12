# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Wrong roles error."""
import discord
from discord.app_commands import CheckFailure
from fluent.runtime import FluentResourceLoader, FluentLocalization


LOADER = FluentResourceLoader("i18n/{locale}")


class NoPoolFound(CheckFailure):
    """No pool found."""

    def __init__(self, pool: str, locale: discord.Locale):
        """Init."""
        translator = FluentLocalization([locale.value, "en-US"], ["errors.ftl"], LOADER)
        message = translator.format_value("no-pool-found", {"pool": pool})
        super().__init__(pool, message)
        self.message = message
