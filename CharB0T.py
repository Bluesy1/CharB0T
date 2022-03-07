# coding=utf-8
# pylint: disable=invalid-name
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
        import uvloop  # pylint: disable=import-outside-toplevel
        uvloop.install()

    with open('bottoken.json', encoding='utf8') as file:
        token = json.load(file)['Token']
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(filename='CharBot.log', encoding='utf-8', mode='w', maxBytes=2000000, backupCount=10)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    # Instantiate a Bot instance
    bot = commands.Bot(command_prefix="!", owner_ids=[225344348903047168, 363095569515806722],
                       case_insensitive=True, intents=discord.Intents.all(), help_command=None,
                       activity=discord.Activity(type=discord.ActivityType.watching, name="over the server"))

    @commands.command
    async def ping(ctx):  # pylint: disable=unused-variable
        """Ping Command TO Check Bot Is Alive"""
        await ctx.event.message.delete()
        await ctx.respond(f"Pong! Latency: {bot.latency * 1000:.2f}ms")

    bot.load_extension('jishaku')
    bot.run(token)


if __name__ == "__main__":
    main()
