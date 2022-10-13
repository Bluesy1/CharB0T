# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
import datetime
from typing import TypedDict


class BannerStatus(TypedDict):
    """Basic banner status"""

    user_id: int
    quote: str
    color: str | None
    cooldown: datetime.datetime
    approved: bool


class BannerStatusPoints(BannerStatus):
    """Banner status, but with user's points included"""

    points: int
