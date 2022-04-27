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
"""Charbot discord bot."""
import asyncio
import datetime
import logging
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from logging.handlers import RotatingFileHandler
from zoneinfo import ZoneInfo

import asyncpg

import discord
from discord.ext import commands
from dotenv import load_dotenv


__ZONEINFO__ = ZoneInfo("America/Detroit")
__TIME__ = lambda: datetime.datetime.now(__ZONEINFO__).replace(microsecond=0, second=0, minute=0, hour=0)  # noqa: E731


class CBot(commands.Bot):
    """Custom bot class. extends discord.ext.commands.Bot.

    This class is used to create the bot instance.

    Attributes
    ----------
    executor : ThreadPoolExecutor
        The executor used to run IO tasks in the background, must be set after opening bot in an async manager,
         before connecting to the websocket.
    process_pool : ProcessPoolExecutor
        The executor used to run CPU tasks in the background, must be set after opening bot in an async manager,
         before connecting to the websocket.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executor: ThreadPoolExecutor = ...  # type: ignore
        self.process_pool: ProcessPoolExecutor = ...  # type: ignore
        self.pool: asyncpg.Pool = ...  # type: ignore

    async def setup_hook(self):
        """Initialize hook for the bot.

        This is called when the bot is logged in but before connecting to the websocket.
        It provides an opportunity to perform some initialisation before the websocket is connected.
        Also loads the cogs, and prints who the bot is logged in as
        """
        print("Setup started")
        await self.load_extension("jishaku")
        await self.load_extension("admin")
        await self.load_extension("dice")
        await self.load_extension("events")
        await self.load_extension("gcal")
        await self.load_extension("mod_support")
        await self.load_extension("primary")
        await self.load_extension("query")
        await self.load_extension("shrugman")
        await self.load_extension("sudoku")
        print("Extensions loaded")
        print(f"Logged in: {self.user.name}#{self.user.discriminator}")  # type: ignore

    async def giveaway_user(self, user: int) -> None | asyncpg.Record:
        """Return an asyncpg entry for the user, joined on all 3 tables for tthe giveaway.

        Parameters
        ----------
        user : int
            The user id.

        Returns
        -------
        asyncpg.Record, optional
            The user record, or None if the user isn't in the DB.
        """
        return await self.pool.fetchrow(
            "SELECT users.id as id, points, b.bid as bid, dp.last_claim as daily, dp.last_particip_dt as "
            "particip_dt, dp.particip as particip, dp.won as won "
            "FROM users join bids b on users.id = b.id join daily_points dp on users.id = dp.id WHERE users.id = $1",
            user,
        )

    async def give_game_points(self, user_id: int, points: int, bonus: int = 0) -> int:
        """Give the user points.

        Parameters
        ----------
        user_id : int
            The user id.
        points : int
            The amount of points to give.
        bonus : int, optional
            The amount of points to add to the user's total points.

        Returns
        -------
        int
            The points gained
        """
        user = await self.giveaway_user(user_id)
        if user is None:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO users (id, points) VALUES ($1, $2)",
                    user_id,
                    points + bonus,
                )
                await conn.execute("INSERT INTO bids (id, bid) VALUES ($1, 0)", user_id)
                await conn.execute(
                    "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won)"
                    " VALUES ($1, $2, $3, $4, $5)",
                    user_id,
                    __TIME__() - datetime.timedelta(days=1),
                    __TIME__(),
                    points,
                    bonus,
                )
                return points + bonus
        else:
            if user["particip_dt"] < __TIME__():
                async with self.pool.acquire() as conn:
                    await conn.execute(
                        "UPDATE daily_points SET last_particip_dt = $1, particip = $2, won = $3 WHERE id = $4",
                        __TIME__(),
                        points,
                        bonus,
                        user_id,
                    )
                    await conn.execute("UPDATE users SET points = points + $1 WHERE id = $2", points + bonus, user_id)
            if user["particip_dt"] == __TIME__():
                if user["particip"] + points > 10:
                    pass
                else:
                    async with self.pool.acquire() as conn:
                        await conn.execute(
                            "UPDATE daily_points SET particip = $1, won = $2 WHERE id = $3",
                            points,
                            bonus,
                            user_id,
                        )
                        await conn.execute(
                            "UPDATE users SET points = points + $1 WHERE id = $2", points + bonus, user_id
                        )
        return points + bonus


class NoGiveawayRole(commands.CommandError):
    """Exception raised when a user has no role for the giveaway but attempts to interact with the system.

    Inherits from :class:`discord.ext.commands.CommandError`.

    Parameters
    ----------
    message : str
        The error message.
    """

    def __init__(self, message: str = "No giveaway allowed role found"):
        self.message = message
        super().__init__(message)

    def __str__(self):
        """Return the error message."""
        return f"An authentication error occurred: {self.message}"


def check_giveaway(roles: list[discord.Role]) -> bool:
    """Check if the user has a role for the giveaway.

    Parameters
    ----------
    roles : list[discord.Role]
        The roles of the user.

    Returns
    -------
    bool
        True if the user has a role for the giveaway, False otherwise.
    """
    allowed_roles = [928481483742670971, 337743478190637077, 685331877057658888]
    if not any(role.id in allowed_roles for role in roles):
        return True
    return True


# skipcq: FLK-D202
def giveaway_command_check():
    """Command Decorator to check if a user is allowed to participate in a giveaway.

    Returns
    -------
    function
        The wrapped function.

    Raises
    ------
    NoGiveawayRole
        If the user has no role for the giveaway, or isued in a dm
    """

    async def predicate(ctx: commands.Context) -> bool:
        """Check if the user is allowed to participate in a giveaway.

        Parameters
        ----------
        ctx : commands.Context
            The context of the command.

        Returns
        -------
        bool
            True if the user is allowed to participate in a giveaway, False otherwise.
        """
        if ctx.guild is None:
            raise NoGiveawayRole("This command can only be used in a server")
        if check_giveaway(ctx.author.roles):  # type: ignore
            return True
        raise NoGiveawayRole("You must be at least level 5 to participate in the giveaways system.")

    return commands.check(predicate)


# noinspection PyBroadException
async def main():
    """Run charbot."""
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        filename="../CharBot.log",
        encoding="utf-8",
        mode="w",
        maxBytes=2000000,
        backupCount=10,
    )
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    logger.addHandler(handler)
    # Instantiate a Bot instance
    bot = CBot(
        command_prefix="!",
        owner_ids=[225344348903047168, 363095569515806722],
        case_insensitive=True,
        intents=discord.Intents.all(),
        help_command=None,
        activity=discord.Activity(type=discord.ActivityType.watching, name="over the server"),
    )

    load_dotenv()
    async with bot, asyncpg.create_pool(  # skipcq: PYL-E1701
        min_size=50,
        max_size=100,
        **{
            "host": os.getenv("HOST"),
            "user": os.getenv("DBUSER"),
            "password": os.getenv("PASSWORD"),
            "database": os.getenv("DATABASE"),
        },
    ) as pool:
        with ThreadPoolExecutor(max_workers=25) as executor, ProcessPoolExecutor(max_workers=5) as process_pool:
            bot.executor = executor
            bot.process_pool = process_pool
            bot.pool = pool
            await bot.start(os.getenv("TOKEN"))  # type: ignore


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()

    asyncio.run(main())
