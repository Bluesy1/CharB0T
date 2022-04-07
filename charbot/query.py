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
import os
import time

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Cog, Context

__source__ = (
    "You can find my source code here: https://www.github.com/Bluesy1/CharB0T/charbot \n"
    "I'm liscensed under the MIT liscense. See the license file for more information: "
    "https://www.github.com/Bluesy1/CharB0T/blob/master/LICENSE \n Creator: Bluesy#8150"
)


class Query(Cog):
    """Query cog"""

    # noinspection PyUnresolvedReferences
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        """Check to run for all cog commands"""
        if ctx.guild is None:
            return False
        return not any(
            role.id in (684936661745795088, 676250179929636886)
            for role in ctx.author.roles  # type: ignore
        ) or any(
            role.id in (338173415527677954, 253752685357039617, 225413350874546176)
            for role in ctx.author.roles  # type: ignore
        )

    @commands.command()
    async def time(self, ctx: Context):
        """Returns eastern time"""
        os.environ["TZ"] = "US/Eastern"
        time.tzset()
        await ctx.send(
            "Charlie's time is: " + time.strftime("%X %x %Z"), reference=ctx.message
        )

    @commands.command()
    async def source(self, ctx: Context):
        """Returns a reference to the source code for the bot and its liscense

        References
        ----------
        Repository:
        https://github.com/Bluesy1/CharB0T/charbot

        Licence:
        MIT - https://github.com/Bluesy1/CharB0T/blob/master/LICENSE

        Parameters
        ----------
        ctx: discord.ext.commands.Context
            The context of the command
        """
        await ctx.reply(__source__)

    @app_commands.command(
        name="source",
        description="Returns a reference to the source code for the bot and its liscense",
    )
    async def app_source(self, interaction: discord.Interaction):
        """Returns a reference to the source code for the bot and its liscense

        References
        ----------
        Repository:
        https://www.github.com/Bluesy1/CharB0T/charbot

        Licence:
        MIT - https://www.github.com/Bluesy1/CharB0T/blob/master/LICENSE

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction of the command
        """
        await interaction.response.send_message(__source__)


async def setup(bot: commands.Bot):
    """Loads Plugin"""
    await bot.add_cog(
        Query(bot), override=True, guild=discord.Object(id=225345178955808768)
    )
