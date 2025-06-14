"""Card generator for Charbot."""

import math
import pathlib
from collections.abc import Callable
from io import BytesIO
from typing import Final

from discord.utils import MISSING
from PIL import Image, ImageDraw, ImageFont


__all__ = ("generate_card", "generate_profile")
__BASE_PATH__: Final[pathlib.Path] = pathlib.Path(__file__).parent / "media/pools"
__DEFAULT_BG__: Final[pathlib.Path] = __BASE_PATH__ / "card.png"
__DEFAULT_PROFILE__: Final[pathlib.Path] = __BASE_PATH__ / "profile.png"
__ONLINE__: Final[pathlib.Path] = __BASE_PATH__ / "online.png"
__OFFLINE__: Final[pathlib.Path] = __BASE_PATH__ / "offline.png"
__IDLE__: Final[pathlib.Path] = __BASE_PATH__ / "idle.png"
__DND__: Final[pathlib.Path] = __BASE_PATH__ / "dnd.png"
__STREAMING__: Final[pathlib.Path] = __BASE_PATH__ / "streaming.png"
__FONT__: Final[str] = str(__BASE_PATH__ / "font2.ttf")
__SMALL_FONT__: Final[ImageFont.FreeTypeFont] = ImageFont.truetype(str(__BASE_PATH__ / "font.ttf"), 20)
__NORMAL_FONT__: Final[ImageFont.FreeTypeFont] = ImageFont.truetype(__FONT__, 36)
__SIGNA_FONT__: Final[ImageFont.FreeTypeFont] = ImageFont.truetype(__FONT__, 25)
__WHITE__: Final[tuple[int, int, int]] = (255, 255, 255)
__DARK__: Final[tuple[int, int, int]] = (252, 179, 63)
__YELLOW__: Final[tuple[int, int, int]] = (255, 234, 167)
__XP_AS_STR__: Final[Callable[[int], str]] = lambda xp: (
    str(xp) if xp < 1000 else f"{xp / 1000:.1f}k" if xp < 1000000 else f"{xp / 1000000:.1f}M"
)


def _overlay(card: Image.Image, profile: Image.Image, status: Image.Image, percentage: float, ellipse: bool) -> BytesIO:
    # Add another blank layer for the progress bar
    # Because drawing on card doesn't make their background transparent
    blank = Image.new("RGBA", card.size, (255, 255, 255, 0))
    blank_draw = ImageDraw.Draw(blank)
    blank_draw.rectangle((245, 185, 750, 205), fill=(255, 255, 255, 0), outline=__DARK__)

    status = status.convert("RGBA").resize((40, 40))
    length_of_bar = (percentage * 4.9) + 248

    blank_draw.rectangle((248, 188, length_of_bar, 202), fill=__DARK__)
    if ellipse:  # pragma: no cover
        blank_draw.ellipse((20, 20, 218, 218), fill=(255, 255, 255, 0), outline=__DARK__)

    profile_pic_holder = Image.new("RGBA", card.size, (255, 255, 255, 0))  # Used as blank image for a mask
    profile_pic_holder.paste(profile, (29, 29, 209, 209), profile)

    pre = Image.composite(profile_pic_holder, card, profile_pic_holder)
    pre = Image.alpha_composite(pre, blank)

    # Status badge
    # Another blank
    blank = Image.new("RGBA", pre.size, (255, 255, 255, 0))
    blank.paste(status, (169, 169))

    final = Image.alpha_composite(pre, blank)
    final_bytes = BytesIO()
    final.save(final_bytes, "png")
    final_bytes.seek(0)
    return final_bytes


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
    if bg_image is MISSING:
        card = Image.open(__DEFAULT_BG__).convert("RGBA")
    else:
        card = Image.open(bg_image).convert("RGBA")

        width, height = card.size
        if width != 900 or height != 238:
            x1 = 0
            y1 = 0
            x2 = width
            nh = math.ceil(width * 0.264444)
            y2 = 0

            if nh < height:  # pragma: no branch
                y1 = (height // 2) - 119
                y2 = nh + y1

            card = card.crop((x1, y1, x2, y2)).resize((900, 238))

    profile_bytes: BytesIO | pathlib.Path = profile_image if profile_image is not MISSING else __DEFAULT_PROFILE__
    profile = Image.open(profile_bytes).convert("RGBA").resize((180, 180))

    # Mask to crop image
    mask = Image.new("RGBA", card.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((29, 29, 209, 209), fill=(255, 25, 255, 255))  # The part need to be cropped

    draw = ImageDraw.Draw(card)
    draw.text((245, 22), pool_name, __WHITE__, font=__NORMAL_FONT__)
    draw.text((245, 98), f"Pool Level {level}", __WHITE__, font=__SMALL_FONT__)
    draw.text((245, 123), reward, __WHITE__, font=__SMALL_FONT__)
    draw.text(
        (245, 150),
        f"Rep {__XP_AS_STR__(current_rep)}/{__XP_AS_STR__(completed_rep)}",
        __WHITE__,
        font=__SMALL_FONT__,
    )

    xp_need = completed_rep - base_rep
    xp_have = current_rep - base_rep

    current_percentage = (xp_have / xp_need) * 100

    status = Image.open(__OFFLINE__)
    if 0 < current_percentage < 34:
        status = Image.open(__DND__)
    elif 34 <= current_percentage < 67:
        status = Image.open(__IDLE__)
    elif 67 <= current_percentage < 100:
        status = Image.open(__STREAMING__)
    elif current_percentage == 100:
        status = Image.open(__ONLINE__)

    return _overlay(card, profile, status, current_percentage, False)


def generate_profile(  # pragma: no cover
    user_name: str,
    profile_image: BytesIO,
    level: int = 1,
    current_xp: int = 0,
    user_xp: int = 20,
    next_xp: int = 100,
    user_position: int = 1,
    user_status: str = "online",
):
    card = Image.open(__DEFAULT_BG__).convert("RGBA")

    profile = Image.open(profile_image)
    profile = profile.convert("RGBA").resize((180, 180))
    mask = Image.new("L", profile.size, 0)
    mask_draw = ImageDraw.Draw(mask).ellipse((0, 0, 180, 180), fill=255)
    profile.putalpha(mask)

    match user_status:
        case "online":
            status = Image.open(__ONLINE__)
        case "idle":
            status = Image.open(__IDLE__)
        case "streaming":
            status = Image.open(__STREAMING__)
        case "dnd":
            status = Image.open(__DND__)
        case _:
            status = Image.open(__OFFLINE__)

    status = status.convert("RGBA").resize((40, 40))

    # Mask to crop image
    mask = Image.new("RGBA", card.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((29, 29, 209, 209), fill=(255, 25, 255, 255))  # The part need to be cropped

    draw = ImageDraw.Draw(card)
    draw.text((245, 22), user_name, __WHITE__, font=__NORMAL_FONT__)
    draw.text((245, 98), f"Rank #{user_position}", __WHITE__, font=__SMALL_FONT__)
    draw.text((245, 123), f"Level {level}", __WHITE__, font=__SMALL_FONT__)
    draw.text(
        (245, 150),
        f"Exp {__XP_AS_STR__(user_xp)}/{__XP_AS_STR__(next_xp)}",
        __WHITE__,
        font=__SMALL_FONT__,
    )

    xp_need = next_xp - current_xp
    xp_have = user_xp - current_xp

    return _overlay(card, profile, status, (xp_have / xp_need) * 100, True)
