# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
import datetime
from decimal import Decimal
from typing import TypedDict

from .enums import Benefits


class BannerRequestLeader(TypedDict):
    leader: bool
    leadership: bool
    points: int
    banner: bool


class BannerStatus(TypedDict):
    user_id: int
    quote: str
    color: str | None
    gradient: bool
    cooldown: datetime.datetime
    approved: bool
    gang_color: int
    name: str
    prestige: int


class BannerStatusPoints(BannerStatus):
    points: int


class Gang(TypedDict):
    name: str
    color: int
    leader: int
    role: int
    channel: int
    control: int
    join_base: int
    join_slope: Decimal  # numeric type in postgres
    upkeep_base: int
    upkeep_slope: Decimal  # numeric type in postgres
    all_paid: bool


class GangMember(TypedDict):
    user_id: int
    gang: Gang


class Benefit(TypedDict):
    id: int
    name: str
    benefit: Benefits
    value: int


class Territory(TypedDict):
    id: int
    name: str
    gang: Gang | None
    members: list[GangMember]
    control: Decimal  # numeric type in postgres
    benefit: Benefit
    raid_end: datetime.datetime | None
    raider: Gang | None
