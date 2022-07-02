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
import logging.config
import os
import socket
import uuid

import aiohttp
import asyncpg
import discord
import sentry_sdk
from discord.ext import commands

from . import CBot, Config, Tree


# noinspection PyBroadException
async def main():
    """Run charbot."""
    # set up logging because i'm using `client.start()`, not `client.run()`
    # so i don't get the sane loging defaults set by discord.py
    logging.config.dictConfig(Config["logging"])  # skpicq: PY-A6006

    # Setup sentry.io integration so that exceptions are logged to sentry.io as well.
    sentry_sdk.set_user({"id": uuid.uuid4(), "ip_address": "{{ auto }}", "username": socket.gethostname()})
    sentry_sdk.init(
        dsn=Config["sentry"]["dsn"],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        environment=Config["sentry"]["environment"],
        release=Config["sentry"]["release"],
        send_default_pii=True,
        attach_stacktrace=True,
        in_app_include=[
            "charbot",
            "minesweeper",
            "shrugman",
            "sudoku",
            "tictactoe",
        ],
    )

    # Instantiate a Bot instance
    async with CBot(  # skipcq: PYL-E1701
        tree_cls=Tree,
        command_prefix=commands.when_mentioned_or("!"),
        owner_ids=[225344348903047168, 363095569515806722],
        case_insensitive=True,
        intents=discord.Intents.all(),
        help_command=None,
        activity=discord.Activity(type=discord.ActivityType.watching, name="over the server"),
    ) as bot, asyncpg.create_pool(
        min_size=50,
        max_size=100,
        host=Config["postgres"]["host"],
        user=Config["postgres"]["user"],
        password=Config["postgres"]["password"],
        database=Config["postgres"]["database"],
    ) as pool, aiohttp.ClientSession() as session:
        bot.pool = pool
        bot.session = session
        await bot.start(Config["discord"]["token"])


if __name__ == "__main__":
    print("Starting charbot...")
    if os.name != "nt":
        import uvloop

        uvloop.install()

        print("Installed uvloop")

    asyncio.run(main())
