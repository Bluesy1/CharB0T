# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Gang war cog file."""
import asyncio
import datetime
from io import BytesIO
from pathlib import Path
from typing import Final, cast
from zoneinfo import ZoneInfo

import asyncpg
import discord
from PIL import Image
from discord import app_commands, ui
from discord.ext import commands, tasks

from . import DuesButton
from . import utils
from .banner import ApprovalView, generate_banner
from ._types import BannerRequestLeader, BannerStatus, BannerStatusPoints
from .shakedowns import do_shakedown
from .. import GuildInteraction as Interaction, CBot


BASE_PATH: Final[Path] = Path(__file__).parent / "user_assets"


class Gangs(commands.Cog):
    """Gang war."""

    gang_guild: discord.Guild
    gang_category: discord.CategoryChannel
    gang_announcements: discord.TextChannel

    __slots__ = (
        "bot",
        "_start_dues_cycle_task",
        "_end_dues_cycle_task",
    )

    def __init__(self, bot: CBot):
        self.bot = bot
        self._start_dues_cycle_task = asyncio.create_task(self.start_dues_cycle())
        self._end_dues_cycle_task = asyncio.create_task(self.end_dues_cycle())
        raise NotImplementedError("Gangs are not implemented yet.")

    async def cog_unload(self) -> None:
        """Unload."""
        self._start_dues_cycle_task.cancel()
        self._end_dues_cycle_task.cancel()

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

    async def start_dues_cycle(self):
        """Start the dues cycle."""
        next_month = (
            datetime.datetime.now(tz=ZoneInfo("US/Michigan")).replace(day=1) + datetime.timedelta(days=32)
        ).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        await discord.utils.sleep_until(next_month)
        conn: asyncpg.pool.PoolConnectionProxy
        async with self.bot.pool.acquire() as conn, conn.transaction():
            await conn.execute(utils.SQL_MONTHLY)
            gangs: list[asyncpg.Record] = await conn.fetch(
                "SELECT name, channel, role,"
                " (TRUE = ALL(SELECT paid FROM gang_members WHERE gang = gangs.name)) as complete FROM gangs"
            )
            for row in gangs:
                channel = cast(
                    discord.TextChannel,
                    self.gang_guild.get_channel(row["channel_id"])
                    or await self.gang_guild.fetch_channel(row["channel_id"]),
                )
                if not row["complete"]:
                    view = ui.View(timeout=60 * 60 * 24 * 7)
                    view.dues_button = DuesButton(row["name"])  # type: ignore
                    view.add_item(view.dues_button)  # type: ignore
                    until = next_month + datetime.timedelta(days=7)
                    msg = await channel.send(
                        f"<@&{row['role_id']}> At least one member of this gang did not have enough rep to "
                        f"automatically pay their dues. Please check if this is you, and if it is, pay with the"
                        f" button below after gaining enough rep to pay, you have until "
                        f"{discord.utils.format_dt(until, 'F')}, {discord.utils.format_dt(until, 'R')}",
                        view=view,
                    )
                    await msg.pin(reason="So it doesn't get lost too quickly")
                else:
                    await channel.send(
                        f"<@&{row['role_id']}> All members of this gang have paid their dues automatically."
                        f" Thank you for participating in the gang war!"
                    )
        self._start_dues_cycle_task = asyncio.create_task(self.start_dues_cycle())

    async def end_dues_cycle(self):
        """End the dues cycle."""
        next_month = (
            datetime.datetime.now(tz=ZoneInfo("US/Michigan")).replace(day=1) + datetime.timedelta(days=32)
        ).replace(day=8, hour=0, minute=0, second=0, microsecond=0)
        await discord.utils.sleep_until(next_month)
        conn: asyncpg.pool.PoolConnectionProxy
        async with self.bot.pool.acquire() as conn, conn.transaction():
            gangs: list[asyncpg.Record] = await conn.fetch(
                "SELECT name, channel, role,"
                " (TRUE = ALL(SELECT paid FROM gang_members WHERE gang = gangs.name)) as complete"
                " FROM gangs WHERE all_paid IS FALSE"
            )
            lost_members = 0
            for row in gangs:
                channel = cast(
                    discord.TextChannel,
                    self.gang_guild.get_channel(row["channel_id"])
                    or await self.gang_guild.fetch_channel(row["channel_id"]),
                )
                if row["complete"]:
                    await channel.send(
                        f"<@&{row['role_id']}> All members of this gang have paid their dues. Thank you for "
                        f"participating in the gang war!"
                    )
                    continue
                _members: list[asyncpg.Record] = await conn.fetch(
                    "SELECT user_id, leader as id FROM gang_members WHERE gang = $1 AND paid IS FALSE", row["name"]
                )
                members: list[discord.Member] = []
                lost_members += len(_members)
                leader_removed = ""
                for _member in _members:
                    member = cast(
                        discord.Member,
                        self.gang_guild.get_member(_member["id"]) or await self.gang_guild.fetch_member(_member["id"]),
                    )
                    await member.remove_roles(discord.Object(id=row["role_id"]), reason="Gang dues not paid.")
                    members.append(member)
                    if _member["leader"]:
                        leader_removed = (
                            "NOTE: Your leader did not pay their dues and has been demoted/removed and an election will"
                            " be held shortly to replace them. <@363095569515806722>"
                        )
                await channel.send(
                    f"<@&{row['role_id']}> All but {len(members)} members of this gang have paid their dues. Those who"
                    f" haven't have been temporarily removed from the gang, but may rejoin. {leader_removed} Thank "
                    f"you for participating in the gang war!"
                )
                await conn.execute("DELETE FROM gang_members WHERE gang = $1 AND paid IS FALSE", row["name"])
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
            async with self.bot.pool.acquire() as conn:
                banner_rec: BannerStatusPoints | None = await conn.fetchrow(
                    "SELECT banners.user_id as user_id, quote, banners.color as color, gradient, cooldown, approved,"
                    " g.color as gang_color, g.name as name, u.points as POINTS FROM banners JOIN gang_members gm ON"
                    " banners.user_id = gm.user_id JOIN gangs g on g.name = gm.gang JOIN users u on g.leader = u.id"
                    " WHERE banners.user_id = $1",
                    member.id,
                )
                if (
                    banner_rec is not None
                    and banner_rec["cooldown"] < discord.utils.utcnow()
                    and banner_rec["approved"]
                    and banner_rec["points"] > 50
                ):
                    banner_bytes = await generate_banner(banner_rec, member)
                    banner_file = discord.File(banner_bytes, filename="banner.png")
                    await message.reply(file=banner_file)
                    await conn.execute(
                        "UPDATE banners SET cooldown = $1 WHERE user_id = $2",
                        discord.utils.utcnow() + datetime.timedelta(days=7),
                        member.id,
                    )
                    await conn.execute("UPDATE users SET points = points - 50 WHERE id = $1", member.id)

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
        name = utils.ColorOpts(color).name
        conn: asyncpg.pool.PoolConnectionProxy
        async with interaction.client.pool.acquire() as conn, conn.transaction():
            # Check if teh gang already exists, the user is already in a gang, or the user doesn't have enough points
            if await conn.fetchval("SELECT 1 FROM gangs WHERE name = $1", name):
                await interaction.followup.send("A gang with that name/color already exists!")
                return
            pts: int | None = await conn.fetchval("SELECT points FROM users WHERE id = $1", interaction.user.id)
            if pts is None:
                await interaction.followup.send("You have never gained any points, try gaining some first!")
                return
            if pts < (base_join + base_recurring + utils.BASE_GANG_COST):
                await interaction.followup.send(
                    f"You don't have enough rep to create a gang! You need at least "
                    f"{base_join + base_recurring + utils.BASE_GANG_COST} rep to create a gang. ("
                    f"{utils.BASE_GANG_COST} combined with the baseline join and recurring costs are"
                    f" required to form a gang)"
                )
                return
            remaining: int = await conn.fetchval(
                "UPDATE users SET points = points - $1 WHERE id = $2 RETURNING points",
                base_join + base_recurring + utils.BASE_GANG_COST,
                interaction.user.id,
            )

            role = await interaction.guild.create_role(
                name=f"{name} Gang",
                color=color.value,  # pycharm still thinks this isn't a property so is complaining about it incorrectly
                reason=f"New gang created by {interaction.user} - id: {interaction.user.id}",
            )
            overwrites = {
                interaction.user: discord.PermissionOverwrite(manage_messages=True, mention_everyone=True),
                role: discord.PermissionOverwrite(view_channel=True, embed_links=True),
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            }
            channel = await interaction.guild.create_text_channel(
                f"{name} Gang", category=self.gang_category, overwrites=overwrites
            )
            await interaction.user.add_roles(role, reason=f"New gang created by {interaction.user}")
            # All gangs start with 100 control.
            await conn.execute(
                "INSERT INTO gangs (name, color, leader, role, channel, control, join_base, join_slope,"
                " upkeep_base, upkeep_slope, all_paid) VALUES ($1, $2, $3, $4, $5, 100, $6, $7, $8, $9, TRUE)",
                name,
                color.value,
                interaction.user.id,
                role.id,
                channel.id,
                base_join,
                scale_join,
                base_recurring,
                scale_recurring,
            )
            await conn.execute("INSERT INTO gang_members (user_id, gang) VALUES ($1, $2)", interaction.user.id, name)
            await interaction.followup.send(
                f"Gang created! You now have {remaining} rep remaining.\n"
                f"Your gang's role is {role.mention}, the channel is {channel.mention}.\n"
                f"NOTE: You have been given the manage messages permission for the channel, so you can pin messages and"
                f" delete other's messages if needed. You have to have 2 Factor Authentication enabled to be able to"
                f" use the manage messages permission. You also have the ability to mention everyone in the channel. "
                f"Please restrict this to only pinging your gang's role. Do not abuse these permissions, or we may "
                f"revoke either or both of them and/or replace you with a different member as leader.",
            )
            await self.gang_announcements.send(f"{interaction.user.mention} created a new gang, the {name} Gang!")

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
        conn: asyncpg.pool.PoolConnectionProxy
        async with interaction.client.pool.acquire() as conn, conn.transaction():
            # check if the gang exists, and if the user has enough rep to join
            if not await conn.fetchval("SELECT 1 FROM gangs WHERE name = $1", gang):
                await interaction.followup.send("That gang doesn't exist!")
                return
            pts: int | None = await conn.fetchval("SELECT points FROM users WHERE id = $1", interaction.user.id)
            if pts is None:
                await interaction.followup.send("You have never gained any points, try gaining some first!")
                return
            needed: int = await conn.fetchval(
                "SELECT join_base + (join_slope * (SELECT COUNT(*) FROM gang_members WHERE gang = $1))"
                " FROM gangs WHERE name = $1",
                gang,
            )
            if needed > pts:
                await interaction.followup.send(
                    f"You don't have enough rep to join that gang! You need at least {needed} rep to join that gang,"
                    f" and you have {pts}."
                )
                return
            remaining: int = await conn.fetchval(
                "UPDATE users SET points = points - $1 WHERE id = $2 RETURNING points", needed, interaction.user.id
            )
            role = discord.Object(id=await conn.fetchval("SELECT role FROM gangs WHERE name = $1", gang))
            channel_id: int = await conn.fetchval("SELECT channel FROM gangs WHERE name = $1", gang)
            channel = cast(
                discord.TextChannel,
                interaction.guild.get_channel(channel_id) or await interaction.guild.fetch_channel(channel_id),
            )
            await interaction.user.add_roles(role, reason=f"Joined gang {gang}")
            await conn.execute("INSERT INTO gang_members (user_id, gang) VALUES ($1, $2)", interaction.user.id, gang)
            await conn.execute(
                "UPDATE gangs SET control = control + $1 WHERE name = $2", utils.rep_to_control(needed), gang
            )
            await interaction.followup.send(
                f"You now have {remaining} rep remaining.\nYou have joined the {gang} Gang!"
            )
            await channel.send(f"Welcome {interaction.user.mention} to the {gang} Gang!")

    @banner.command()  # pyright: ignore[reportGeneralTypeIssues]
    @app_commands.checks.cooldown(2, 60 * 60 * 24 * 7 * 4, key=lambda i: i.user.id)
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
        conn: asyncpg.pool.PoolConnectionProxy
        async with interaction.client.pool.acquire() as conn, conn.transaction():
            leader: BannerRequestLeader | None = await conn.fetchrow(
                "SELECT leader, leadership, u.points AS points "
                "FROM gang_members JOIN users u on u.id = gang_members.user_id WHERE user_id = $1",
                interaction.user.id,
            )
            if leader is None:
                await interaction.followup.send("You are not in a gang!")
                return
            if leader["leader"] is False and leader["leadership"] is False:
                await interaction.followup.send("You are not the leadership of your gang!")
                return
            if leader["points"] < 500:
                await interaction.followup.send(
                    f"You don't have enough rep to request a banner! (Have: {leader['points']}, Need: 500)"
                )
                return
            if base is None and color is None:
                await interaction.followup.send("You need to specify a base image or color!")
                return
            if base is not None and color is not None:
                await interaction.followup.send("You can't specify both a base image and a color!")
                return
            if base is not None:
                if content_type := base.content_type:
                    if content_type not in ("image/png", "image/jpeg"):
                        await interaction.followup.send("The base image must be a PNG or JPEG!")
                        return
                try:

                    def sync_code(img: bytes, path: Path):
                        """Blocking code to run in an executor"""
                        image = Image.open(BytesIO(img))
                        image.save(path, format="PNG")

                    await asyncio.to_thread(
                        sync_code,
                        await base.read(),
                        BASE_PATH / f"{interaction.user.id}.png",
                    )
                except (discord.DiscordException, OSError, ValueError, TypeError):
                    await interaction.followup.send("Failed to grab image, try again.")
                    return
                insert_color: int | None = None
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
        conn: asyncpg.Connection
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
