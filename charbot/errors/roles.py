"""Wrong roles error."""

from discord.app_commands import MissingAnyRole


class MissingProgramRole(MissingAnyRole):
    """Wrong roles' error.

    Raised when the command is not run in the right channel.

    Parameters
    ----------
    roles : list
        The roles the command should be run with.
    """

    def __init__(self, roles: list[int | str]):
        super().__init__(roles)
        missing = [f"'{role}'" for role in roles]

        fmt = (
            f"{', '.join(missing[:-1])} or {missing[-1]}"
            if len(missing) > 2
            else " or ".join(missing)
            if len(missing) == 2
            else missing[0]
        )
        self.message = (
            f"You are missing at least one of the required roles: {fmt} - "
            + "you must be at least level 1 to use this command/button."
        )

    def __str__(self):
        """Get the error as a string."""
        return self.message
