# -*- coding: utf-8 -*-
#  ----------------------------------------------------------------------------
#  MIT License
#
# Copyright (c) 2020 - 2021 Md Shahriyar Alam
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
"""Card generator for Charbot."""
import math
from io import BytesIO

from discord.utils import MISSING
from PIL import Image, ImageDraw, ImageFont


def generate_card(
    *,
    bg_image: BytesIO = MISSING,
    profile_image: BytesIO = MISSING,
    level: int = 1,
    base_rep: int = 0,
    current_rep: int = 20,
    completed_rep: int = 100,
    pool_name: str = "Unknown",
    reward: str = "Unknown",
):
    """Generate a card.

    This is adapted from the disrank library.

    Parameters
    ----------
    bg_image: BytesIO = MISSING
        The background image. Defaults to the default background image.
    profile_image: BytesIO = MISSING
        The profile image. Defaults to the default profile image.
    level: int = 1
        The level of the pool.
    base_rep: int = 0
        The base rep of the pool.
    current_rep: int = 20
        The current rep in the pool.
    completed_rep: int = 100
        The rep needed to complete the pool.
    pool_name: str = "Unknown"
        The name of the pool. Defaults to "Unknown".
    reward: str = "Unknown"
        The reward of the pool. Defaults to "Unknown".

    Returns
    -------
    BytesIO
        The card image as a buffered stream of I/O Bytes.
    """
    default_bg = "charbot/media/pools/card.png"
    default_profile = "charbot/media/pools/profile.png"
    online = "charbot/media/pools/online.png"
    offline = "charbot/media/pools/offline.png"
    idle = "charbot/media/pools/idle.png"
    dnd = "charbot/media/pools/dnd.png"
    streaming = "charbot/media/pools/streaming.png"
    font1 = "charbot/media/pools/font.ttf"
    font2 = "charbot/media/pools/font2.ttf"
    if bg_image is MISSING:
        card = Image.open(default_bg).convert("RGBA")
    else:
        card = Image.open(bg_image).convert("RGBA")

        width, height = card.size
        if width == 900 and height == 238:
            pass
        else:
            x1 = 0
            y1 = 0
            x2 = width
            nh = math.ceil(width * 0.264444)
            y2 = 0

            if nh < height:
                y1 = (height // 2) - 119
                y2 = nh + y1

            card = card.crop((x1, y1, x2, y2)).resize((900, 238))

    profile_bytes: BytesIO | str = profile_image if profile_image is not MISSING else default_profile
    profile = Image.open(profile_bytes).convert("RGBA").resize((180, 180))

    profile_pic_holder = Image.new("RGBA", card.size, (255, 255, 255, 0))  # Is used for a blank image for a mask

    # Mask to crop image
    mask = Image.new("RGBA", card.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((29, 29, 209, 209), fill=(255, 25, 255, 255))  # The part need to be cropped

    # Editing stuff here

    # ======== Fonts to use =============
    font_normal = ImageFont.truetype(font2, 36)
    font_small = ImageFont.truetype(font1, 20)
    # noinspection PyUnusedLocal
    font_signa = ImageFont.truetype(font2, 25)  # noqa: F841

    # ======== Colors ========================
    WHITE = (255, 255, 255)
    DARK = (252, 179, 63)
    # noinspection PyUnusedLocal
    YELLOW = (255, 234, 167)  # noqa: F841

    get_str = (
        lambda xp: str(xp) if xp < 1000 else f"{xp / 1000:.1f}k" if xp < 1000000 else f"{xp / 1000000:.1f}M"
    )  # noqa: F731

    draw = ImageDraw.Draw(card)
    draw.text((245, 22), pool_name, WHITE, font=font_normal)
    draw.text((245, 98), f"Pool Level {level}", WHITE, font=font_small)
    draw.text((245, 123), reward, WHITE, font=font_small)
    draw.text(
        (245, 150),
        f"Rep {get_str(current_rep)}/{get_str(completed_rep)}",
        WHITE,
        font=font_small,
    )

    # Adding another blank layer for the progress bar
    # Because drawing on card doesn't make their background transparent
    blank = Image.new("RGBA", card.size, (255, 255, 255, 0))
    blank_draw = ImageDraw.Draw(blank)
    blank_draw.rectangle((245, 185, 750, 205), fill=(255, 255, 255, 0), outline=DARK)

    xpneed = completed_rep - base_rep
    xphave = current_rep - base_rep

    current_percentage = (xphave / xpneed) * 100

    status = Image.open(offline)
    if 0 < current_percentage < 34:
        status = Image.open(dnd)
    elif 0.34 <= current_percentage < 67:
        status = Image.open(idle)
    elif 0.67 <= current_percentage < 100:
        status = Image.open(streaming)
    elif current_percentage == 100:
        status = Image.open(online)

    status = status.convert("RGBA").resize((40, 40))
    length_of_bar = (current_percentage * 4.9) + 248

    blank_draw.rectangle((248, 188, length_of_bar, 202), fill=DARK)
    # blank_draw.ellipse((20, 20, 218, 218), fill=(255, 255, 255, 0), outline=DARK)  # skipcq: PY-W0069

    profile_pic_holder.paste(profile, (29, 29, 209, 209), profile)

    pre = Image.composite(profile_pic_holder, card, profile_pic_holder)
    pre = Image.alpha_composite(pre, blank)

    # Status badge
    # Another blank
    blank = Image.new("RGBA", pre.size, (255, 255, 255, 0))
    blank.paste(status, (169, 169))

    final = Image.alpha_composite(pre, blank)
    if __name__ == "__main__":
        final.show()
    final_bytes = BytesIO()
    final.save(final_bytes, "png")
    final_bytes.seek(0)
    return final_bytes


if __name__ == "__main__":
    generate_card(
        level=1,
        current_rep=0,
        completed_rep=100,
        pool_name="Lorem ipsum",
        reward="dolor sit amet, consectetur adipiscing elit, sed",
    )
