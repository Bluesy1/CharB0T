# coding=utf-8
import json
import logging
import os
from logging.handlers import RotatingFileHandler

import discord
from discord.ext import commands


# noinspection PyBroadException
def main():
    """Main"""
    if os.name != "nt":
        import uvloop

        uvloop.install()

    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        filename="UBCO.log",
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
    bot = commands.Bot(
        command_prefix=";",
        owner_id=363095569515806722,
        case_insensitive=True,
        intents=discord.Intents.all(),
        help_command=None,
    )

    async def on_connect():
        print("Logged In!")

    bot.load_extension("jishaku")
    bot.load_extension(".admin", package="ubcoext")
    bot.on_connect = on_connect
    with open("UBCbot.json", encoding="utf8") as file:
        bot.run(json.load(file)["Token"])


if __name__ == "__main__":
    main()
