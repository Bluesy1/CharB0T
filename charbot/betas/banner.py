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


FONT: Final = ImageFont.truetype((Path(__file__).parent.parent / "media" / "pools" / "font.ttf").read_bytes(), 30)
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
    """
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
        except (OSError, ValueError, TypeError):
            raise ValueError("Invalid base image")
        else:
            if img.size != (1000, 250):
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
    #  draw.text((img.width - 20, 15), name.upper(), fill=(255, 255, 255), font=FONT, anchor="ra", align="right")
    draw.multiline_text(
        (img.width - 20, 50),
        fill(quote, width=22, max_lines=5),
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


async def generate_banner(payload: BannerStatus, member: discord.Member) -> BytesIO:
    """Generate a banner image.

    Parameters
    ----------
    payload : BannerStatus
        The infor about the banner being generated
    member : discord.Member
        The member who owns the banner.
    """
    c = payload["color"]
    prof = BytesIO()
    await member.display_avatar.replace(size=128, format="png", static_format="png").save(prof)
    if c is None:
        return await asyncio.to_thread(
            banner,
            BASE_PATH / f"{member.id}.png",
            member.display_name,
            prof,
            payload["quote"],
            0,
        )
    color = Color.from_str(c)
    return await asyncio.to_thread(
        banner,
        color,
        member.display_name,
        prof,
        payload["quote"],
        0,
    )
