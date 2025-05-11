import datetime
from collections.abc import Callable, Coroutine
from typing import Any, ClassVar
from zoneinfo import ZoneInfo

import asyncpg
from discord import Member, User, Webhook, app_commands
from discord.ext import commands


class CBot(commands.Bot):
    """Charbot Class."""

    ZONEINFO: ClassVar[ZoneInfo]
    CHANNEL_ID: ClassVar[int]
    TIME: Callable[[], datetime.datetime]
    __init__: Callable[[tuple[Any, ...], bool, type["Tree"], dict[str, Any]], None]
    pool: asyncpg.Pool
    program_logs: Webhook
    setup_hook: Callable[..., Coroutine[None, None, None]]

    async def give_game_points(self, member: Member | User, game: str, points: int, bonus: int = 0) -> int:
        """Give points to a member for a game."""
        ...


class Tree(app_commands.CommandTree[CBot]):
    """Tree Class."""

    ...
