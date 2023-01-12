# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT
from io import BytesIO

import pytest
from discord.utils import MISSING
from PIL import Image

from charbot import card


@pytest.mark.parametrize("current", [0, 1, 35, 68, 100])
def test_generate_card(current):
    """Test the generate_card function."""
    with Image.open(f"tests/charbot/media/card_test_{current}_rep.PNG") as expected, open(
        "charbot/media/pools/profile.png", "rb"
    ) as f2, open("charbot/media/pools/card.png", "rb") as f3:
        got = Image.open(
            card.generate_card(
                level=1,
                current_rep=current,
                completed_rep=100,
                pool_name="Lorem ipsum",
                reward="dolor sit amet, consectetur adipiscing elit, sed",
                bg_image=BytesIO(f2.read()) if current == 0 else BytesIO(f3.read()) if current == 1 else MISSING,
            )
        )
        assert expected == got, f"Got unexpected card for {current} rep"
