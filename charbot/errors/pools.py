"""Wrong roles error."""

from discord.app_commands import CheckFailure


class NoPoolFound(CheckFailure):
    """No pool found."""

    def __init__(self, pool: str):
        """Init."""
        message = f"{pool} pool not found. Please choose one from the autocomplete."
        super().__init__(pool, message)
        self.message = message
