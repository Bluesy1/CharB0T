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
import logging
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from logging.handlers import RotatingFileHandler

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv


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

    async def setup_hook(self):
        """Initialize hook for the bot.

        This is called when the bot is logged in but before connecting to the websocket.
        It provides an opportunity to perform some initialisation before the websocket is connected.
        Also loads the cogs, and prints who the bot is logged in as

        Parameters
        ----------
        self : CBot
            The CBot instance.
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
    async with bot:  # skipcq: PYL-PYL-E1701
        with ThreadPoolExecutor(max_workers=25) as executor, ProcessPoolExecutor(max_workers=5) as process_pool:
            bot.executor = executor
            bot.process_pool = process_pool
            await bot.start(os.getenv("TOKEN"))  # type: ignore


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()

    asyncio.run(main())
