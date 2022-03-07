# coding=utf-8
# pylint: disable=invalid-name
import json
import logging
import os
from logging.handlers import RotatingFileHandler

import discord
from discord.ext import commands


# noinspection PyBroadException
def main():  # pylint: disable=too-many-statements
    """Main"""
    if os.name != "nt":
        import uvloop  # pylint: disable=import-outside-toplevel
        uvloop.install()

    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(filename='Char2.log', encoding='utf-8', mode='w', maxBytes=2000000, backupCount=10)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    bot = commands.Bot(command_prefix="c?", owner_ids=[225344348903047168, 363095569515806722],
                       case_insensitive=True, intents=discord.Intents.all(), help_command=None)

    async def on_connect():
        print("Logged In!")

    bot.load_extension('jishaku')
    bot.load_extension('.primary', package='char2ext')
    bot.on_connect = on_connect
    with open('token2.json', encoding='utf8') as file:
        bot.run(json.load(file)['token'])


if __name__ == "__main__":
    main()
