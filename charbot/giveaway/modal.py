"""Bid modal class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, cast

import discord
from discord import Interaction, ui


if TYPE_CHECKING:  # pragma: no cover
    from . import CBot, GiveawayView

_LanguageTag = Literal["en-US", "es-ES", "fr", "nl"]


def rectify_bid(bid_int: int, current_bid: int | None, points: int) -> int:
    """Rectify the bid to ensure it is within the bounds.

    Parameters
    ----------
    bid_int : int
        The bid as an integer.
    current_bid : int | None
        The current bid for the user.
    points : int
        The user's points.

    Returns
    -------
    bid_int: int
        The rectified bid.
    """
    bid_int = min(bid_int, points)
    current_bid = current_bid or 0
    if current_bid + bid_int > 32768:
        bid_int = 32768 - current_bid
    return bid_int


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

    async def on_submit(self, interaction: Interaction[CBot]) -> None:
        """Call when a bid modal is submitted.

        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction that was submitted.
        """
        try:
            val = self.bid_str.value
            bid_int = int(val)
        except ValueError:  # pragma: no cover
            return await self.invalid_bid(interaction)
        if 0 >= bid_int <= 32768:  # pragma: no cover
            return await self.invalid_bid(interaction)
        await interaction.response.defer(ephemeral=True, thinking=True)
        async with self.view.bid_lock, self.bot.pool.acquire() as conn, conn.transaction():
            points: int | None = await conn.fetchval("SELECT points FROM users WHERE id = $1", interaction.user.id)
            if not await self.check_points(bid_int, interaction, points):  # pragma: no cover
                return
            bid_int = rectify_bid(
                bid_int,
                await conn.fetchval("SELECT bid FROM bids WHERE id = $1", interaction.user.id),
                cast(int, points),
            )
            points = await conn.fetchval(
                "UPDATE users SET points = points - $1 WHERE id = $2 RETURNING points", bid_int, interaction.user.id
            )
            new_bid = await conn.fetchval(
                "UPDATE bids SET bid = bid + $1 WHERE id = $2 RETURNING bid", bid_int, interaction.user.id
            )
            await self.bid_success(
                interaction,
                bid_int,
                cast(int, new_bid),
                cast(int, points),
                await conn.fetchval("SELECT wins FROM winners WHERE id = $1", interaction.user.id),
            )
            self.stop()

    async def bid_success(
        self, interaction: Interaction[CBot], bid_int: int, new_bid: int, points: int, wins: int | None
    ) -> None:
        """Call when a bid is successful.

        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction that was submitted.
        bid_int : int
            The amount of points that were bid.
        new_bid : int
            The new bid.
        points : int
            The user's new points.
        wins : int | None
            The user's wins, if any.
        """
        self.view.total_entries += bid_int
        chance = new_bid * 100 / self.view.total_entries
        message = (
            f"You have bid {bid_int} more entries, for a total of {new_bid} entries, giving you a "
            + f"{chance:.2f}% chance of winning! You now have {points} reputation left, and you "
            + f"have won {wins or 0}/3 giveaways you can this month!"
        )
        await interaction.followup.send(message, ephemeral=True)
        self.view.top_bid = max(new_bid, self.view.top_bid)

    async def check_points(self, bid_int: int, interaction: Interaction[CBot], points: int | None) -> bool:
        """Check if the user has enough points to bid.

        Parameters
        ----------
        bid_int : int
            The bid amount.
        interaction : Interaction[CBot]
            The interaction that was submitted.
        points : int | None
            The user's points.

        Returns
        -------
        valid : bool
            If the user's bid is valid.
        """
        if points is None or points == 0:
            await interaction.followup.send("You either have never gained reputation or have 0.")
            self.stop()
            return False
        if points < bid_int:
            await interaction.followup.send(
                f"You do not have enough reputation to bid {bid_int} entries, you need {points} more."
            )
            self.stop()
            return False
        return True

    async def invalid_bid(self, interaction: Interaction[CBot]):
        """Call when a bid is invalid."""
        await interaction.response.send_message(
            "Please enter a valid integer above 0 and less than 32768.",
            ephemeral=True,
        )
        return self.stop()
