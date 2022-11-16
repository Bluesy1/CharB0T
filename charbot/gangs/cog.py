# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Gang war cog file."""
import asyncio
import datetime
from pathlib import Path
from typing import Final, cast
from zoneinfo import ZoneInfo

import asyncpg
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import MISSING

from . import dues
from . import utils
from .actions import create, join, banner, user_items, gang_items
from .banner import ApprovalView, generate_banner, gen_banner
from .types import BannerStatus, GangDues
from .shakedowns import do_shakedown
from .. import GuildInteraction as Interaction, CBot, Config
from .actions.user_items import view_items_autocomplete as user_items_autocomplete
from .actions.gang_items import view_items_autocomplete as gang_items_autocomplete

BASE_PATH: Final[Path] = Path(__file__).parent / "user_assets"


class Gangs(commands.Cog):
    """Gang war."""

    __slots__ = (
        "bot",
        "_start_dues_cycle_task",
        "_end_dues_cycle_task",
        "gang_guild",
        "gang_category",
        "gang_announcements",
    )

    def __init__(self, bot: CBot):
        self.bot = bot
        self._start_dues_cycle_task = asyncio.create_task(self.start_dues_cycle())
        self._end_dues_cycle_task = asyncio.create_task(self.end_dues_cycle())
        self.gang_guild: discord.Guild = bot.holder.get("gang_guild")
        self.gang_category: discord.CategoryChannel = bot.holder.get("gang_category")
        self.gang_announcements: discord.Webhook = bot.holder.get("gang_announcements")

    async def cog_load(self) -> None:  # pragma: no cover
        """Load."""
        config = Config["discord"]["gangs"]
        if self.gang_guild is MISSING:
            self.gang_guild = await self.bot.fetch_guild(Config["discord"]["guild"])
        if self.gang_category is MISSING:
            self.gang_category = await self.gang_guild.fetch_channel(config["category"])  # type: ignore
        if self.gang_announcements is MISSING:
            self.gang_announcements = await self.bot.fetch_webhook(config["announcements"])

    async def cog_unload(self) -> None:
        """Unload."""
        self._start_dues_cycle_task.cancel()
        self._end_dues_cycle_task.cancel()
        self.bot.holder["gang_guild"] = self.gang_guild
        self.bot.holder["gang_category"] = self.gang_category
        self.bot.holder["gang_announcements"] = self.gang_announcements

    gang = app_commands.Group(
        name="gang",
        description="Base group for gang war commands",
        guild_only=True,
        default_permissions=discord.Permissions(manage_messages=True),
    )
    participate = app_commands.Group(
        name="participate", description="Base group for starting participation in a gang war", parent=gang
    )
    banner = app_commands.Group(name="banner", description="Base group for managing the user banner", parent=gang)

    items = app_commands.Group(
        name="items",
        description="Base group for managing the user's items",
        guild_only=True,
        default_permissions=discord.Permissions(manage_messages=True),
    )
    user_items = app_commands.Group(name="user", description="Base group for managing the user's items", parent=items)
    gang_items = app_commands.Group(name="gang", description="Base group for managing the gang's items", parent=items)

    async def start_dues_cycle(self):
        """Start the dues cycle."""
        next_month = (
            datetime.datetime.now(tz=ZoneInfo("US/Michigan")).replace(day=1) + datetime.timedelta(days=32)
        ).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        await discord.utils.sleep_until(next_month)
        async with self.bot.pool.acquire() as conn, conn.transaction():
            await conn.execute(utils.SQL_MONTHLY)
            gangs: list[GangDues] = await conn.fetch(
                "SELECT name, channel, role,"
                " (TRUE = ALL(SELECT paid FROM gang_members WHERE gang = gangs.name)) as complete FROM gangs"
            )
            await asyncio.gather(
                *(dues.send_dues_start(self.gang_guild, next_month, row) for row in gangs), return_exceptions=True
            )
        self._start_dues_cycle_task = asyncio.create_task(self.start_dues_cycle())

    async def end_dues_cycle(self):
        """End the dues cycle."""
        next_month = (
            datetime.datetime.now(tz=ZoneInfo("US/Michigan")).replace(day=1) + datetime.timedelta(days=32)
        ).replace(day=8, hour=0, minute=0, second=0, microsecond=0)
        await discord.utils.sleep_until(next_month)
        async with self.bot.pool.acquire() as conn, conn.transaction():
            gangs: list[GangDues] = await conn.fetch(
                "SELECT name, channel, role, (TRUE = ALL(SELECT paid FROM gang_members WHERE gang = gangs.name))"
                " as complete FROM gangs WHERE all_paid IS FALSE"
            )
            lost_members = 0
            guild = self.gang_guild
            for row in gangs:
                lost_members += await dues.send_dues_end(cast(asyncpg.Connection, conn), guild, row)
            empty_gangs = await conn.fetch(
                "SELECT name FROM gangs WHERE 0 == (SELECT COUNT(*) FROM gang_members WHERE gang = gangs.name)"
            )
            if lost_members > 0:
                await self.gang_announcements.send(
                    f"{lost_members} member(s) of the gangs have been removed from their gangs for not paying their "
                    f"dues. If you were one of the member(s) removed, remember you can always rejoin a gang if you have"
                    f" enough rep! Thank you for participating in the gang war! {len(empty_gangs)} ran out of members"
                    f" and got disbanded temporarily."
                )
            await conn.execute("DELETE FROM gangs WHERE name in $1", [row["name"] for row in empty_gangs])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle messages."""
        if message.author.bot or message.guild is None:
            return
        member = cast(discord.Member, message.author)
        if "my gang" in message.content.lower() and message.channel.id == 225345178955808768:
            if file := await gen_banner(self.bot.pool, member):
                await message.reply(file=file)

    @participate.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def create(
        self,
        interaction: Interaction[CBot],
        color: utils.ColorOpts,
        base_join: app_commands.Range[int, 0, 32767],
        scale_join: app_commands.Range[int, 0, 32767],
        base_recurring: app_commands.Range[int, 0, 32767],
        scale_recurring: app_commands.Range[int, 0, 32767],
    ):
        """Create a new gang.

        Parameters
        ----------
        interaction : Interaction[CBot]
            Interaction object for the current context
        color : int
            Color of the gang, which forms the color and name of the gang
        base_join : int
            Base join cost
        scale_join : int
            Scale of join cost, to go up per for each member in the gang
        base_recurring : int
            Base recurring cost
        scale_recurring : int
            Scale of recurring cost, to go up per for each member in the gang
        """
        await interaction.response.defer(ephemeral=True)
        async with interaction.client.pool.acquire() as conn, conn.transaction():
            # Check if the gang already exists, the user is already in a gang, or the user doesn't have enough points
            remaining = await create.check_gang_conditions(
                cast(asyncpg.Connection, conn), interaction.user.id, color, base_join, base_recurring
            )
            if isinstance(remaining, str):
                await interaction.followup.send(remaining)
                return
            role, channel = await create.create_gang_discord_objects(
                interaction.guild, interaction.user, self.gang_category, color
            )
            await interaction.user.add_roles(role, reason=f"New gang created by {interaction.user}")
            # All gangs start with 100 control.
            await conn.execute(
                "INSERT INTO gangs (name, color, leader, role, channel, control, join_base, join_slope,"
                " upkeep_base, upkeep_slope, all_paid) VALUES ($1, $2, $3, $4, $5, 100, $6, $7, $8, $9, TRUE)",
                color.name,
                color.value,
                interaction.user.id,
                role.id,
                channel.id,
                base_join,
                scale_join,
                base_recurring,
                scale_recurring,
            )
            await conn.execute(
                "INSERT INTO gang_members (user_id, gang) VALUES ($1, $2)", interaction.user.id, color.name
            )
            await interaction.followup.send(
                f"Gang created! You now have {remaining} rep remaining.\n"
                f"Your gang's role is {role.mention}, the channel is {channel.mention}.\n"
                f"NOTE: You have been given the manage messages permission for the channel, so you can pin messages and"
                f" delete other's messages if needed. You have to have 2 Factor Authentication enabled to be able to"
                f" use the manage messages permission. You also have the ability to mention everyone in the channel. "
                f"Please restrict this to only pinging your gang's role. Do not abuse these permissions, or we may "
                f"revoke either or both of them and/or replace you with a different member as leader.",
            )
            await self.gang_announcements.send(f"{interaction.user.mention} created a new gang, the {color.name} Gang!")

    @participate.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def join(self, interaction: Interaction[CBot], gang: utils.GANGS):
        """Join a gang.

        Parameters
        ----------
        interaction : Interaction[CBot]
            Interaction object for the current context
        gang : str
            Name of the gang to join
        """
        await interaction.response.defer(ephemeral=True)
        async with interaction.client.pool.acquire() as conn, conn.transaction():
            # check if the gang exists, and if the user has enough rep to join
            res = await join.try_join(cast(asyncpg.Connection, conn), gang, interaction.user.id)
            if isinstance(res, str):
                await interaction.followup.send(res)
                return
            remaining, needed = res
            role = discord.Object(id=await conn.fetchval("SELECT role FROM gangs WHERE name = $1", gang))
            await interaction.user.add_roles(role, reason=f"Joined gang {gang}")
            await conn.execute("INSERT INTO gang_members (user_id, gang) VALUES ($1, $2)", interaction.user.id, gang)
            await conn.execute(
                "UPDATE gangs SET control = control + $1 WHERE name = $2", utils.rep_to_control(needed), gang
            )
            await interaction.followup.send(
                f"You now have {remaining} rep remaining.\nYou have joined the {gang} Gang!"
            )
            channel_id: int = await conn.fetchval("SELECT channel FROM gangs WHERE name = $1", gang)
            channel = cast(
                discord.TextChannel,
                interaction.guild.get_channel(channel_id) or await interaction.guild.fetch_channel(channel_id),
            )
            await channel.send(f"Welcome {interaction.user.mention} to the {gang} Gang!")

    @banner.command()  # pyright: ignore[reportGeneralTypeIssues]
    @app_commands.checks.cooldown(2, 60 * 60 * 24 * 7 * 4, key=lambda i: i.user.id)  # pragma: no branch
    async def request(
        self,
        interaction: Interaction[CBot],
        quote: app_commands.Range[str, 0, 100],
        base: discord.Attachment | None = None,
        color: utils.ColorOpts | None = None,
        gradient: bool = False,
    ) -> None:
        """Request a banner or an edit to an existing banner if an update is rejected, you will need to reapply

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the current context
        quote: str
            The quote to use for the banner
        base: discord.Attachment | None, default None
            The base image to use for the banner, leave empty if you want a gradient or solid color banner
        color: ColorOpts | None, default None
            The color to use for the banner, leave empty if you want a solid gang color banner or image banner
        gradient: bool, default False
            Whether to use a gradient banner or solid color, set to true to gradient with your gangs color
        """
        await interaction.response.defer(ephemeral=True)
        async with interaction.client.pool.acquire() as conn, conn.transaction():
            err = await banner.allowed_banner(cast(asyncpg.Connection, conn), interaction.user.id)
            if err is not None:
                await interaction.followup.send(err)
                return
            valid = banner.check_parameters(base, color, gradient)
            if valid is not None:
                await interaction.followup.send(valid)
                return
            if base is not None:
                res = await banner.download_banner_bg(base, BASE_PATH, interaction.user.id)
                if res is not None:
                    await interaction.followup.send(res)
                    return
                insert_color: int | None = None
                gradient = False
            else:
                if color is None:
                    _color: int = await conn.fetchval(
                        "SELECT color FROM gangs WHERE name = (SELECT gang FROM gang_members WHERE user_id = $1)",
                        interaction.user.id,
                    )
                else:
                    _color = color.value.value
                insert_color: int | None = _color
            await conn.execute(
                "INSERT INTO banners (user_id, quote, color, gradient) VALUES ($1, $2, $3, $4)"
                " ON CONFLICT (user_id) DO UPDATE SET"
                " quote = EXCLUDED.quote, color = EXCLUDED.color, gradient = EXCLUDED.gradient, approved = FALSE",
                interaction.user.id,
                quote,
                insert_color,
                gradient,
            )
            remaining: int = await conn.fetchval(
                "UPDATE users SET points = points - 500 WHERE id = $1 RETURNING points", interaction.user.id
            )
            await interaction.followup.send(f"You now have {remaining} rep remaining.\nYou have requested a banner!")

    @banner.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def status(self, interaction: Interaction[CBot]) -> None:
        """Check the status of your banner request.

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the current context
        """
        await interaction.response.defer(ephemeral=True)
        banner_rec: BannerStatus | None = await interaction.client.pool.fetchrow(
            "SELECT banners.user_id as user_id, quote, banners.color as color, gradient, cooldown, approved,"
            " g.color as gang_color, g.name as name , xu.prestige as prestige "
            "FROM banners JOIN gang_members gm on banners.user_id = gm.user_id JOIN gangs g on g.name = gm.gang"
            " JOIN xp_users xu on banners.user_id = xu.id"
            " WHERE banners.user_id = $1",
            interaction.user.id,
        )
        if banner_rec is None:
            await interaction.followup.send("You don't have a banner_rec, or haven't requested one!")
            return
        if banner_rec["approved"] is False:
            await interaction.followup.send("Your banner_rec is still pending approval!")
            return
        banner_bytes = await generate_banner(banner_rec, interaction.user)
        banner_file = discord.File(banner_bytes, filename="banner.png")
        await interaction.followup.send(
            f"Your banner has been approved and is as follows! Cooldown until: "
            f"{discord.utils.format_dt(banner_rec['cooldown'], 'R')}",
            file=banner_file,
        )

    # noinspection PyShadowingBuiltins
    @user_items.command()  # pyright: ignore[reportGeneralTypeIssues]
    @app_commands.autocomplete(item=user_items_autocomplete)  # type: ignore
    async def view(
        self, interaction: Interaction[CBot], all: bool, owned: bool, item: str | None = None
    ) -> None:  # pragma: no cover
        """View items

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the current context
        all: bool
            Whether to view all items or just one
        owned: bool
            Whether to view it only if you own it or not
        item: str | None, default None
            The item to view, leave empty if you want to view all items
        """
        await interaction.response.defer(ephemeral=True)
        if owned and all:
            ret = await user_items.try_display_inventory(interaction.client.pool, interaction.user.id)
        elif all:
            ret = await user_items.try_display_available_items(interaction.client.pool, interaction.user.id)
        else:
            if item is None:
                await interaction.followup.send("You need to specify an item to view!")
                return
            ret = await user_items.try_display_item(interaction.client.pool, interaction.user.id, item)
        if isinstance(ret, str):
            await interaction.followup.send(ret)
            return
        embed = ret.embeds[0]
        await interaction.followup.send(embed=embed, view=ret)

    @user_items.command()  # pyright: ignore[reportGeneralTypeIssues]
    @app_commands.autocomplete(item=user_items_autocomplete)  # type: ignore
    async def sell(self, interaction: Interaction[CBot], item: str) -> None:  # pragma: no cover
        """Sell an item

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the current context
        item: str
            The item to sell
        """
        await interaction.response.defer(ephemeral=True)
        ret = await user_items.try_sell_item(interaction.client.pool, interaction.user.id, item)
        if isinstance(ret, str):
            await interaction.followup.send(ret)
            return
        await interaction.followup.send(f"You have sold {item} and now have {ret} rep!")

    @user_items.command()  # pyright: ignore[reportGeneralTypeIssues]
    @app_commands.autocomplete(item=user_items_autocomplete)  # type: ignore
    async def use(self, interaction: Interaction[CBot], item: str) -> None:  # pragma: no cover
        """Use an item

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the current context
        item: str
            The item to use
        """
        await interaction.response.defer(ephemeral=True)
        ret = await user_items.try_use_item(interaction.client.pool, interaction.user.id, item)
        if isinstance(ret, str):
            await interaction.followup.send(ret)
            return
        await interaction.followup.send(f"You have used {item} and now have {ret} rep!")

    @user_items.command()  # pyright: ignore[reportGeneralTypeIssues]
    @app_commands.autocomplete(item=user_items_autocomplete)  # type: ignore
    async def gift(self, interaction: Interaction[CBot], item: str, user: discord.Member) -> None:  # pragma: no cover
        """Gift an item

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the current context
        item: str
            The item to gift
        user: discord.Member
            The user to gift it to
        """
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            await user_items.try_gift_item(interaction.client.pool, interaction.user.id, item, user.id)
        )

    # noinspection PyShadowingBuiltins
    @gang_items.command(name="view")  # pyright: ignore[reportGeneralTypeIssues]
    @app_commands.autocomplete(item=gang_items_autocomplete)  # type: ignore
    async def gang_item_view(
        self, interaction: Interaction[CBot], all: bool, owned: bool, item: str | None = None
    ) -> None:  # pragma: no cover
        """View items

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the current context
        all: bool
            Whether to view all items or just one
        owned: bool
            Whether to view it only if you own it or not
        item: str | None, default None
            The item to view, leave empty if you want to view all items
        """
        await interaction.response.defer(ephemeral=True)
        if owned and all:
            ret = await gang_items.try_display_inventory(interaction.client.pool, interaction.user.id)
        elif all:
            ret = await gang_items.try_display_available_items(interaction.client.pool, interaction.user.id)
        else:
            if item is None:
                await interaction.followup.send("You need to specify an item to view!")
                return
            ret = await gang_items.try_display_item(interaction.client.pool, interaction.user.id, item)
        if isinstance(ret, str):
            await interaction.followup.send(ret)
            return
        embed = ret.embeds[0]
        await interaction.followup.send(embed=embed, view=ret)

    @gang_items.command(name="sell")  # pyright: ignore[reportGeneralTypeIssues]
    @app_commands.autocomplete(item=gang_items_autocomplete)  # type: ignore
    async def gang_item_sell(self, interaction: Interaction[CBot], item: str) -> None:  # pragma: no cover
        """Sell an item

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the current context
        item: str
            The item to sell
        """
        await interaction.response.defer(ephemeral=True)
        ret = await gang_items.try_sell_item(interaction.client.pool, interaction.user.id, item)
        if isinstance(ret, str):
            await interaction.followup.send(ret)
            return
        await interaction.followup.send(f"You have sold {item} and your gang now has {ret} control!")

    @gang_items.command(name="use")  # pyright: ignore[reportGeneralTypeIssues]
    @app_commands.autocomplete(item=gang_items_autocomplete)  # type: ignore
    async def gang_item_use(self, interaction: Interaction[CBot], item: str) -> None:  # pragma: no cover
        """Use an item

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the current context
        item: str
            The item to use
        """
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            await gang_items.try_use_item(interaction.client.pool, interaction.user.id, item)
        )

    @commands.command(name="approve", hidden=True)
    @commands.guild_only()
    async def approve_cmd(self, ctx: commands.Context[CBot]):
        """Approve a banner request"""
        member = cast(discord.Member, ctx.author)
        if not member.guild_permissions.manage_roles:
            return
        banner_rec: BannerStatus | None = await ctx.bot.pool.fetchrow(
            "SELECT banners.user_id as user_id, quote, banners.color as color, gradient, cooldown, approved,"
            " g.color as gang_color, g.name as name, xu.prestige as prestige "
            "FROM banners JOIN gang_members gm on banners.user_id = gm.user_id JOIN gangs g on g.name = gm.gang"
            " JOIN xp_users xu on banners.user_id = xu.id"
            " WHERE approved = FALSE ORDER BY cooldown LIMIT 1",
            member.id,
        )
        if banner_rec is None:
            await ctx.reply("There are currently no banner awaiting approval!")
            return
        guild = cast(discord.Guild, ctx.guild)
        requester = guild.get_member(banner_rec["user_id"]) or await guild.fetch_member(banner_rec["user_id"])
        banner_bytes = await generate_banner(banner_rec, requester)
        await ctx.reply(
            "Approve, deny, or cancel?",
            file=discord.File(banner_bytes, filename="banner.png"),
            view=ApprovalView(banner_rec, member.id),
        )
        banner_bytes.close()

    @commands.command(name="shakedown", hidden=True)
    @commands.guild_only()
    async def trigger_shakedown(self, ctx: commands.Context[CBot]):
        """Trigger a shakedown"""
        member = cast(discord.Member, ctx.author)
        if not member.guild_permissions.manage_roles:
            return
        res = await do_shakedown(ctx.bot.pool, force=True)
        await self.gang_announcements.send(f"Today's shakedown found {res} items!")
        await ctx.reply(f"Today's shakedown found {res} items!")

    @tasks.loop(time=datetime.time(0, tzinfo=ZoneInfo("America/New_York")))
    async def auto_shakedown(self):  # pragma: no cover
        """Auto shakedown"""
        if datetime.datetime.now().day % 3 == 0:
            res = await do_shakedown(self.bot.pool)
            await self.gang_announcements.send(f"Today's shakedown found {res} items!")
