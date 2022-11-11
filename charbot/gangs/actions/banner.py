# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Collection of functions for requesting a banner."""
from __future__ import annotations

import asyncio
from io import BytesIO
from pathlib import Path

import asyncpg
import discord
from PIL import Image

from charbot.gangs.types import BannerRequestLeader
from charbot.gangs.utils import ColorOpts


__all__ = ("allowed_banner", "download_banner_bg", "check_parameters")


async def allowed_banner(conn: asyncpg.Connection, user: int) -> str | None:
    """Check if a user is allowed to request a banner.

    Parameters
    ----------
    conn : asyncpg.Connection
        The database connection.
    user : int
        The ID of the user to check.

    Returns
    -------
    str | None
        The error message, or None if the user is allowed to request a banner.
    """
    leader: BannerRequestLeader | None = await conn.fetchrow(
        "SELECT leader, leadership, u.points AS points "
        "FROM gang_members JOIN users u on u.id = gang_members.user_id WHERE user_id = $1",
        user,
    )
    if leader is None:
        return "You are not in a gang!"
    if leader["leader"] is False and leader["leadership"] is False:
        return "You are not the leadership of your gang!"
    if leader["points"] < 500:
        return f"You don't have enough rep to request a banner! (Have: {leader['points']}, Need: 500)"
    return None


async def download_banner_bg(base: discord.Attachment, base_path: Path, user: int) -> str | None:
    """Download the banner background image.

    Parameters
    ----------
    base : discord.Attachment
        The attachment to download.
    base_path : Path
        The base path to save the image to, to be extended by the user id.
    user : int
        The ID of the user who requested the banner.
    """
    if content_type := base.content_type:  # pragma: no branch
        if content_type not in ("image/png", "image/jpeg"):
            return "The base image must be a PNG or JPEG!"
    try:
        await asyncio.to_thread(  # pragma: no branch
            lambda img: Image.open(BytesIO(img)).save(base_path / f"{user}.png", format="PNG"), await base.read()
        )
    except (discord.DiscordException, OSError, ValueError, TypeError):
        return "Failed to grab image, try again."
    return None


def check_parameters(base: discord.Attachment | None, color: ColorOpts | None, gradient: bool) -> str | None:
    """Check if the parameters are valid.

    Parameters
    ----------
    base : discord.Attachment | None
        The base image to use for the banner.
    color : ColorOpts | None
        The color to use for the banner.
    gradient : bool
        Whether to use a gradient.

    Returns
    -------
    str | None
        The error message, or None if the parameters are valid.
    """
    if base is None and gradient is True and color is None:
        return "You need to specify a base image, or if you want a gradient, you must specify the second color!"
    if base is not None and color is not None:
        return "You can't specify both a base image and a color!"
    return None
