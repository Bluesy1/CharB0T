# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Collection of functions for creating a gang."""
from __future__ import annotations

import asyncpg
import discord

from .. import utils

__all__ = ("create_gang_discord_objects", "check_gang_conditions")


async def check_gang_conditions(
    conn: asyncpg.Connection, user: int, color: utils.ColorOpts, base_join: int, base_recurring: int
) -> str | int:
    """Check if a user can create a gang, and charge them if they can.

    Parameters
    ----------
    conn : asyncpg.Connection
        The database connection.
    user : int
        The user id to check.
    color : ColorOpts
        The color to use for the gang.
    base_join : int
        The base cost to join a gang, as set by the user.
    base_recurring : int
        The base cost to stay in a gang, as set by the user.
    """
    if await conn.fetchval("SELECT 1 FROM gangs WHERE name = $1", color.name):
        return "A gang with that name/color already exists!"
    pts: int | None = await conn.fetchval("SELECT points FROM users WHERE id = $1", user)
    if pts is None:
        return "You have never gained any points, try gaining some first!"
    if pts < (base_join + base_recurring + utils.BASE_GANG_COST):
        return (
            f"You don't have enough rep to create a gang! You need at least "
            f"{base_join + base_recurring + utils.BASE_GANG_COST} rep to create a gang. ("
            f"{utils.BASE_GANG_COST} combined with the baseline join and recurring costs are"
            f" required to form a gang)"
        )

    return await conn.fetchval(
        "UPDATE users SET points = points - $1 WHERE id = $2 RETURNING points",
        base_join + base_recurring + utils.BASE_GANG_COST,
        user,
    )


async def create_gang_discord_objects(
    guild: discord.Guild, user: discord.Member, category: discord.CategoryChannel, color: utils.ColorOpts
) -> tuple[discord.Role, discord.TextChannel]:
    """Create the discord objects for a gang.

    Parameters
    ----------
    guild : discord.Guild
        The guild to create the objects in.
    user : discord.Member
        The user to create the objects for.
    category : discord.CategoryChannel
        The category to create the channel in.
    color : ColorOpts
        The color to use for the role.
    """
    role = await guild.create_role(
        name=f"{color.name} Gang",
        color=color.value,
        reason=f"New gang created by {user} - id: {user.id}",
    )
    overwrites = {
        user: discord.PermissionOverwrite(manage_messages=True, mention_everyone=True),
        role: discord.PermissionOverwrite(view_channel=True, embed_links=True),
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
    }
    channel = await guild.create_text_channel(f"{color.name.lower()}-gang", category=category, overwrites=overwrites)
    await user.add_roles(role, reason=f"New gang created by {user}")
    return role, channel


async def create_gang(
    conn: asyncpg.Connection,
    user: discord.Member,
    category: discord.CategoryChannel,
    color: utils.ColorOpts,
    join_base: int,
    recurring_base: int,
    join_scale: int,
    recurring_scale: int,
) -> str | tuple[int, discord.TextChannel, discord.Role]:
    """Create a new gang.

    Parameters
    ----------
    conn : asyncpg.Connection
        Connection to the database
    user : discord.Member
        Member who is creating the gang
    category: discord.CategoryChannel
        Category to create the gang channel in
    color : utils.ColorOpts
        Color of the gang, which forms the color and name of the gang
    join_base : int
        Base join cost
    recurring_base : int
        Base recurring cost
    join_scale : int
        Scale of join cost, to go up per for each member in the gang
    recurring_scale : int
        Scale of recurring cost, to go up per for each member in the gang

    Returns
    -------
    str | tuple[int, discord.TextChannel, discord.Role]
        If the gang already exists, the user is already in a gang, or the user doesn't have enough points, a string
    """
    remaining = await check_gang_conditions(conn, user.id, color, join_base, recurring_base)
    if isinstance(remaining, str):
        return remaining
    role, channel = await create_gang_discord_objects(user.guild, user, category, color)
    await user.add_roles(role, reason=f"New gang created by {user}")
    # All gangs start with 100 control.
    await conn.execute(
        "INSERT INTO gangs (name, color, leader, role, channel, control, join_base, join_slope,"
        " upkeep_base, upkeep_slope, all_paid) VALUES ($1, $2, $3, $4, $5, 100, $6, $7, $8, $9, TRUE)",
        color.name,
        color.value,
        user.id,
        role.id,
        channel.id,
        join_base,
        join_scale,
        recurring_base,
        recurring_scale,
    )
    await conn.execute("INSERT INTO gang_members (user_id, gang) VALUES ($1, $2)", user.id, color.name)
    return remaining, channel, role
