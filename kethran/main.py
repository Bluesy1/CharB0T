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
"""Kethran main module."""
import logging
import os
from logging.handlers import RotatingFileHandler

import discord
from discord.ext import commands
from dotenv import load_dotenv


class Kethran(commands.Bot):
    """Custom bot class. extends discord.ext.commands.Bot."""

    async def setup_hook(self):
        """Load all the extensions and tells us the name and discriminator of the bot."""
        print("Setup started")
        await self.load_extension("jishaku")
        await self.load_extension("primary")
        print("Extensions loaded")
        user = self.user
        assert isinstance(user, discord.ClientUser)  # skipcq: BAN-B101
        print(f"Logged in:{user.name}#{user.discriminator}")


# noinspection PyBroadException
def main():
    """Run Kethran.

    This function instantiates the bot and runs it.
    """
    if os.name != "nt":
        import uvloop

        uvloop.install()

    logger = logging.getLogger("discord")
    logger.setLevel(logging.WARNING)
    handler = RotatingFileHandler(
        filename="kethran.log",
        encoding="utf-8",
        mode="w",
        maxBytes=2000000,
        backupCount=10,
    )
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    logger.addHandler(handler)
    bot = Kethran(
        command_prefix="k",
        owner_id=363095569515806722,
        case_insensitive=True,
        help_command=None,
        intents=discord.Intents.all(),
    )

    load_dotenv()
    bot.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()
