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
"""Primary functions for the Kethran Bot."""
import datetime
import random
import sys

import discord
import pytz
from discord.ext import commands, tasks
from discord.ext.commands import Cog
from discord.utils import utcnow


sys.path.append("..")
from helpers import roller  # skipcq: FLK-E402  # noqa: E402


class Primary(Cog):
    """Kethran's Primary Functions.

    This is the primary functions that Kethran uses.
    It has the following functions:
    - Dice Roller
    - Automated message every friday at 5:00pm Pacific Time

    Parameters
    ----------
    bot: commands.Bot
        The bot that the cog is attached to

    Attributes
    ----------
    bot: commands.Bot
        The bot that the cog is attached to
    responses: list[str]
        A list of responses that Kethran uses
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.responses = [
            "Bork!",
            "Bork!",
            "Bork!",
            "Bork!",
            "Bork!",
            "WOOF!",
            "WOOF!",
            "WOOF!",
            "WOOF!",
            "AROOOF!",
            "AROOOF!",
            "AROOOF!",
            "AROOOF!",
            "HOOOWL!",
            "HOOOWL!",
            "HOOOWL!",
            "HOOOWL!",
            "HOOOWL!",
            "Aroof",
            "Aroof",
            "Aroof",
            "Aroof",
            "*Sniff Sniff Sniff*",
            "*Sniff Sniff Sniff*",
            "*Sniff Sniff Sniff*",
            "*Sniff Sniff Sniff*",
            "*Does not care*",
            "*Does not care*",
            "*Does not care*",
            "*Does not care*",
            "*I want scritches*",
            "*I want scritches*",
            "*I want scritches*",
            "*I want scritches*",
            "*I want scritches*",
            "*is busy*",
            "*is busy*",
            "*is busy*",
            "*is busy*",
            "snuffles",
            "snuffles",
            "snuffles",
            "snuffles",
            "snuffles apologetically",
            "snuffles apologetically",
            "snuffles apologetically",
            "snuffles apologetically",
            "sits",
            "sits",
            "sits",
            "sits",
            "lays down",
            "lays down",
            "lays down",
            "lays down",
            "chuffs",
            "chuffs",
            "chuffs",
            "chuffs",
            "pants",
            "pants",
            "pants",
            "pants",
            "plays dead",
            "plays dead",
            "plays dead",
            "plays dead",
            "gives paw",
            " gives paw",
            "gives paw",
            "gives paw",
            "rolls over",
            "rolls over",
            "rolls over",
            "rolls over",
            "is adorable",
            "is adorable",
            "is adorable",
            "is adorable",
            "plops head on lap",
            "whimpers",
            "whimpers",
            "whimpers",
            "licks face",
            "licks face",
            "licks face",
            "licks face",
            "*Sits*",
            "*Sits*",
            "*Sits*",
            "*Sits*",
            "*is adorable*",
            "*is adorable*",
            "*is adorable*",
            "*is adorable*",
            "pants",
            "pants",
            "pants",
            "pants",
            "**HOLY SHIT!** \n**HOLY SHIT!**\n**HOLY SHIT!**",
        ]

    async def cog_load(self) -> None:
        """Start the automated message every friday at 5:00pm Pacific Time.

        Parameters
        ----------
        self: Primary
            An instance of the Primary class
        """
        pass
        # self.friday_5.start()

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Cancel the automated message every friday at 5:00pm Pacific Time.

        Parameters
        ----------
        self: Primary
            An instance of the Primary class
        """
        pass
        # self.friday_5.cancel()

    @tasks.loop(  # skipcq: PYL-E1123
        time=datetime.time(
            hour=17,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=pytz.timezone("US/Pacific"),
        )
    )
    async def friday_5(self) -> None:
        """Automated message every friday at 5:00pm Pacific Time.

        Parameters
        ----------
        self: Primary
            An instance of the Primary class
        """
        if utcnow().date().weekday() == 5:
            channel = await self.bot.fetch_channel(878434694713188362)
            assert isinstance(channel, discord.TextChannel)  # skipcq: BAN-B101
            await channel.send(random.choice(self.responses))

    @Cog.listener()
    async def on_message(self, message: discord.Message):
        """Check for the word kethran being in a message and respond accordingly.

        Responds with a random response if in the correct channels.
        If the message is a dm and from a specific user
        the bot will forward the message to a specific channel.

        Parameters
        ----------
        self: Primary
            An instance of the Primary class
        message: discord.Message
            The message that was sent
        """
        if not message.author.bot and message.channel.type is not discord.ChannelType.private:
            if message.channel.id in [901325983838244865, 878434694713188362] and "kethran" in message.content.lower():
                await message.channel.send(
                    random.choice(self.responses),
                    reference=message,
                    mention_author=True,
                )
        elif message.author.id == 184524255197659136:
            channel = await self.bot.fetch_channel(878434694713188362)
            assert isinstance(channel, discord.TextChannel)  # skipcq: BAN-B101
            await channel.send(message.content)

    @commands.command()
    async def roll(self, ctx: commands.Context, *, arg: str):
        """Command to roll a dice.

        Parameters
        ----------
        self: Primary
            An instance of the Primary class
        ctx: commands.Context
            The context of the command
        arg: str
            The dice to roll
        """
        await ctx.send(f"Kethran {roller.roll(arg)}", reference=ctx.message)


async def setup(bot: commands.Bot):
    """Load the Primary cog into the bot.

    Parameters
    ----------
    bot: commands.Bot
        The bot to load the cog into
    """
    await bot.add_cog(Primary(bot))
