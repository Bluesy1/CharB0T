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
"""Game giveaway extension."""
import copy
import datetime
import os
import random
import warnings
from statistics import mean

import asyncpg
import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
from discord.utils import utcnow

from main import CBot, NoGiveawayRole, giveaway_command_check, check_giveaway, __TIME__, __ZONEINFO__


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
        self.message: discord.Message | None = None
        self.bidders: list[asyncpg.Record] = []
        if url is not None:
            self.add_item(ui.Button(label=game, style=discord.ButtonStyle.link, url=url))

    async def end(self, webhook: discord.Webhook, report_hook: discord.Webhook):
        """End the giveaway.

        Parameters
        ----------
        webhook: discord.Webhook
            The webhook to send the giveaway message to.
        report_hook: discord.Webhook
            The webhook to send the report message to.
        """
        self.bid.disabled = True
        self.bid.label = "Giveaway ended"
        self.check.disabled = True
        self.check.label = "Giveaway ended"
        self.embed.set_footer(text="Giveaway ended")
        self.embed.timestamp = utcnow()
        self.embed.clear_fields()
        async with self.bot.pool.acquire() as conn:  # type: asyncpg.Connection
            bidders = await conn.fetch("SELECT * FROM bids ORDER BY bid DESC")
        self.bidders = copy.deepcopy(bidders)
        bids: list[list[int]] = [[], []]
        for bid in bidders:
            bids[0].append(bid["id"])
            bids[1].append(bid["bid"])
        _winners = random.sample(bids[0], k=6, counts=bids[1])
        winners = []
        for win in _winners:
            if len(winners) >= 3:
                break
            if win not in winners:
                winners.append(win)
        while len(winners) < min(3, len(bids[0])):
            new_winner = random.sample(bids[0], k=1, counts=bids[1])
            if new_winner[0] not in winners:
                winners.append(new_winner[0])
        winner = await webhook.channel.guild.fetch_member(winners[0])  # type: ignore
        async with self.bot.pool.acquire() as conn:  # type: asyncpg.Connection
            winning_bid = await conn.fetchval("SELECT bid FROM bids WHERE id = $1", winners[0])
        self.embed.title = f"{winner.display_name} won the {self.game} giveaway!"
        self.embed.add_field(name="Winner", value=f"{winner.mention} with {winning_bid} points bid.", inline=True)
        self.embed.add_field(name="Bidders", value=f"{len(bids[0])}", inline=True)
        self.embed.add_field(name="Average Bid", value=f"{mean(bids[1]):.2f}", inline=True)
        self.embed.add_field(
            name="Average Win Chance", value=f"{(mean(bids[1])*100/self.total_entries):.2f}", inline=True
        )
        self.embed.add_field(name="Top Bid", value=f"{self.top_bid:.2f}", inline=True)
        self.embed.add_field(name="Total Entries", value=f"{self.total_entries}", inline=True)
        self.embed.add_field(name="Winners", value="4 Backup winners selected if ", inline=True)
        await self.message.edit(embed=self.embed, view=self)  # type: ignore
        await webhook.send(
            f"Congrats to {winner.mention} for winning the {self.game} giveaway!",
            allowed_mentions=discord.AllowedMentions(users=True),
        )
        await report_hook.send(
            f"{winner.mention} won the {self.game} giveaway!\nBackup winners: {winners[1:]}. all winner ids:"
            f" {winners}\nBidders: {len(bids[0])}\nAverage bid: {mean(bids[1]):.2f}\nAverage win chance:"
            f" {(mean(bids[1])*100/self.total_entries):.2f}\nTop bid: {self.top_bid:.2f}\nTotal entries: "
            f"{self.total_entries}\n ***BIDS WIPED AND PREPPING FOR NEW GIVEAWAY***",
            allowed_mentions=discord.AllowedMentions(users=True),
        )
        async with self.bot.pool.acquire() as conn:  # type: asyncpg.Connection
            # noinspection SqlWithoutWhere
            await conn.execute("DELETE FROM bids")

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
        if self.message is None:
            self.message = interaction.message
        if not check_giveaway(interaction.user.roles):  # type: ignore
            await interaction.response.send_message("You must be at least level 5 to participate in the giveaways!")
            return
        modal = BidModal(self.bot, self)
        await interaction.response.send_modal(modal)
        await modal.wait()

    # noinspection PyUnusedLocal
    @ui.button(label="Check", style=discord.ButtonStyle.blurple)
    async def check(self, interaction: discord.Interaction, button: ui.Button) -> None:  # skipcq: PYL-W0613
        """Check the current bid for a user.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        button : ui.Button
            The button that was pressed.
        """
        if not check_giveaway(interaction.user.roles):  # type: ignore
            await interaction.response.send_message("You must be at least level 5 to participate in the giveaways!")
            return
        async with self.bot.pool.acquire() as conn:
            record = await conn.fetchval("SELECT bid FROM bids WHERE id = $1", interaction.user.id)
            bid: int = record if record is not None else 0
        chance = bid * 100 / self.total_entries
        await interaction.response.send_message(
            f"You have bid {bid} entries, giving you a {chance:.2f}% chance of winning!", ephemeral=True
        )


