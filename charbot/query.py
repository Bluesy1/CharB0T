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
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
import pytesseract
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Cog, Context
from PIL import Image


__source__ = "<https://github.com/Bluesy1/CharB0T/tree/main/charbot>"


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
        author = ctx.author
        assert isinstance(author, discord.Member)  # skipcq: BAN-B101
        return not any(role.id in (684936661745795088, 676250179929636886) for role in author.roles) or any(
            role.id in (338173415527677954, 253752685357039617, 225413350874546176) for role in author.roles
        )

    @commands.command()
    async def time(self, ctx: Context):
        """Return eastern time.

        Parameters
        ----------
        ctx : Context
            The context of the command.
        """
        await ctx.reply(f"Charlie's time is: {datetime.now(ZoneInfo('America/Detroit')).strftime('%X %x %Z')}")

    @commands.command()
    async def changelog(self, ctx: Context):
        """Return the changelog.

        Parameters
        ----------
        ctx : Context
            The context of the command.
        """
        await ctx.reply("Here's the changelog: https://bluesy1.github.io/CharB0T/changes")

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
            "**Read the FAQ and the following channels before asking questions:**\n"
            "**<#244635060144308224>, <#970138004947611710>, <#398949472840712192>, <#343806259319013378>**\n"
            "**Q:** What is the purpose of this bot?\n"
            "**A:** This bot is a tool for the Charlie's discord server. It is used to "
            "provide custom tools and communication for the server.\n\n"
            "**Q:** How do I use this bot?\n"
            "**A:** You can use the bot by using the prefix `!` and the command name, or slash commands. \n\n"
        )

    @commands.hybrid_command(name="source", description="Info about the source code")
    @app_commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.channel)
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
        await ctx.reply(f"https://bluesy1.github.io/CharB0T/\n{__source__}\nMIT License")

    @commands.command(aliaes=["ocr"])
    async def pull_text(self, ctx: Context, image: discord.Attachment | None = None):
        """Pull the test out of an image using Optical Character Recognition.

        Parameters
        ----------
        ctx : Context
            The context of the command.
        image : discord.Attachment | None
            The image to pull text from.
        """
        try:
            langs = pytesseract.get_languages()
        except pytesseract.TesseractNotFoundError:
            await ctx.reply("Tesseract is not installed, I cannot read images.")
            __import__("logging").getLogger("charbot.query").error("Tesseract is not installed, I cannot read images.")
            return
        else:
            if "eng" not in langs:
                await ctx.reply("Tesseract does not have English installed, I cannot read images.")
                return
        async with ctx.typing():
            if image is None:
                if ref := ctx.message.reference:
                    attachments = ref.resolved.attachments
                    if len(attachments) == 1:
                        att = attachments[0]
                        res: str = await asyncio.to_thread(
                            lambda img: pytesseract.image_to_string(
                                Image.frombytes("RGBA", (att.width, att.height), img)
                            ),
                            att.read(),
                        )
                    else:
                        await ctx.reply("Please provide an image or reply to a message with an image.")
                        return
                else:
                    await ctx.reply("Please provide an image or reply to a message with an image.")
                    return
            else:
                res: str = await asyncio.to_thread(
                    lambda img: pytesseract.image_to_string(Image.frombytes("RGBA", (image.width, image.height), img)),
                    await image.read(),
                )
            await ctx.reply(f"```\n{res}\n```")

    # skipcq: PYL-W0105
    """@commands.hybrid_command(name="imgscam", description="Info about the semi fake image scam on discord")
    async def imgscam(self, ctx: Context):
        \"""Send the image scam info url.

        Parameters
        ----------
        ctx: discord.ext.commands.Context
            The context of the command
        \"""
        await ctx.reply("https://blog.hyperphish.com/articles/001-loading/")
    """


async def setup(bot: commands.Bot):
    """Load Plugin.

    Parameters
    ----------
    bot : commands.Bot
        The bot object to bind the cog to.
    """
    await bot.add_cog(Query(bot), override=True)
