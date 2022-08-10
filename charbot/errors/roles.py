# -*- coding: utf-8 -*-
#  ----------------------------------------------------------------------------
#  MIT License
#
# Copyright (c) 2022 Bluesy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#  ----------------------------------------------------------------------------
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
            fmt = "{}, or {}".format(", ".join(missing[:-1]), missing[-1])
        else:
            fmt = " or ".join(missing)
        translator = FluentLocalization([locale.value, "en-US"], ["errors.ftl"], LOADER)
        self.message = translator.format_value("missing-program-role", {"roles": fmt})

    def __str__(self):
        """Get the error as a string."""
        return self.message
