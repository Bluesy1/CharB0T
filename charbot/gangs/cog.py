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
"""Gang war cog file."""
import asyncio
import datetime
from typing import cast
from zoneinfo import ZoneInfo

import asyncpg
import discord
from discord import app_commands, ui, utils
from discord.ext import commands

from . import ColorOpts, DuesButton, SQL_MONTHLY, GANGS
from .. import GuildInteraction as Interaction, CBot


class Gangs(commands.Cog):
    """Gang war."""

    gang_guild: discord.Guild
    gang_category: discord.CategoryChannel
    gang_announcements: discord.TextChannel

    def __init__(self, bot: CBot):
        self.bot = bot
        self._baseline_gang_cost = 100
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

    async def start_dues_cycle(self):
        """Start the dues cycle."""
        next_month = (
            datetime.datetime.now(tz=ZoneInfo("US/Michigan")).replace(day=1) + datetime.timedelta(days=32)
        ).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        await utils.sleep_until(next_month)
        conn: asyncpg.Connection
        async with self.bot.pool.acquire() as conn, conn.transaction():
            await conn.execute(SQL_MONTHLY)
            gangs: list[asyncpg.Record] = await conn.fetch(
                "SELECT name, channel_id, role_id,"
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
                    view.dues_button = DuesButton(row["name"])
                    view.add_item(view.dues_button)
                    until = next_month + datetime.timedelta(days=7)
                    msg = await channel.send(
                        f"<@&{row['role_id']}> At least one member of this gang did not have enough rep to "
                        f"automatically pay their dues. Please check if this is you, and if it is, pay with the"
                        f" button below after gaining enough rep to pay, you have until {utils.format_dt(until, 'F')},"
                        f" {utils.format_dt(until, 'R')}",
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
        await utils.sleep_until(next_month)
        conn: asyncpg.Connection
        async with self.bot.pool.acquire() as conn, conn.transaction():
            gangs: list[asyncpg.Record] = await conn.fetch(
                "SELECT name, channel_id, role_id,"
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
                    f" haven't have been temporatially removed from the gang, but may rejoin. {leader_removed} Thank "
                    f"you for participating in the gang war!"
                )
                await conn.execute("DELETE FROM gang_members WHERE gang = $1 AND paid IS FALSE", row["name"])
            empty_gangs = await conn.fetch(
                "SELECT name FROM gangs WHERE 0 == (SELECT COUNT(*) FROM gang_members WHERE gang = gangs.name)"
            )
            if lost_members > 0:
                await self.gang_announcements.send(
                    f"{lost_members} member(s) of the gangs have been removed from thier gangs for not paying their "
                    f"dues. If you were one of the member(s) removed, remember you can always rejoin a gang if you have"
                    f" enough rep! Thank you for participating in the gang war! {len(empty_gangs)} ran out of members"
                    f" and got disbanded temporarily."
                )
            await conn.execute("DELETE FROM gangs WHERE name in $1", [row["name"] for row in empty_gangs])

    @participate.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def create(
        self,
        interaction: Interaction[CBot],
        color: ColorOpts,
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
        conn: asyncpg.Connection
        name = ColorOpts(color).name
        async with interaction.client.pool.acquire() as conn, conn.transaction():
            # Check if teh gang already exists, the user is already in a gang, or the user doesn't have enough points
            if await conn.fetchval("SELECT 1 FROM gangs WHERE name = $1", name):
                await interaction.followup.send("A gang with that name/color already exists!")
                return
            pts: int | None = await conn.fetchval("SELECT points FROM users WHERE id = $1", interaction.user.id)
            if pts is None:
                await interaction.followup.send("You have never gained any points, try gaining some first!")
                return
            if pts < (base_join + base_recurring + self._baseline_gang_cost):
                await interaction.followup.send(
                    f"You don't have enough rep to create a gang! You need at least "
                    f"{base_join + base_recurring + self._baseline_gang_cost} rep to create a gang. ("
                    f"{self._baseline_gang_cost} combined with the baseline join and recurring costs are"
                    f" required to form a gang)"
                )
                return
            remaining: int = await conn.fetchval(
                "UPDATE users SET points = points - $1 WHERE id = $2 RETURNING points",
                base_join + base_recurring + self._baseline_gang_cost,
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
            control = 100  # TODO: do a proper impl for control
            await conn.execute(
                "INSERT INTO gangs ("
                "name, color, leader_id, role_id, channel_id, control, join_base, join_slope, upkeep_base, upkeep_slope"
                ", all_paid) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, TRUE)",
                name,
                color.value,
                interaction.user.id,
                role.id,
                channel.id,
                control,
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
                f"Please restict this to only pinging your gang's role. Do not abuse these permissions, or we may "
                f"revoke either or both of them and/or replace you with a different member as leader.",
            )
            await self.gang_announcements.send(f"{interaction.user.mention} created a new gang, the {name} Gang!")

    @participate.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def join(self, interaction: Interaction[CBot], gang: GANGS):
        """Join a gang.

        Parameters
        ----------
        interaction : Interaction[CBot]
            Interaction object for the current context
        gang : str
            Name of the gang to join
        """
        await interaction.response.defer(ephemeral=True)
        conn: asyncpg.Connection
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
            role = discord.Object(id=await conn.fetchval("SELECT role_id FROM gangs WHERE name = $1", gang))
            channel_id: int = await conn.fetchval("SELECT channel_id FROM gangs WHERE name = $1", gang)
            channel = cast(
                discord.TextChannel,
                interaction.guild.get_channel(channel_id) or await interaction.guild.fetch_channel(channel_id),
            )
            await interaction.user.add_roles(role, reason=f"Joined gang {gang}")
            await conn.execute("INSERT INTO gang_members (user_id, gang) VALUES ($1, $2)", interaction.user.id, gang)
            await conn.execute(
                "UPDATE gangs SET control = control + $1 WHERE name = $2", needed / 50, gang
            )  # TODO: do a proper impl for control conversion
            await interaction.followup.send(
                f"You now have {remaining} rep remaining.\nYou have joined the {gang} Gang!"
            )
            await channel.send(f"Welcome {interaction.user.mention} to the {gang} Gang!")
