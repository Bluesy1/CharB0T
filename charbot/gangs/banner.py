# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Gang banner code."""
from __future__ import annotations

import asyncio
import datetime
from collections.abc import Iterable
from io import BytesIO
from pathlib import Path
from textwrap import fill
from typing import Final

import asyncpg
import discord
from discord import Color, Interaction, ui
from PIL import Image, ImageDraw, ImageFont

from .types import BannerStatus, BannerStatusPoints
from .. import CBot


FONT: Final = ImageFont.truetype(str(Path(__file__).parent.parent / "media/pools/font.ttf"), 30)
FONT_QUOTE: Final = ImageFont.truetype(str(Path(__file__).parent.parent / "media/pools/font.ttf"), 25)
BASE_PATH: Final[Path] = Path(__file__).parent / "user_assets"
STAR_COLOR: Final[tuple[int, int, int]] = (69, 79, 191)


def interpolate(f_co: tuple[int, int, int], t_co: tuple[int, int, int], interval: int) -> Iterable[list[int]]:
    """Interpolate between two colors to create a gradient.

    Parameters
    ----------
    f_co : tuple[int, int, int]
        The first color as a tuple of 0 to 255 ints as an RGB tuple.
    t_co : tuple[int, int, int]
        The second color as a tuple of 0 to 255 ints as an RGB tuple.
    interval : int
        The number of steps to interpolate between the two colors.

    Yields
    ------
    list[int]
        The next color as a list of 0 to 255 ints as an RGB tuple.

    Raises
    ------
    ValueError
        If the colors are not valid or the interval is not valid.
    """
    if interval < 2:
        raise ValueError(f"Interval must be greater than 1, got {interval}")
    if any(0 > i < 255 for i in f_co):
        raise ValueError(f"Invalid start color: {f_co}")
    if any(0 > i < 255 for i in t_co):
        raise ValueError(f"Invalid end color: {t_co}")
    det_co = [(t - f) / interval for f, t in zip(f_co, t_co)]
    for i in range(interval):
        yield [round(f + det * i) for f, det in zip(f_co, det_co)]


def prestige_positions(prestige: int) -> Iterable[tuple[int, int, int]]:
    """Get the positions for the prestige stars

    Parameters
    ----------
    prestige: int
        The prestige of the user.

    Yields
    -------
    tuple[int, int, int]
        The positions for the prestige stars.
    """
    for i in range(min(prestige, 19)):
        yield 955 - (i * 50), 220, 25


