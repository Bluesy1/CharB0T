# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""Game giveaway extension."""
import asyncio
import datetime
import random
import warnings
from statistics import mean
from typing import Any, cast

import asyncpg
import discord
import pandas as pd
from discord import ui
from discord.ext import commands, tasks
from discord.utils import MISSING, utcnow
from fluent.runtime import FluentLocalization

from . import CBot, errors


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
        if url is not None:
            self.add_item(ui.Button(label=game, style=discord.ButtonStyle.link, url=url))

    def __repr__(self):
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
            game = cast(str, embed.title)
            url = embed.url
            view = cls(bot, embed, game, url)
            view.message = message
            view.top_bid = 0
            view.total_entries = int(cast(str, embed.fields[3].value))
            if view.total_entries:
                view.check.disabled = False
        except (IndexError, ValueError, TypeError, AssertionError) as e:
            raise KeyError("Invalid giveaway embed.") from e
        return view

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if the interaction is valid.

        Parameters
        ----------
        interaction : discord.Interaction
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
        user = cast(discord.Member, interaction.user)
        if all(role.id not in self.bot.ALLOWED_ROLES for role in user.roles):
            raise errors.MissingProgramRole(self.bot.ALLOWED_ROLES, interaction.locale)
        return True

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: ui.Item[Any]) -> None:
        """Error handler.

        Parameters
        ----------
        interaction : discord.Interaction
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
            self.embed.add_field(name="Winner", value=f"{winner.name}#{winner.discriminator}", inline=True)
            if drawn:
                self.embed.add_field(
                    name="Backup Winners",
                    value=f"{', '.join(f'{m.name}#{m.discriminator}' for m in drawn)}",
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
            if return_bids:
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
                if len(winners_) >= 3:
                    break
                if win not in winners_:
                    winners_.append(win)
            while len(winners_) < min(3, len(bids[0])):
                new_winner = random.sample(bids[0], k=1, counts=bids[1])
                if new_winner[0] not in winners_:
                    winners_.append(new_winner[0])
            if self.message.guild is None:
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

    # noinspection PyUnusedLocal
    @ui.button(label="Bid", style=discord.ButtonStyle.green)
    async def bid(self, interaction: discord.Interaction, button: ui.Button) -> None:  # skipcq: PYL-W0613
        """Increase or make the initial bid for a user.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        async with self.bot.pool.acquire() as conn:
            wins = await conn.fetchval("SELECT wins FROM winners WHERE id = $1", interaction.user.id) or 0
            if wins >= 3:
                translator = FluentLocalization(
                    [interaction.locale.value, "en-US"], ["giveaway.ftl"], self.bot.localizer_loader
                )
                await interaction.response.send_message(translator.format_value("giveaway-try-later"), ephemeral=True)
                return
        modal = BidModal(self.bot, self)
        await interaction.response.send_modal(modal)
        await modal.wait()
        if self.total_entries > 0:
            self.check.disabled = False
        self.embed.set_field_at(3, name="Total Reputation Bid", value=f"{self.total_entries}")
        message = cast(discord.WebhookMessage, self.message)
        await message.edit(embed=self.embed, view=self)

    # noinspection PyUnusedLocal
    @ui.button(label="Check", style=discord.ButtonStyle.blurple, disabled=True)
    async def check(self, interaction: discord.Interaction, button: ui.Button) -> None:  # skipcq: PYL-W0613
        """Check the current bid for a user.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        async with self.bot.pool.acquire() as conn:
            translator = FluentLocalization(
                [interaction.locale.value, "en-US"], ["giveaway.ftl"], self.bot.localizer_loader
            )
            wins = await conn.fetchval("SELECT wins FROM winners WHERE id = $1", interaction.user.id) or 0
            if wins >= 3:
                await interaction.response.send_message(translator.format_value("giveaway-try-later"), ephemeral=True)
                return
            record = await conn.fetchval("SELECT bid FROM bids WHERE id = $1", interaction.user.id)
            bid: int = record if record is not None else 0
        chance = bid / self.total_entries
        await interaction.response.send_message(
            translator.format_value("giveaway-check-success", {"bid": bid, "chance": chance, "wins": wins}),
            ephemeral=True,
        )

    # noinspection PyUnusedLocal
    @ui.button(label="Toggle Giveaway Alerts", style=discord.ButtonStyle.danger)
    async def toggle_alerts(self, interaction: discord.Interaction, button: ui.Button) -> None:  # skipcq: PYL-W0613
        """Toggle the giveaway alerts.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        await interaction.response.defer(ephemeral=True, thinking=True)
        user = cast(discord.Member, interaction.user)
        async with self.role_semaphore:
            translator = FluentLocalization(
                [interaction.locale.value, "en-US"], ["giveaway.ftl"], self.bot.localizer_loader
            )
            if all(role.id != 972886729231044638 for role in user.roles):
                await user.add_roles(discord.Object(id=972886729231044638), reason="Toggled giveaway alerts.")
                await interaction.followup.send(translator.format_value("giveaway-alerts-enable"))
            else:
                await user.remove_roles(discord.Object(id=972886729231044638), reason="Toggled giveaway alerts.")
                await interaction.followup.send(translator.format_value("giveaway-alerts-disable"))


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
        if 0 > bid_int < 32768:
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

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
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


async def setup(bot: CBot):
    """Giveaway cog setup.

    Parameters
    ----------
    bot : CBot
        The bot to add the cog to.
    """
    await bot.add_cog(Giveaway(bot), override=True)
