# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Bid modal class."""

import discord
import warnings
from discord import ui
from fluent.runtime import FluentLocalization
from typing import cast

from charbot import CBot
from . import GiveawayView


class BidModal(ui.Modal, title="Bid"):
    """Bid modal class.

    Parameters
    ----------
    bot : CBot
        The bot instance.
    view : GiveawayView
        The active giveaway view.

    Attributes
    ----------
    bot : CBot
        The bot instance.
    view : GiveawayView
        The active giveaway view.
    """

    def __init__(self, bot: CBot, view: GiveawayView):
        super().__init__(timeout=None, title="Bid")
        self.bot = bot
        self.view = view

    bid_str = ui.TextInput(
        label="How much to increase your bid by?",
        placeholder="Enter your bid (Must be an integer between 0 and 32768)",
        style=discord.TextStyle.short,
        min_length=1,
        max_length=5,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Call when a bid modal is submitted.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that was submitted.
        """
        translator = FluentLocalization(
            [interaction.locale.value, "en-US"], ["giveaway.ftl"], self.bot.localizer_loader
        )
        try:
            val = self.bid_str.value
            bid_int = int(val)
        except ValueError:
            await interaction.response.send_message(
                translator.format_value("giveaway-bid-invalid-bid."), ephemeral=True
            )
            return self.stop()
        if 0 >= bid_int <= 32768:
            await interaction.response.send_message(
                translator.format_value("giveaway-bid-invalid-bid."), ephemeral=True
            )
            return self.stop()
        await interaction.response.defer(ephemeral=True, thinking=True)
        async with self.view.bid_lock, self.bot.pool.acquire() as conn, conn.transaction():
            points: int | None = await conn.fetchval("SELECT points FROM users WHERE id = $1", interaction.user.id)
            if points is None or points == 0:
                await interaction.followup.send(translator.format_value("giveaway-bid-no-rep"))
                return self.stop()
            if points < bid_int:
                await interaction.followup.send(
                    translator.format_value("giveaway-bid-not-enough-rep", {"bid": bid_int, "points": points})
                )
                return self.stop()
            bid_int = min(bid_int, points)
            current_bid = await conn.fetchval("SELECT bid FROM bids WHERE id = $1", interaction.user.id) or 0
            if current_bid + bid_int > 32768:
                bid_int = 32768 - current_bid
            points: int | None = await conn.fetchval(
                "UPDATE users SET points = points - $1 WHERE id = $2 RETURNING points", bid_int, interaction.user.id
            )
            if points is None:
                warnings.warn("Points should not be None at this code.", RuntimeWarning)
                points = 0
                await conn.execute("UPDATE users SET points = 0 WHERE id = $1", interaction.user.id)
            _new_bid: int | None = await conn.fetchval(
                "UPDATE bids SET bid = bid + $1 WHERE id = $2 RETURNING bid", bid_int, interaction.user.id
            )
            if _new_bid is None:
                warnings.warn("Bid should not be None at this code.", RuntimeWarning)
                _new_bid = bid_int
                await conn.execute(
                    "INSERT INTO bids (bid,id) values ($1, $2) ON CONFLICT DO UPDATE SET bid = $1",
                    bid_int,
                    interaction.user.id,
                )
            self.view.total_entries += bid_int
            new_bid = cast(int, _new_bid)
            chance = new_bid / self.view.total_entries
            await interaction.followup.send(
                translator.format_value(
                    "giveaway-bid-success",
                    {
                        "bid": bid_int,
                        "new_bid": new_bid,
                        "chance": chance,
                        "points": points,
                        "wins": await conn.fetchval("SELECT wins FROM winners WHERE id = $1", interaction.user.id) or 0,
                    },
                ),
                ephemeral=True,
            )
            self.view.top_bid = max(new_bid, self.view.top_bid)
            self.stop()
