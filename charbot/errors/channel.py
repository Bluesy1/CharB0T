# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Wrong channel error."""
import discord
from discord.app_commands import AppCommandError

from charbot_rust import translate


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
        self.message = translate(locale.value, "wrong-channel", {"channelid": f"{channel}"})
        self._channel: int = channel

    def __str__(self):
        """Get the error as a string."""
        return self.message
