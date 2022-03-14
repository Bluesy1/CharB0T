# coding=utf-8
import logging
import os
from logging.handlers import RotatingFileHandler

import discord
from discord.ext import commands
from dotenv import load_dotenv


class C2Bot(commands.Bot):
    """Custom bot class. extends discord.ext.commands.Bot"""

    async def setup_hook(self):
        """Setup hook"""
        print("Setup started")
        await self.load_extension("jishaku")
        await self.load_extension("primary")
        print("Extensions loaded")
        print(f"Logged in as {self.user.name}#{self.user.discriminator}")


# noinspection PyBroadException
def main():
    """Main"""
    if os.name != "nt":
        import uvloop

        uvloop.install()

    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        filename="../Char2.log",
        encoding="utf-8",
        mode="w",
        maxBytes=2000000,
        backupCount=10,
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)

    bot = C2Bot(
        command_prefix="c?",
        owner_ids=[225344348903047168, 363095569515806722],
        case_insensitive=True,
        intents=discord.Intents.all(),
        help_command=None,
    )

    async def on_connect():
        """Function called on bot connect"""
        print("Logged In!")

    bot.on_connect = on_connect
    load_dotenv()
    bot.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()
