# -*- coding: utf-8 -*-
import datetime
from collections.abc import Callable, Coroutine
from typing import Any, ClassVar
from zoneinfo import ZoneInfo

import aiohttp
import asyncpg
from discord import app_commands, Member, User, Webhook
from discord.ext import commands
from fluent.runtime import FluentResourceLoader


class CBot(commands.Bot):
    """Charbot Class."""

    ZONEINFO: ClassVar[ZoneInfo]
    ALLOWED_ROLES: ClassVar[list[int | str]]
    CHANNEL_ID: ClassVar[int]
    TIME: Callable[[], datetime.datetime]
    __init__: Callable[[tuple[Any, ...], bool, type["Tree"], dict[str, Any]], None]
    session: aiohttp.ClientSession
    pool: asyncpg.Pool
    program_logs: Webhook
    setup_hook: Callable[[], Coroutine[None, None, None]]
    giveaway_user: Callable[[int], Coroutine[None, None, None | asyncpg.Record]]
    localize_loader: FluentResourceLoader

    async def give_game_points(self, member: Member | User, game: str, points: int, bonus: int = 0) -> int:
        """Give points to a member for a game."""
        ...


class Tree(app_commands.CommandTree[CBot]):
    """Tree Class."""

    ...
