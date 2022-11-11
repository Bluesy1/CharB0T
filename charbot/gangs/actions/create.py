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
    conn: asyncpg.Connection, user: discord.Member, color: utils.ColorOpts, base_join: int, base_recurring: int
) -> str | int:
    """Check if a user can create a gang, and charge them if they can.

    Parameters
    ----------
    conn : asyncpg.Connection
        The database connection.
    user : discord.Member
        The user to check.
    color : ColorOpts
        The color to use for the gang.
    base_join : int
        The base cost to join a gang, as set by the user.
    base_recurring : int
        The base cost to stay in a gang, as set by the user.
    """
    if await conn.fetchval("SELECT 1 FROM gangs WHERE name = $1", color.name):
        return "A gang with that name/color already exists!"
    pts: int | None = await conn.fetchval("SELECT points FROM users WHERE id = $1", user.id)
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
        user.id,
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
    channel = await guild.create_text_channel(f"{color.name} Gang", category=category, overwrites=overwrites)
    await user.add_roles(role, reason=f"New gang created by {user}")
    return role, channel