def banner(
    base: Path | Color | tuple[Color, Color], username: str, profile: BytesIO, gang: str, quote: str, prestige: int
) -> BytesIO:
    """Create a banner image.

    Parameters
    ----------
    base : Path | Color | tuple[Color, Color]
        The file, color, or gradient to use as the base.
    username : str
        The username of the member who owns the banner.
    profile : BytesIO
        The profile of the member who owns the banner.
    gang : str
        The name of the gang.
    quote : str
        The quote to display.
    prestige : int
        The prestige of the user.

    Returns
    -------
    BytesIO
        The banner image.

    Raises
    ------
    ValueError
        If the base is invalid.
    """
    img = _init_base(base)
    draw = ImageDraw.Draw(img)
    for pos in prestige_positions(prestige):
        draw.regular_polygon(pos, 3, rotation=0, fill=STAR_COLOR, outline=STAR_COLOR)
        draw.regular_polygon(pos, 3, rotation=180, fill=STAR_COLOR, outline=STAR_COLOR)
    _write_text(draw, img, gang, quote, username)
    profile_pic_holder = Image.new("RGBA", img.size, (255, 255, 255, 0))  # Is used for a blank image so that I can mask
    mask = Image.new("RGBA", img.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((65, 65, 193, 193), fill=(255, 25, 255, 255))  # The part need to be cropped
    profile_pic_holder.paste(Image.open(profile), (65, 65, 193, 193))
    img.paste(profile_pic_holder, None, mask)
    res = BytesIO()
    img.save(res, format="PNG")
    res.seek(0)
    return res


def _write_text(draw: ImageDraw.ImageDraw, img: Image.Image, gang: str, quote: str, username: str) -> None:
    """Write the text to the image.

    Parameters
    ----------
    draw: ImageDraw.ImageDraw
        The draw object to use.
    img: Image.Image
        The image to draw on.
    gang: str
        The gang of the gang.
    quote: str
        The quote to display.
    username: str
        The username of the member who owns the banner.
    """
    draw.text((img.width - 20, 15), gang.upper(), fill=(255, 255, 255), font=FONT, anchor="ra", align="right")
    draw.multiline_text(
        (img.width - 20, 50),
        fill(quote, width=30, max_lines=4, break_long_words=True),
        fill=(255, 255, 255),
        font=FONT_QUOTE,
        align="right",
        anchor="ra",
    )
    draw.text((20, 15), username, fill=(255, 255, 255), font=FONT, anchor="la", align="left")


def _init_base(base: Path | Color | tuple[Color, Color]) -> Image.Image:
    """Initialize the base image.

    Parameters
    ----------
    base : Path | Color | tuple[Color, Color]
        The file, color, or gradient to use as the base.

    Returns
    -------
    Image.Image
        The base image.

    Raises
    ------
    ValueError
        If the base is invalid.
    """
    if isinstance(base, Path):
        try:
            img = Image.open(base)
        except (OSError, ValueError, TypeError) as e:  # pragma: no cover
            raise ValueError("Invalid base image") from e
        else:
            if img.size != (1000, 250):  # pragma: no branch  # I don't care to test this, incorrectly supplied
                # images are at the invokers own risk
                img = img.resize((1000, 250))
    elif isinstance(base, Color):
        img = Image.new("RGBA", (1000, 250), base.to_rgb())
    else:
        img = Image.new("RGBA", (1000, 250), 0)
        draw = ImageDraw.Draw(img)
        for i, color in enumerate(interpolate(base[0].to_rgb(), base[1].to_rgb(), 2000)):
            draw.line([(i, 0), (0, i)], tuple(color), width=1)
    return img


async def generate_banner(payload: BannerStatus, member: discord.Member) -> BytesIO:  # pragma: no cover
    """Generate a banner image.

    Parameters
    ----------
    payload : BannerStatus
        The info about the banner being generated
    member : discord.Member
        The member who owns the banner.
    """
    with BytesIO(await member.display_avatar.replace(size=128, format="png", static_format="png").read()) as profile:
        return await asyncio.to_thread(
            banner,
            Color.from_str(payload["color"]) if payload["color"] is not None else BASE_PATH / f"{member.id}.png",
            member.display_name,
            profile,
            payload["name"],
            payload["quote"],
            payload["prestige"],
        )


async def gen_banner(pool: asyncpg.Pool, member: discord.Member) -> discord.File | None:
    """Generate a banner for a member.

    Parameters
    ----------
    pool: asyncpg.Pool
        The database pool.
    member: discord.Member
        The member to generate the banner for.

    Returns
    -------
    image: discord.File, optional
        The generated banner.
    """
    async with pool.acquire() as conn:
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
            await conn.execute(
                "UPDATE banners SET cooldown = $1 WHERE user_id = $2",
                discord.utils.utcnow() + datetime.timedelta(days=7),
                member.id,
            )
            await conn.execute("UPDATE users SET points = points - 50 WHERE id = $1", member.id)
            return banner_file
    return None


class ApprovalView(ui.View):
    """Approve or deny a banner.

    Parameters
    ----------
    payload: BannerStatus
        The banner to approve or deny.
    mod: int
        The ID of the moderator who requested the approval session.
    """

    __slots__ = ("requester", "mod")

    def __init__(self, payload: BannerStatus, mod: int):
        super().__init__()
        self.requester = payload["user_id"]
        self.mod = mod

    async def interaction_check(self, interaction: Interaction[CBot]) -> bool:
        """Check if the interaction is valid."""
        return interaction.user.id == self.mod

    @ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: Interaction[CBot], _: ui.Button):
        """Approve the banner."""
        await interaction.response.defer(ephemeral=True)
        await interaction.client.pool.execute(
            "UPDATE banners SET approved = TRUE, cooldown = now() WHERE user_id = $1", self.requester
        )
        await interaction.edit_original_response(content="Banner approved.", attachments=[], view=None)
        self.stop()

    @ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: Interaction[CBot], _: ui.Button):
        """Deny the banner."""
        await interaction.response.defer(ephemeral=True)
        await interaction.client.pool.execute("DELETE FROM banners WHERE user_id = $1", self.requester)
        await interaction.edit_original_response(content="Banner denied.", attachments=[], view=None)
        self.stop()

    @ui.button(label="Cancel", style=discord.ButtonStyle.blurple)
    async def cancel(self, interaction: Interaction[CBot], _: ui.Button):
        """Cancel the banner."""
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_response(
            content="Banner approval session cancelled.", attachments=[], view=None
        )
        self.stop()
