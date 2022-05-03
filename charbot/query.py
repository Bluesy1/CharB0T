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
"""Query extension."""
import os
import time

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Cog, Context

__source__ = (
    "You can find my source code here: https://github.com/Bluesy1/CharB0T/tree/main/charbot \n"
    "I'm liscensed under the MIT liscense. See the license file for more information: "
    "https://www.github.com/Bluesy1/CharB0T/blob/master/LICENSE \n Creator: Bluesy#8150"
)


class Query(Cog):
    """Query cog.

    Parameters
    ----------
    bot : Bot
        The bot object to bind the cog to.

    Attributes
    ----------
    bot : Bot
        The bot object the cog is attached to.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        """Check to run for all cog commands.

        Parameters
        ----------
        ctx : Context
            The context of the command.

        Returns
        -------
        bool
            True if the user has the required permissions to use the cog.
        """
        if ctx.guild is None:
            return False
        return not any(
            role.id in (684936661745795088, 676250179929636886) for role in ctx.author.roles  # type: ignore
        ) or any(
            role.id in (338173415527677954, 253752685357039617, 225413350874546176)
            for role in ctx.author.roles  # type: ignore
        )

    @commands.command()
    async def time(self, ctx: Context):
        """Return eastern time.

        Parameters
        ----------
        ctx : Context
            The context of the command.
        """
        os.environ["TZ"] = "US/Eastern"
        time.tzset()
        await ctx.send("Charlie's time is: " + time.strftime("%X %x %Z"), reference=ctx.message)

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def objection(self, ctx: Context):
        """Return the objection.

        Parameters
        ----------
        ctx : Context
            The context of the command.
        """
        await ctx.send("Objection! Hearsay.")
        await ctx.message.delete()

    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.channel)
    async def faq(self, ctx: commands.Context):
        """Return the FAQ.

        Parameters
        ----------
        ctx : Context
            The context of the command.
        """
        await ctx.reply(
            "**Frequently Asked Questions**\n\n"
            "**Q:** What is the purpose of this bot?\n"
            "**A:** This bot is a tool for the Charlie's discord server. It is used to "
            "provide custom tools and communication for the server.\n\n"
            "**Q:** How do I use this bot?\n"
            "**A:** You can use the bot by using the prefix `!` and the command name, or slash commands. \n\n"
            "**Q:** How do I get the bot?\n"
            "**A:** You can get the bot's source from the source command.\n\n"
            "**Q:** Why are so many things locked behind level 5?\n"
            "**A:** This is to prevent people from abusing the bot, and Charlie's generousity.\n\n"
            "**Q:** What level am I?\n"
            "**A:** You can check your level by using the `rank` command.\n\n"
            "**Q:** How much reputation can I earn from games every day?\n"
            "**A:** You are limited globall across all games to an undisclosed amount.\n\n"
            "**Q:** How do I get more reputation?\n"
            "**A:** You can earn more reputation by playing games or the `rollcall` command.\n\n"
            "**Q:** How much rep do i have?\n"
            "**A:** You can check your reputation by using the `reputation` command.\n\n"
        )

    @commands.hybrid_command(name="source", description="Info about the source code")
    @app_commands.guilds(225345178955808768)
    async def source(self, ctx: Context):
        """Return a reference to the source code for the bot and its liscense.

        References
        ----------
        Repository:
        https://github.com/Bluesy1/CharB0T/tree/main/charbot

        Licence:
        MIT - https://github.com/Bluesy1/CharB0T/blob/master/LICENSE

        Parameters
        ----------
        ctx: discord.ext.commands.Context
            The context of the command
        """
        await ctx.reply(__source__)

    @commands.hybrid_command(name="imgscam", description="Info about the semi fake image scam on discord")
    @app_commands.guilds(225345178955808768)
    async def imgscam(self, ctx: Context):
        """Send the image scam info url.

        Parameters
        ----------
        ctx: discord.ext.commands.Context
            The context of the command
        """
        await ctx.reply("https://blog.hyperphish.com/articles/001-loading/")


async def setup(bot: commands.Bot):
    """Load Plugin.

    Parameters
    ----------
    bot : commands.Bot
        The bot object to bind the cog to.
    """
    await bot.add_cog(Query(bot), override=True, guild=discord.Object(id=225345178955808768))
