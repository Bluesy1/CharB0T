# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Wrong roles error."""
import discord
from discord.app_commands import MissingAnyRole
from fluent.runtime import FluentResourceLoader, FluentLocalization


LOADER = FluentResourceLoader("i18n/{locale}")


class MissingProgramRole(MissingAnyRole):
    """Wrong roles' error.

    Raised when the command is not run in the right channel.

    Parameters
    ----------
    roles : list
        The roles the command should be run with.
    """

    def __init__(self, roles: list[int | str], locale: discord.Locale):
        super().__init__(roles)
        missing = [f"'{role}'" for role in roles]

        if len(missing) > 2:
            fmt = f"{', '.join(missing[:-1])}, or {missing[-1]}"
        else:
            fmt = " or ".join(missing)
        translator = FluentLocalization([locale.value, "en-US"], ["errors.ftl"], LOADER)
        self.message = translator.format_value("missing-program-role", {"roles": fmt})

    def __str__(self):
        """Get the error as a string."""
        return self.message
