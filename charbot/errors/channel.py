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
"""Wrong channel error."""
import discord
from discord.app_commands import AppCommandError
from fluent.runtime import FluentResourceLoader, FluentLocalization


LOADER = FluentResourceLoader("i18n")


class WrongChannelError(AppCommandError):
    """Wrong channel error.

    Raised when the command is not run in the right channel.

    Parameters
    ----------
    channel : int
        The channel ID the command should be run in.
    """

    def __init__(self, channel: int, locale: discord.Locale):
        """Init."""
        super().__init__()
        translator = FluentLocalization(LOADER, [locale.value, "en-US"], ["errors.ftl"])
        self.message = translator.format_value("wrong-channel", {"channelid": self._channel})
        self._channel: int = channel

    def __str__(self):
        """Get the error as a string."""
        return self.message
