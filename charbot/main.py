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
import logging
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from logging.handlers import RotatingFileHandler

import asyncpg
import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot import CBot, Tree


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
        tree_cls=Tree,
        command_prefix=commands.when_mentioned_or("!"),
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
            token = os.getenv("TOKEN")
            assert isinstance(token, str)  # skipcq: BAN-B101
            await bot.start(token)


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()

    asyncio.run(main())
