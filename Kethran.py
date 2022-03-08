# coding=utf-8
# pylint: disable=invalid-name
import json
import logging
import os
from logging.handlers import RotatingFileHandler

import discord
from discord.ext import commands


# noinspection PyBroadException
def main():  # pylint: disable = too-many-statements
    """Main"""
    if os.name != "nt":
        import uvloop  # pylint: disable=import-outside-toplevel
        uvloop.install()

    logger = logging.getLogger('discord')
    logger.setLevel(logging.WARNING)
    handler = RotatingFileHandler(filename='kethran.log', encoding='utf-8', mode='w', maxBytes=2000000, backupCount=10)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    bot = commands.Bot(command_prefix="k", owner_id=363095569515806722, case_insensitive=True, help_command=None,
                       intents=discord.Intents.message_content)

    async def on_connect():
        print("Logged In!")

    friday_5.start()
    bot.on_connect = on_connect
    bot.load_extension('jishaku')
    with open("KethranToken.json", encoding='utf8') as file:
        bot.run(json.load(file)['Token'])


if __name__ == "__main__":
    main()
