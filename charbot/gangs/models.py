# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Gang war models."""
from enum import Enum
from typing import Literal

from discord import Color


__all__ = ("ColorOpts", "GANGS", "SQL_MONTHLY")


class ColorOpts(Enum):
    Black = Color(0x36454F)  # actually called charcoal, but is close enough to black
    Red = Color.dark_red()
    Green = Color.green()
    Blue = Color(0x0000FF)
    Purple = Color(0x800080)
    Violet = Color(0xEE82EE)
    Yellow = Color(0xFFD700)
    Orange = Color(0xFF6200)
    White = Color(0xC0C0C0)  # actually called silver, but is close enough to white


GANGS = Literal["Black", "Red", "Green", "Blue", "Purple", "Violet", "Yellow", "Orange", "White"]
SQL_MONTHLY = """
DO $$
DECLARE
user_id BIGINT;
gang VARCHAR(10);
BEGIN
UPDATE gangs SET all_paid = TRUE WHERE all_paid IS NOT TRUE;
FOR user_id, gang IN SELECT gang_members.user_id, gang_members.gang FROM gang_members
    LOOP
    IF (SELECT points from users WHERE id == user_id) >= (SELECT upkeep_base + (
        upkeep_slope * (SELECT COUNT(*) FROM gang_members WHERE gang = gang)) FROM gangs WHERE name = gang)
        THEN
            UPDATE users SET points = points - (SELECT upkeep_base + (
                upkeep_slope * (SELECT COUNT(*) FROM gang_members WHERE gang = gang))
                                                FROM gangs WHERE name = gang) WHERE id = user_id;
    ELSE
        UPDATE gang_members SET paid = FALSE WHERE user_id = user_id;
        UPDATE gangs SET all_paid = FALSE WHERE name = gang;
    END IF;
END LOOP;
END $$;
"""
