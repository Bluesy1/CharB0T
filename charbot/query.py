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
import re
from io import BytesIO
from datetime import datetime
from typing import cast, TYPE_CHECKING, Final
from zoneinfo import ZoneInfo

import discord
import pytesseract
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Cog, Context
from PIL import Image, ImageOps


if TYPE_CHECKING:
    from . import CBot, GuildInteraction as Interaction


__rules__: Final[dict[int, str]] = {
    1: "Be respectful to others. Being drunk is not an excuse for being stupid. Common-sense matters."
    " Just because it isn’t explicitly written here, doesn’t mean it doesn’t break the rules.",
    2: "Please utilize the text and voice channels as they are described and keep things on topic."
    " Please be open to explaining and including others for any conversation you have here.",
    3: "Don't spam. Intentionally spamming gets you kicked or muted. Whether or not you are spamming is subject to"
    " interpretation of the moderator team. I will side with their judgment.",
    4: "Please do NOT use this as a venue for asking me when new videos will be released. "
    "I release stuff as fast as my schedule allows. See <#922613000047824956> for the breakdown",
    5: "In voice channels, please be courteous and do not hog the mic, scream, play background music, or "
    "other annoying things.",
    6: "Please no backseat gaming (we get enough of it on YouTube comments), and don't throw out spoilers to current"
    " things I or another person is working on.",
    7: "Feel free to use pictures in the chats, but nothing too crude, and nothing X rated. Insta-ban for anyone "
    "posting pornography, etc.",
    8: "Discord invites and promotions of your own content anywhere but <#298485559813210115> are restricted, "
    "if you wish to post one somewhere please check with Mods",
    9: "Please respect the Mods here. They are good people who sincerely want this environment to be awesome too. "
    "If they’re advising you to change your behavior, it’s the same as me doing it. Please listen.",
    10: "Some language will be deleted. I like the idea of maintaining a PG-13 community environment. "
    "Find a way to say it another way, if the bot kills your message.",
}
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
    def __init__(self, bot: "CBot"):
        self.ocr_done: set[int] = set()
        self.bot = bot

    async def cog_load(self) -> None:
        """Load the cog."""
        self.ocr_done = self.bot.holder.get("ocr_done", self.ocr_done)
        self.clear_ocr_done.start()

    async def cog_unload(self) -> None:
        """Unload the cog."""
        self.bot.holder["ocr_done"] = self.ocr_done
        self.clear_ocr_done.cancel()

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

    @staticmethod
    def get_text(image: BytesIO) -> str:
        """Get the text from an image using pytesseract"""
        img = Image.open(image)
        if img.is_animated:
            img.seek(0)
            buf = BytesIO()
            img.save(buf, format="PNG", save_all=False)
            img = Image.open(buf)
        unfiltered = re.sub(r"\n[\n ]*", "\n", pytesseract.image_to_string(ImageOps.grayscale(img)))
        filtered = re.sub(r"", "", unfiltered, flags=re.IGNORECASE)
        return filtered

    @commands.command(aliases=["ocr"])
    @commands.max_concurrency(2, commands.BucketType.channel, wait=True)
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
                    if ref.message_id in self.ocr_done:
                        await ctx.reply("I have already read this image.")
                        return
                    self.ocr_done.add(cast(int, ref.message_id))
                    attachments = cast(discord.Message, ref.resolved).attachments
                    if len(attachments) == 1:
                        buffer = BytesIO(await attachments[0].read())
                        res = await asyncio.to_thread(self.get_text, buffer)
                    else:
                        await ctx.reply("Please provide an image or reply to a message with an image.")
                        return
                else:
                    await ctx.reply("Please provide an image or reply to a message with an image.")
                    return
            else:
                self.ocr_done.add(ctx.message.id)
                buffer = BytesIO(await image.read())
                res = await asyncio.to_thread(self.get_text, buffer)
            if len(res.strip()) < 5:
                await ctx.reply("I could not read any text from the image.")
            else:
                await ctx.reply(f"```\n{res.strip()[:300]}\n```")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Called when a reaction is added to a message.

        Parameters
        ----------
        payload : discord.RawReactionActionEvent
            The payload of the reaction.
        """
        if payload.guild_id != 225345178955808768:
            return
        if not payload.emoji.is_unicode_emoji():
            return
        elif payload.emoji.name != "\U0001F984":
            return
        if payload.message_id in self.ocr_done:
            return
        self.ocr_done.add(payload.message_id)
        guild = cast(discord.Guild, self.bot.get_guild(payload.guild_id))
        channel = cast(
            discord.TextChannel | discord.VoiceChannel,
            guild.get_channel(payload.channel_id) or await guild.fetch_channel(payload.channel_id),
        )
        message = await channel.fetch_message(payload.message_id)
        if len(message.attachments) < 1:
            await channel.send(f"Please only react to messages with at least one attachment. <@{payload.user_id}>")
            return
        buffer = BytesIO(await message.attachments[0].read())
        res = await asyncio.to_thread(self.get_text, buffer)
        if len(res.strip()) < 5:
            await channel.send(f"<@{payload.user_id}> I could not read any text from the image.")
        else:
            await channel.send(f"<@{payload.user_id}>\n```\n{res.strip()[:300]}\n```")

    @tasks.loop(hours=24)
    async def clear_ocr_done(self):
        """Clear the OCR done set."""
        self.ocr_done.clear()

    @app_commands.command()
    @app_commands.guild_only()
    async def rules(
        self,
        interaction: "Interaction[CBot]",
        rule: app_commands.Range[int, 1, 10] | None = None,
        member: discord.Member | None = None,
    ):
        """Get a rule or the rules of the server.

        Parameters
        ----------
        interaction: Interaction[CBot]
            The interaction of the command.
        rule: app_commands.Range[int, 1, 10] | None
            The rule to get, if None, all rules are returned.
        member: discord.Member | None
            The member to get the rules for, if None, the author is quietly sent the rule(s).
        """
        if not rule:
            resp = (
                "\n".join(f"**{num}**: {_rule}" for num, _rule in __rules__.items()) + "The rules can be found here: "
                "https://docs.google.com/document/d/1BFVIJXSaJmze2czLFK3Ysme2f7qKYhWU17GyQJZdUSc"
            )
        else:
            resp = (
                f"Rule **{rule}** is {__rules__[rule]}\n The rules can be found here: "
                f"https://docs.google.com/document/d/1BFVIJXSaJmze2czLFK3Ysme2f7qKYhWU17GyQJZdUSc"
            )
        if member:
            await interaction.response.send_message(
                f"{member.mention}:\n{resp}",
                allowed_mentions=discord.AllowedMentions(
                    users=[member], everyone=False, roles=False, replied_user=False
                ),
            )
        else:
            await interaction.response.send_message(resp, ephemeral=True)


async def setup(bot: "CBot"):
    """Load Plugin.

    Parameters
    ----------
    bot : commands.Bot
        The bot object to bind the cog to.
    """
    await bot.add_cog(Query(bot), override=True)
