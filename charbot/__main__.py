"""Charbot discord bot."""

import asyncio
import logging.config
import os

import asyncpg
import discord
import sentry_sdk
from discord.ext import commands

from . import CBot, Config, Tree


async def main():
    """Run charbot."""
    # set up logging because i'm using `client.start()`, not `client.run()`
    # so I don't get the sane logging defaults set by discord.py
    logging.config.dictConfig(Config["logging"])  # skipcq: PY-A6006

    # Setup sentry.io integration so that exceptions are logged to sentry.io as well.
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
    async with (
        CBot(  # skipcq: PYL-E1701
            tree_cls=Tree,
            command_prefix=commands.when_mentioned_or("!"),
            owner_ids=[225344348903047168, 363095569515806722],
            case_insensitive=True,
            intents=discord.Intents.all(),
            help_command=None,
            activity=discord.Activity(type=discord.ActivityType.watching, name="over the server"),
        ) as bot,
        asyncpg.create_pool(
            min_size=50,
            max_size=100,
            host=Config["postgres"]["host"],
            user=Config["postgres"]["user"],
            password=Config["postgres"]["password"],
            database=Config["postgres"]["database"],
        ) as pool,
    ):
        bot.pool = pool
        await bot.start(Config["discord"]["token"])


if __name__ == "__main__":
    print("Starting charbot...")
    if os.name != "nt":
        import uvloop

        print("Using uvloop")

        uvloop.run(main())
    else:
        asyncio.run(main())
