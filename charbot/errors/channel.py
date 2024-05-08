"""Wrong channel error."""

from discord.app_commands import AppCommandError


class WrongChannelError(AppCommandError):
    """Wrong channel error.

    Raised when the command is not run in the right channel.

    Parameters
    ----------
    channel : int
        The channel ID the command should be run in.
    """

    def __init__(self, channel: int):
        """Init."""
        super().__init__()
        self.message = f"This command can only be run in the channel <#{channel}> ."
        self._channel: int = channel

    def __str__(self):
        """Get the error as a string."""
        return self.message
