# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Banner code."""
import asyncio
from collections.abc import Iterable
from io import BytesIO
from pathlib import Path
from textwrap import fill
from typing import Final

import discord
from discord import Color
from PIL import Image, ImageDraw, ImageFont

from ._types import BannerStatus


FONT: Final = ImageFont.truetype("charbot/media/pools/font.ttf", 30)
FONT_QUOTE: Final = ImageFont.truetype("charbot/media/pools/font.ttf", 20)
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
    for i in range(prestige):
        if i >= 19:
            return
        yield 955 - (i * 50), 220, 25


def banner(
    base: Path | Color | tuple[Color, Color], username: str, profile: BytesIO, quote: str, prestige: int
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
    if isinstance(base, Path):
        try:
            img = Image.open(base)
        except (OSError, ValueError, TypeError) as e:  # pragma: no cover
            raise ValueError("Invalid base image") from e
        else:
            if img.size != (1000, 250):  # pragma: no branch  # i don't care to test this, incorrectly supplied
                # images are at the invokers own risk
                img = img.resize((1000, 250))
    elif isinstance(base, Color):
        img = Image.new("RGBA", (1000, 250), base.to_rgb())
    else:
        img = Image.new("RGBA", (1000, 250), 0)
        draw = ImageDraw.Draw(img)
        for i, color in enumerate(interpolate(base[0].to_rgb(), base[1].to_rgb(), 2000)):
            draw.line([(i, 0), (0, i)], tuple(color), width=1)
    draw = ImageDraw.Draw(img)
    for pos in prestige_positions(prestige):
        draw.regular_polygon(pos, 3, rotation=0, fill=STAR_COLOR, outline=STAR_COLOR)
        draw.regular_polygon(pos, 3, rotation=180, fill=STAR_COLOR, outline=STAR_COLOR)
    draw.multiline_text(
        (img.width - 20, 50),
        fill(quote, width=30, max_lines=4, break_long_words=True),
        fill=(255, 255, 255),
        font=FONT,
        align="right",
        anchor="ra",
    )
    draw.text((20, 15), username, fill=(255, 255, 255), font=FONT, anchor="la", align="left")
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


async def generate_banner(payload: BannerStatus, member: discord.Member) -> BytesIO:  # pragma: no cover
    """Generate a banner image.

    Parameters
    ----------
    payload : BannerStatus
        The infor about the banner being generated
    member : discord.Member
        The member who owns the banner.
    """
    with BytesIO(await member.display_avatar.replace(size=128, format="png", static_format="png").read()) as profile:
        return await asyncio.to_thread(
            banner,
            Color.from_str(payload["color"]) if payload["color"] is not None else BASE_PATH / f"{member.id}.png",
            member.display_name,
            profile,
            payload["quote"],
            0,
        )
