"""Wrong channel error."""

from typing import cast

import discord
from discord.app_commands import AppCommandError

from charbot_rust import translate

from . import _LanguageTag


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
        self.message = translate(cast(_LanguageTag, locale.value), "wrong-channel", {"channel-id": f"{channel}"})
        self._channel: int = channel

    def __str__(self):
        """Get the error as a string."""
        return self.message
