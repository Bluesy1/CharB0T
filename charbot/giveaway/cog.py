# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Giveaway  commands."""
from __future__ import annotations
import datetime
from typing import TYPE_CHECKING, cast

import discord
import pandas as pd
from discord.ext import commands, tasks
from discord.utils import MISSING, utcnow

from . import GiveawayView

if TYPE_CHECKING:
    from .. import CBot


class Giveaway(commands.Cog):
    """Giveaway commands.
    This cog is for the giveaway commands, and the giveaway itself.
    Parameters
    ----------
    bot : CBot
        The bot instance.
    Attributes
    ----------
    bot : CBot
        The bot instance.
    yesterdays_giveaway : GiveawayView
        The giveaway view for yesterday's giveaway.
    current_giveaway : GiveawayView
        The giveaway view for the current giveaway.
    charlie: discord.Member
        The member object for charlie.
    games: pandas.DataFrame
        The games dataframe, with the index date in the form (m)m/(d)d/yyyy., and columns game, url, and source.
    """

    def __init__(self, bot: CBot):
        self.bot = bot
        self.yesterdays_giveaway: GiveawayView = bot.holder.pop("yesterdays_giveaway")
        self.current_giveaway: GiveawayView = bot.holder.pop("current_giveaway")
        self.charlie: discord.Member = MISSING
        self.games: pd.DataFrame = pd.read_csv(
            "charbot/giveaway.csv", index_col=0, usecols=[0, 1, 2, 4], names=["date", "game", "url", "source"]
        )

    async def cog_load(self) -> None:
        """Call when the cog is loaded."""
        self.daily_giveaway.start()
        if self.current_giveaway is not MISSING:
            message = self.current_giveaway.message
        else:
            message_found = False
            _message: discord.Message = MISSING
            async for _message in cast(
                discord.TextChannel | discord.VoiceChannel, await self.bot.fetch_channel(926307166833487902)
            ).history(limit=5):
                if _message.components:
                    message_found = True
                    break
            if message_found is True and _message is not MISSING:
                message = await self.bot.giveaway_webhook.fetch_message(_message.id)
            else:
                raise RuntimeError("Could not find giveaway message.")
        current_giveaway = GiveawayView.recreate_from_message(message, self.bot)
        await current_giveaway.message.edit(view=current_giveaway)
        self.current_giveaway = current_giveaway

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236  # pragma: no cover
        """Call when the cog is unloaded."""
        self.daily_giveaway.cancel()
        self.bot.holder["yesterdays_giveaway"] = self.yesterdays_giveaway
        self.bot.holder["current_giveaway"] = self.current_giveaway

    @tasks.loop(time=datetime.time(hour=9, minute=0, second=0, tzinfo=CBot.ZONEINFO))  # skipcq: PYL-E1123
    async def daily_giveaway(self):
        """Run the daily giveaway."""
        if self.bot.TIME().day == 1:
            # noinspection SqlWithoutWhere
            await self.bot.pool.execute("DELETE FROM winners")  # clear the table the start of each month
        if self.current_giveaway is not MISSING:
            self.yesterdays_giveaway = self.current_giveaway
            await self.yesterdays_giveaway.end()
        if not isinstance(self.charlie, discord.Member):
            guild = self.bot.get_guild(225345178955808768)
            if guild is None:
                guild = await self.bot.fetch_guild(225345178955808768)
            self.charlie = await guild.fetch_member(225344348903047168)
        self.games = pd.read_csv(
            "charbot/giveaway.csv", index_col=0, usecols=[0, 1, 2, 4], names=["date", "game", "url", "source"]
        )
        try:
            gameinfo: dict[str, str] = dict(self.games.loc[self.bot.TIME().strftime("%-m/%-d/%Y")])
        except KeyError:
            gameinfo: dict[str, str] = {"game": "Charlie Didn't Give me one", "url": "None", "source": "Charlie"}
        game = gameinfo["game"]
        url = gameinfo["url"] if gameinfo["url"] != "None" else None
        embed = discord.Embed(
            title="Daily Giveaway",
            description=f"Today's Game: [{game}]({url})",
            color=discord.Color.dark_blue(),
            timestamp=utcnow(),
            url=url,
        )
        embed.set_author(name=self.charlie.display_name, icon_url=self.charlie.display_avatar.url)
        embed.set_footer(text="Started at")
        embed.add_field(name="How to Participate", value="Select bid and enter your bid in the popup.", inline=True)
        embed.add_field(name="How to Win", value="The winner will be chosen at random.", inline=True)
        # noinspection SpellCheckingInspection
        embed.add_field(
            name="How to get reputation",
            value="You get reputation by attending `rollcall` and by "
            "participating in programs (games) in <#969972085445238784>.",
            inline=True,
        )
        embed.add_field(name="Total Reputation Bid", value="0", inline=True)
        self.current_giveaway = GiveawayView(self.bot, embed, game, url)
        self.current_giveaway.message = await self.bot.giveaway_webhook.send(
            "<@&972886729231044638>",
            embed=embed,
            view=self.current_giveaway,
            allowed_mentions=discord.AllowedMentions(roles=True),
            wait=True,
        )