class BidModal(ui.Modal):
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
        super().__init__(timeout=None)
        self.bot = bot
        self.view = view

    bid_str = ui.TextInput(
        label="Increase bid by. If the value you enter is larger than your point balance, all your points will be bid.",
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
        try:
            bid_int = int(self.bid_str.value)  # type: ignore
        except ValueError:
            await interaction.response.send_message("Please enter a valid integer between 0 and 32768.", ephemeral=True)
            return self.stop()
        if 32768 < bid_int < 0:
            await interaction.response.send_message("Please enter a valid integer between 0 and 32768.", ephemeral=True)
            return self.stop()
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:  # type: asyncpg.Connection
            points: int | None = await conn.fetchval("SELECT points FROM users WHERE id = $1", interaction.user.id)
            if points is None or points == 0:
                await interaction.followup.send("You either have never gathered points or have 0.")
                return self.stop()
            if points < bid_int:
                await interaction.followup.send(
                    f"You do not have enough points to bid {bid_int} more. You have {points} points."
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
            new_bid: int | None = await conn.fetchval(
                "UPDATE bids SET bid = bid + $1 WHERE id = $2 RETURNING bid", bid_int, interaction.user.id
            )
            if new_bid is None:
                warnings.warn("Bid should not be None at this code.", RuntimeWarning)
                new_bid = bid_int
                await conn.execute("UPDATE bids SET bid = $1 WHERE id = $2", bid_int, interaction.user.id)
            self.view.total_entries += bid_int
            chance = new_bid * 100 / self.view.total_entries  # type: ignore
            await interaction.followup.send(
                f"You have bid {bid_int} more entries, for a total of {new_bid} entries, giving you a"
                f" {chance:.2f}% chance of winning! You now have {points} points left.",
                ephemeral=True,
            )
            if new_bid > self.view.top_bid:  # type: ignore
                self.view.top_bid = new_bid  # type: ignore
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
    giveaway_webhook: discord.Webhook
        The webhook for the giveaway.
    report_webhook: discord.Webhook
        The webhook for the giveaway report.
    """

    def __init__(self, bot: CBot):
        self.bot = bot
        self.yesterdays_giveaway: GiveawayView | None = None
        self.current_giveaway: GiveawayView | None = None
        self.charlie: discord.Member = ...  # type: ignore
        self.giveaway_webhook: discord.Webhook = ...  # type: ignore
        self.report_webhook: discord.Webhook = ...  # type: ignore

    async def cog_load(self) -> None:
        """Call when the cog is loaded."""
        self.giveaway_webhook = await self.bot.fetch_webhook(int(os.getenv("GIVEAWAY_WEBHOOK")))  # type: ignore
        self.report_webhook = await self.bot.fetch_webhook(int(os.getenv("GIVEAWAY_WIN_WEBHOOK")))  # type: ignore
        self.daily_giveaway.start()

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Call when the cog is unloaded."""
        self.daily_giveaway.cancel()

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """Handle errors in commands.

        This is called when an error is raised while running a command.

        This only handles one specific error, :class:`NoGiveawayRole`, and otherwise re raises the error.

        Parameters
        ----------
        ctx : commands.Context
            The context of the command.
        error : Exception
            The error that was raised.

        Raises
        ------
        Exception
            The error that was raised, it wasn't NoGiveawayRole.
        """
        if isinstance(error, NoGiveawayRole):
            await ctx.send(error.message, ephemeral=True)
        else:
            raise error

    @commands.hybrid_group(name="giveaway", description="Giveaway commands.")
    @giveaway_command_check()
    @app_commands.guilds(225345178955808768)
    async def giveaway(self, ctx: commands.Context) -> None:
        """Giveaway commands.

        This command group is used to manage giveaways.

        Invoking the base group as a prefix command is informs the invoker of the subcommands.

        Parameters
        ----------
        ctx : commands.Context
            The context of the command invocation.
        """
        await ctx.send("The subcommanf options for `giveaway` are `query` and `daily`.")

    @giveaway.command(name="daily", description="Claim your daily points")
    @giveaway_command_check()
    @app_commands.guilds(225345178955808768)
    async def daily(self, ctx: commands.Context):
        """Get a daily reward.

        Parameters
        ----------
        ctx : commands.Context
            The context of the command invocation.
        """
        user = await self.bot.giveaway_user(ctx.author.id)
        if user is None:
            async with self.bot.pool.acquire() as conn:
                await conn.execute("INSERT INTO users (id, points) VALUES ($1, 20)", ctx.author.id)
                await conn.execute(
                    "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won) VALUES "
                    "($1, $2, $3, 0, 0)",
                    ctx.author.id,
                    __TIME__(),
                    __TIME__() - datetime.timedelta(days=1),
                )
                await ctx.send("You got your daily reward of 20 points!")
            return
        if user["daily"] == __TIME__():
            await ctx.send("You already got your daily reward.")
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE users SET points = points + 20 WHERE id = $1", ctx.author.id)
            await conn.execute("UPDATE daily_points SET last_claim = $1 WHERE id = $2", __TIME__(), ctx.author.id)
        await ctx.send("You got your daily reward of 20 points!")

    @giveaway.command(name="query", description="Query your points")
    @giveaway_command_check()
    @app_commands.guilds(225345178955808768)
    async def query_points(self, ctx: commands.Context):
        """Query your points.

        Parameters
        ----------
        ctx : commands.Context
            The context of the command invocation.
        """
        user = await self.bot.giveaway_user(ctx.author.id)
        points = user["points"] if user is not None else 0
        if ctx.interaction is not None:
            await ctx.send(f"You have {points} points.", ephemeral=True)
        else:
            await ctx.author.send(f"You have {points} points.")

    @tasks.loop(time=datetime.time(hour=0, minute=0, second=0, tzinfo=__ZONEINFO__))  # skipcq: PYL-E1123
    async def daily_giveaway(self):
        """Run the daily giveaway."""
        if self.current_giveaway is not None:
            self.yesterdays_giveaway = self.current_giveaway
            await self.yesterdays_giveaway.end(self.giveaway_webhook, self.report_webhook)
        if self.charlie is None:
            self.charlie = await (await self.bot.fetch_guild(225345178955808768)).fetch_member(225344348903047168)
        # TODO: Do Whatever i have to do to get the game, and optionally URL for the new giveaway  # skipcq: PYL-W0511
        game = "Placeholder untill charlie gets me a list of games"
        url = "https://discord.com/developers/docs/intro"
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
        embed.add_field(
            name="How to get points",
            value="You get points by using the `!daily` command and by playing the minigames.",
            inline=True,
        )
        embed.add_field(name="Total Points Bid", value="0", inline=True)
        embed.add_field(name="Largest Bid", value="0", inline=True)
        self.current_giveaway = GiveawayView(self.bot, embed, game, url)
        self.current_giveaway.message = await self.giveaway_webhook.send(
            embed=embed, view=self.current_giveaway, wait=True
        )


async def setup(bot: CBot):
    """Giveaway cog setup.

    Parameters
    ----------
    bot : CBot
        The bot to add the cog to.
    """
    await bot.add_cog(Giveaway(bot), guild=discord.Object(id=225345178955808768), override=True)
