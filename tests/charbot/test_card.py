# -*- coding: utf-8 -*-
from io import BytesIO

import pytest
from discord.utils import MISSING
from PIL import Image

from charbot import card


@pytest.mark.parametrize("current", [0, 1, 35, 68, 100])
def test_generate_card(current):
    """Test the generate_card function."""
    with open(f"tests/charbot/media/card_test_{current}_rep.PNG", "rb") as f, open(
        "charbot/media/pools/profile.png", "rb"
    ) as f2, open("charbot/media/pools/card.png", "rb") as f3:
        assert Image.open(f) == Image.open(
            card.generate_card(
                level=1,
                current_rep=current,
                completed_rep=100,
                pool_name="Lorem ipsum",
                reward="dolor sit amet, consectetur adipiscing elit, sed",
                bg_image=BytesIO(f2.read()) if current == 0 else BytesIO(f3.read()) if current == 1 else MISSING,
            )
        )
