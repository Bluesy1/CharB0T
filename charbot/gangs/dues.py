# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Gang war."""
from __future__ import annotations

import datetime
from typing import cast

import asyncpg

import discord
from discord import ui

from .types import GangDues
from .. import GuildComponentInteraction as CInteraction, CBot
from . import GANGS, utils


class DuesButton(ui.Button):
    """Dues button."""

    def __init__(self, gang: GANGS) -> None:
        """Init."""
        super().__init__(style=discord.ButtonStyle.success, custom_id=f"dues_{gang}", label="Pay", emoji="\U0001F4B0")
        self.gang = gang

    async def callback(self, interaction: CInteraction[CBot]):
        """Buttons callback."""
        await interaction.response.defer(ephemeral=True)
        conn: asyncpg.pool.PoolConnectionProxy
        async with interaction.client.pool.acquire() as conn, conn.transaction():
            paid: bool = await conn.fetchval("SELECT paid FROM gang_members WHERE user_id = $1", interaction.user.id)
            if paid:
                await interaction.followup.send("You have already paid your dues for this month.")
                return
            if not await conn.fetchval(
                "SELECT CASE"
                " WHEN (SELECT points FROM users WHERE id = $1) >= (SELECT upkeep_base + (upkeep_slope * ("
                "SELECT COUNT(*) FROM gang_members WHERE gang = $2)) FROM gangs WHERE name = $2)"
                " THEN TRUE ELSE FALSE END",
                interaction.user.id,
                self.gang,
            ):
                details = cast(
                    asyncpg.Record,
                    await conn.fetchrow(
                        "SELECT "
                        "(SELECT upkeep_base + (upkeep_slope * (SELECT COUNT(*) FROM gang_members WHERE gang = $1))"
                        " FROM gangs WHERE name = $1) AS upkeep,"
                        " (SELECT points FROM users WHERE id = $2) AS points",
                        self.gang,
                        interaction.user.id,
                    ),
                )
                await interaction.followup.send(
                    f"You do not have enough rep to pay your dues, you have {details['points']} rep and need "
                    f"{details['upkeep']:.0f} rep to pay your dues."
                )
                return
            remaining: int = await conn.fetchval(
                "UPDATE users SET points = points - ("
                "SELECT upkeep_base + (upkeep_slope * (SELECT COUNT(*) FROM gang_members WHERE gang = $1))"
                " FROM gangs WHERE name = $1) WHERE id = $2 RETURNING points",
                self.gang,
                interaction.user.id,
            )
            await conn.execute("UPDATE gang_members SET paid = TRUE WHERE user_id = $1", interaction.user.id)
            await conn.execute(
                "UPDATE gangs SET control = control + $2 WHERE name = $1",
                self.gang,
                utils.rep_to_control(
                    await conn.fetchval(
                        "SELECT "
                        "(SELECT upkeep_base + (upkeep_slope * (SELECT COUNT(*) FROM gang_members WHERE gang = $1)) "
                        "FROM gangs WHERE name = $1) AS upkeep",
                        self.gang,
                    )
                ),
            )
            await interaction.followup.send(
                f"You have paid your dues for {self.gang} Gang! You now have {remaining} rep remaining."
            )


async def send_dues_start(guild: discord.Guild, month: datetime.datetime, gang: GangDues):
    """Send the initial dues message for a gang

    Parameters
    ----------
    guild: discord.Guild
        The guild to send the message in
    month: datetime.datetime
        The month the dues are for
    gang: GangDues
        The gang to send the dues for
    """
    channel = cast(
        discord.TextChannel,
        guild.get_channel(gang["channel"]) or await guild.fetch_channel(gang["channel"]),
    )
    if not gang["complete"]:
        view = ui.View(timeout=60 * 60 * 24 * 7)
        view.dues_button = DuesButton(gang["name"])  # type: ignore
        view.add_item(view.dues_button)  # type: ignore
        until = month + datetime.timedelta(days=7)
        msg = await channel.send(
            f"<@&{gang['role']}> At least one member of this gang did not have enough rep to "
            f"automatically pay their dues. Please check if this is you, and if it is, pay with the"
            f" button below after gaining enough rep to pay, you have until "
            f"{discord.utils.format_dt(until, 'F')}, {discord.utils.format_dt(until, 'R')}",
            view=view,
        )
        await msg.pin(reason="So it doesn't get lost too quickly")
    else:
        await channel.send(
            f"<@&{gang['role']}> All members of this gang have paid their dues automatically."
            f" Thank you for participating in the gang war!"
        )


async def send_dues_end(conn: asyncpg.Connection, guild: discord.Guild, gang: GangDues) -> int:
    """Send the end of the dues period message for a gang

    Parameters
    ----------
    conn: asyncpg.Connection
        The database connection to use
    guild: discord.Guild
        The guild to send the message in
    gang: GangDues
        The gang to send the dues for

    Returns
    -------
    int
        The number of members who did not pay their dues
    """
    channel = cast(
        discord.TextChannel, guild.get_channel(gang["channel"]) or await guild.fetch_channel(gang["channel"])
    )
    if gang["complete"]:
        await channel.send(
            f"<@&{gang['role']}> All members of this gang have paid their dues. Thank you for "
            f"participating in the gang war!"
        )
        return 0
    _members: list[asyncpg.Record] = await conn.fetch(
        "SELECT user_id, leader as id FROM gang_members WHERE gang = $1 AND paid IS FALSE", gang["name"]
    )
    members: list[discord.Member] = []
    leader_removed = ""
    for _member in _members:
        member = cast(discord.Member, guild.get_member(_member["id"]) or await guild.fetch_member(_member["id"]))
        await member.remove_roles(discord.Object(id=gang["role"]), reason="Gang dues not paid.")
        members.append(member)
        if _member["leader"]:
            leader_removed = (
                "NOTE: Your leader did not pay their dues and has been demoted/removed and an election will"
                " be held shortly to replace them. <@363095569515806722>"
            )
    await channel.send(
        f"<@&{gang['role']}> All but {len(members)} members of this gang have paid their dues. Those who"
        f" haven't have been temporarily removed from the gang, but may rejoin. {leader_removed} Thank "
        f"you for participating in the gang war!"
    )
    await conn.execute("DELETE FROM gang_members WHERE gang = $1 AND paid IS FALSE", gang["name"])
    return len(members)
