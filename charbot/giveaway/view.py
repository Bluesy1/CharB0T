# -*- coding: utf-8 -*-
"""Giveaway view."""
from __future__ import annotations

import asyncio
import random
from statistics import mean
from typing import TYPE_CHECKING, Any, Literal, cast

import asyncpg
import discord
from discord import Interaction, ui
from discord.utils import MISSING, utcnow

import charbot_rust
from . import BidModal
from .. import errors

if TYPE_CHECKING:  # pragma: no cover
    from .. import CBot

_LanguageTag = Literal["en-US", "es-ES", "fr", "nl"]


async def hit_max_wins(interaction: Interaction["CBot"]):
    """Standard response for when a user has hit max wins for a month."""
    try:
        await interaction.response.send_message(
            charbot_rust.translate(cast(_LanguageTag, interaction.locale.value), "giveaway-try-later", {}),
            ephemeral=True,
        )
    except RuntimeError:  # pragma: no cover
        await interaction.response.send_message(
            "You have won 3 giveaways recently, please wait until the first of the next month to bid again.",
            ephemeral=True,
        )


class GiveawayView(ui.View):
    """Giveaway view.
    Handles the giveaway and prompts modals on button click.
    Parameters
    ----------
    bot : CBot
        The bot instance.
    embed : discord.Embed
        The embed of the giveaway.
    game : str
        The game being given away.
    url : str | None
        The url of the game being given away.
    Attributes
    ----------
    bot : CBot
        The bot instance.
    embed : discord.Embed
        The embed of the giveaway.
    total_entries : int
        The total number of entries.
    top_bid : int
        The top bid.
    game : str
        The game being given away.
    url : str | None
        The url of the game being given away.
    message : discord.Message | None
        The message of the giveaway.
    bidders : list[asyncpg.Record]
        The list of bidders. Only filled when the end() method is called.
    """

    def __init__(self, bot: CBot, embed: discord.Embed, game: str, url: str | None = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.embed = embed
        self.total_entries = 0
        self.top_bid = 0
        self.game = game
        self.url = url
        self.message: discord.WebhookMessage = MISSING
        self.role_semaphore = asyncio.BoundedSemaphore(10)
        self.bid_lock = asyncio.Lock()
        self.bidders: list[asyncpg.Record] = []
        if url is not None:  # pragma: no branch
            self.add_item(ui.Button(label=game, style=discord.ButtonStyle.link, url=url))

    def __repr__(self):  # pragma: no cover
        """Representation of the view."""
        return (
            f"<{self.__class__.__name__} timeout={self.timeout} children={len(self._children)}"
            f" game={self.game} total_entries={self.total_entries} top_bid={self.top_bid}>"
        )

    @classmethod
    def recreate_from_message(cls, message: discord.WebhookMessage, bot: CBot):
        """Create a view from a message.
        Parameters
        ----------
        message : discord.Message
            The message of the giveaway.
        bot : CBot
            The bot instance.
        Returns
        -------
        GiveawayView
            The view of the giveaway.
        """
        try:
            embed = message.embeds[0]
            view = cls(bot, embed, cast(str, embed.description).split("[")[1].split("]")[0], embed.url)
            view.message = message
            view.top_bid = 0
            view.total_entries = int(cast(str, embed.fields[3].value))
            if view.total_entries:  # pragma: no branch
                view.check.disabled = False
        except (IndexError, ValueError, TypeError) as e:
            raise KeyError("Invalid giveaway embed.") from e
        return view

    async def interaction_check(self, interaction: Interaction["CBot"]) -> bool:  # pragma: no cover
        """Check if the interaction is valid.
        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction to check.
        Returns
        -------
        bool
            Whether the interaction is valid.
        Raises
        ------
        errors.MissingProgramRole
            If no program roles are present.
        """
        if all(role.id not in self.bot.ALLOWED_ROLES for role in cast(discord.Member, interaction.user).roles):
            raise errors.MissingProgramRole(self.bot.ALLOWED_ROLES, interaction.locale)
        return True

    async def on_error(
        self, interaction: Interaction["CBot"], error: Exception, item: ui.Item[Any]
    ) -> None:  # pragma: no cover
        """Error handler.
        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction.
        error : Exception
            The error.
        item : ui.Item
            The item.
        """
        if isinstance(error, errors.MissingProgramRole):
            await interaction.response.send_message(error.message, ephemeral=True)
        else:
            await super(GiveawayView, self).on_error(interaction, error, item)

    def _prep_view_for_draw(self):
        """Disable all buttons."""
        self.bid.disabled = True
        self.bid.label = "Giveaway ended"
        self.check.disabled = True
        self.check.label = "Giveaway ended"
        self.toggle_alerts.disabled = True
        self.toggle_alerts.label = "Giveaway ended"
        self.embed.set_footer(text="Giveaway ended")
        self.embed.timestamp = utcnow()
        self.embed.clear_fields()
        self.stop()

    def _create_drawn_embed(
        self,
        winner: discord.Member | None,
        drawn: list[discord.Member],
        winning_bid: int,
        avg_bid: float,
        total_bidders: int,
    ):
        """Create the post draw embed.
        Parameters
        ----------
        winner : discord.Member
            The winner of the giveaway.
        drawn : list[discord.Member]
            The list of drawn members as backups.
        winning_bid : int
            The winning bid.
        avg_bid : int
            The average bid.
        total_bidders : int
            The total number of bidders.
        """
        if winner is not None:
            self.embed.title = f"{winner.display_name} won the {self.game} giveaway!"
            self.embed.add_field(
                name="Winner", value=f"{winner.mention} with {winning_bid} reputation bid.", inline=True
            )
            self.embed.add_field(name="Bidders", value=total_bidders, inline=True)
            self.embed.add_field(
                name="Average Bid and Win Chance",
                value=f"{avg_bid:.2f}, {(avg_bid * 100 / self.total_entries):.2f}%",
                inline=True,
            )
            self.embed.add_field(name="Top Bid", value=f"{self.top_bid:.2f}", inline=True)
            self.embed.add_field(name="Total Entries", value=f"{self.total_entries}", inline=True)
            self.embed.add_field(name="Winner", value=f"{winner}", inline=True)
            if drawn:  # pragma: no branch
                self.embed.add_field(
                    name="Backup Winners",
                    value=f"{', '.join(f'{member}' for member in drawn)}",
                    inline=True,
                )
                _drawn = [winner, *drawn]
                self.embed.add_field(
                    name="All Drawn People", value=f"{', '.join(m.mention for m in _drawn)}", inline=True
                )
        else:
            self.embed.add_field(name="No Winners", value="No bids were made.", inline=True)

    async def _get_bidders(self) -> list[asyncpg.Record]:
        """Get the bidders.
        Returns
        -------
        list[asyncpg.Record]
        """
        async with self.bot.pool.acquire() as conn:
            blocked: list[int] = [block["id"] for block in await conn.fetch("SELECT id FROM winners WHERE wins >= 3")]
            raw_bidders = await conn.fetch("SELECT * FROM bids WHERE bid > 0 ORDER BY bid DESC")
            bidders = [bid for bid in raw_bidders if bid["id"] not in blocked]
            return_bids = [(bid["bid"], bid["id"]) for bid in raw_bidders if bid["id"] in blocked]
            if return_bids:  # pragma: no cover
                await conn.executemany("UPDATE users SET points = points + $1 WHERE id = $2", return_bids)
        return bidders

    async def _draw_winner(self, bidders: list[asyncpg.Record]) -> tuple[list[discord.Member], float]:
        """Draw the winner.
        Parameters
        ----------
        bidders : list[asyncpg.Record]
            The list of bidders.
        Returns
        -------
        tuple[list[discord.Member], float]
            The list of drawn members and the average bid.
        """
        if bidders:
            self.bidders = bidders.copy()
            bids: list[list[int]] = [[], []]
            for bid in bidders:
                bids[0].append(bid["id"])
                bids[1].append(bid["bid"])
            avg_bid = mean(bids[1])
            _winners = random.sample(bids[0], k=min(6, len(bidders)), counts=bids[1])
            winners_ = []
            for win in _winners:
                if len(winners_) >= 3:  # pragma: no cover
                    break
                if win not in winners_:
                    winners_.append(win)
            while len(winners_) < min(3, len(bids[0])):
                new_winner = random.sample(bids[0], k=1, counts=bids[1])
                if new_winner[0] not in winners_:  # pragma: no branch
                    winners_.append(new_winner[0])
            if self.message.guild is None:  # pragma: no cover
                _id = 225345178955808768
                self.message.guild = self.bot.get_guild(_id) or await self.bot.fetch_guild(_id)
            winners = [await self.message.guild.fetch_member(winner) for winner in winners_]
        else:
            winners = []
            avg_bid = 0
        return winners, avg_bid

    async def end(self):
        """End the giveaway."""
        self._prep_view_for_draw()
        bidders = await self._get_bidders()
        self.top_bid = max(bidders, key=lambda bid: bid["bid"], default={"bid": 0})["bid"]
        self.total_entries = sum(bid["bid"] for bid in bidders)
        winners, avg_bid = await self._draw_winner(bidders)
        if winners:
            winner = winners[0]
            winning_bid = await self.bot.pool.fetchval("SELECT bid FROM bids WHERE id = $1", winner.id)
        else:
            winner = None
            winning_bid = 0
        self._create_drawn_embed(winner, winners[1:], winning_bid, avg_bid, len(bidders))
        message = cast(discord.Message, self.message)
        await message.edit(embed=self.embed, view=self)
        if winner is not None:
            await self.bot.giveaway_webhook.send(
                f"Congrats to {winner.mention} for winning the {self.game} giveaway! Please send a single DM to"
                f" Charlie to claim it. If you're listed under backups, stay tuned for if the first winner does not"
                f" reach out to redeem their prize.",
                allowed_mentions=discord.AllowedMentions(users=True),
            )
        await self.bot.pool.execute("UPDATE bids SET bid = 0 WHERE bid > 0")
        await self.bot.program_logs.send(
            f"{self.game} giveaway ended. {len(bidders)} bidders, {len(winners)} winners, "
            f"{self.total_entries} entries, {self.top_bid} top bid.\n Winners:"
            f" {', '.join(w.mention for w in winners)}"
        )

    @ui.button(label="Bid", style=discord.ButtonStyle.green)
    async def bid(self, interaction: Interaction["CBot"], button: ui.Button) -> None:  # skipcq: PYL-W0613
        """Increase or make the initial bid for a user.
        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        async with interaction.client.pool.acquire() as conn:
            wins = await conn.fetchval("SELECT wins FROM winners WHERE id = $1", interaction.user.id) or 0
            if wins >= 3:
                await hit_max_wins(interaction)
                return
        modal = BidModal(self.bot, self)
        await interaction.response.send_modal(modal)

        async def _task():
            """Wait for the modal to be closed."""
            await modal.wait()
            if self.total_entries > 0:  # pragma: no cover
                self.check.disabled = False
            self.embed.set_field_at(3, name="Total Reputation Bid", value=f"{self.total_entries}")
            message = cast(discord.WebhookMessage, self.message)
            await message.edit(embed=self.embed, view=self)

        asyncio.create_task(_task())

    @ui.button(label="Check", style=discord.ButtonStyle.blurple, disabled=True)
    async def check(self, interaction: Interaction["CBot"], button: ui.Button) -> None:  # skipcq: PYL-W0613
        """Check the current bid for a user.
        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        async with interaction.client.pool.acquire() as conn:
            wins = await conn.fetchval("SELECT wins FROM winners WHERE id = $1", interaction.user.id) or 0
            if wins >= 3:
                await hit_max_wins(interaction)
                return
            record = await conn.fetchval("SELECT bid FROM bids WHERE id = $1", interaction.user.id)
            bid: int = record if record is not None else 0
        chance = round(100 * bid / self.total_entries, 2)
        await interaction.response.send_message(
            charbot_rust.translate(
                cast(_LanguageTag, interaction.locale.value),
                "giveaway-check-success",
                {"bid": bid, "chance": chance, "wins": wins},
            ),
            ephemeral=True,
        )

    @ui.button(label="Toggle Giveaway Alerts", style=discord.ButtonStyle.danger)
    async def toggle_alerts(
        self, interaction: Interaction["CBot"], _: ui.Button
    ) -> None:  # skipcq: PYL-W0613  # pragma: no cover
        """Toggle the giveaway alerts.
        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction object.
        _ : ui.Button
            The button that was pressed.
        """
        await interaction.response.defer(ephemeral=True, thinking=True)
        async with self.role_semaphore:
            if all(role.id != 972886729231044638 for role in cast(discord.Member, interaction.user).roles):
                await cast(discord.Member, interaction.user).add_roles(
                    discord.Object(id=972886729231044638), reason="Toggled giveaway alerts."
                )
                await interaction.followup.send(
                    charbot_rust.translate(cast(_LanguageTag, interaction.locale.value), "giveaway-alerts-enable", {})
                )
            else:
                await cast(discord.Member, interaction.user).remove_roles(
                    discord.Object(id=972886729231044638), reason="Toggled giveaway alerts."
                )
                await interaction.followup.send(
                    charbot_rust.translate(cast(_LanguageTag, interaction.locale.value), "giveaway-alerts-disable", {})
                )
