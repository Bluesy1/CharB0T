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
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from logging.handlers import RotatingFileHandler

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv


class CBot(commands.Bot):
    """Custom bot class. extends discord.ext.commands.Bot"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executor = ThreadPoolExecutor(max_workers=25)

    async def setup_hook(self):
        """Setup hook"""
        print("Setup started")
        await self.load_extension("jishaku")
        await self.load_extension("admin")
        await self.load_extension("dice")
        await self.load_extension("events")
        await self.load_extension("gcal")
        await self.load_extension("mod_support")
        await self.load_extension("query")
        print("Extensions loaded")
        print(f"Logged in: {self.user.name}#{self.user.discriminator}")  # type: ignore


# noinspection PyBroadException
async def main():
    """Main"""
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        filename="../CharBot.log",
        encoding="utf-8",
        mode="w",
        maxBytes=2000000,
        backupCount=10,
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)
    # Instantiate a Bot instance
    bot = CBot(
        command_prefix="!",
        owner_ids=[225344348903047168, 363095569515806722],
        case_insensitive=True,
        intents=discord.Intents.all(),
        help_command=None,
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="over the server"
        ),
    )

    load_dotenv()
    async with bot:
        with ThreadPoolExecutor(max_workers=25) as executor:
            bot.executor = executor
            await bot.start(os.getenv("TOKEN"))  # type: ignore


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()

    asyncio.run(main())
