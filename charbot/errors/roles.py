"""Wrong roles error."""

from typing import cast

import discord
from discord.app_commands import MissingAnyRole

from charbot_rust import translate

from . import _LanguageTag


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

        fmt = (
            f"{', '.join(missing[:-1])} or {missing[-1]}"
            if len(missing) > 2
            else " or ".join(missing)
            if len(missing) == 2
            else missing[0]
        )
        self.message = translate(cast(_LanguageTag, locale.value), "missing-program-role", {"roles": fmt})

    def __str__(self):
        """Get the error as a string."""
        return self.message
