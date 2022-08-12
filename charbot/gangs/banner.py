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
"""Gang banner code."""
from collections.abc import Iterable
from io import BytesIO
from textwrap import fill
from typing import Final

from discord import Color
from PIL import Image, ImageDraw, ImageFont

FONT: Final = ImageFont.truetype("/home/gavin/PycharmProjects/CharB0T/charbot/media/pools/font.ttf", 30)


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
    """
    det_co = [(t - f) / interval for f, t in zip(f_co, t_co)]
    for i in range(interval):
        yield [round(f + det * i) for f, det in zip(f_co, det_co)]


def banner(
    base: BytesIO | Color | tuple[Color, Color], username: str, profile: BytesIO, name: str, quote: str
) -> BytesIO:
    """Create a banner image.

    Parameters
    ----------
    base : BytesIO | Color | tuple[Color, Color]
        The file, color, or gradient to use as the base.
    username : str
        The username of the member who owns the banner.
    profile : BytesIO
        The profile of the member who owns the banner.
    name : str
        The name of the gang.
    quote : str
        The quote to display.

    Returns
    -------
    BytesIO
        The banner image.

    Raises
    ------
    ValueError
        If the base is invalid.
    """
    if isinstance(base, BytesIO):
        try:
            img = Image.open(base)
        except (OSError, ValueError, TypeError):
            raise ValueError("Invalid base image")
        else:
            if img.size != (1000, 500):
                img = img.resize((1000, 250))
    elif isinstance(base, Color):
        img = Image.new("RGBA", (1000, 250), base.to_rgb())
    else:
        img = Image.new("RGBA", (1000, 250), 0)
        draw = ImageDraw.Draw(img)
        for i, color in enumerate(interpolate(base[0].to_rgb(), base[1].to_rgb(), 2000)):
            draw.line([(i, 0), (0, i)], tuple(color), width=1)
    draw = ImageDraw.Draw(img)
    draw.text((img.width - 20, 15), name.upper(), fill=(255, 255, 255), font=FONT, anchor="ra", align="right")
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
    # prof = member.display_avatar.replace(size=128, format="png", static_format="png")
    profile_pic_holder.paste(Image.open(profile), (65, 65, 193, 193))
    img.paste(profile_pic_holder, None, mask)
    res = BytesIO()
    img.save(res, format="PNG")
    res.seek(0)
    return res
