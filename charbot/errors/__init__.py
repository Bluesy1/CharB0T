"""Custom errors for the bot."""

__all__ = ("WrongChannelError", "MissingProgramRole")

from .channel import WrongChannelError
from .roles import MissingProgramRole
