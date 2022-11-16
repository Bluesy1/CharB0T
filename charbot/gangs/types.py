# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import TypedDict, NamedTuple

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


class GangDues(TypedDict):
    name: str
    channel: int
    role: int
    complete: bool


class Benefit(TypedDict):
    id: int
    name: str
    benefit: Benefits
    value: int


class Territory(TypedDict):
    id: int
    name: str
    gang: str
    members: list[GangMember]
    benefit: Benefit
    raid_end: datetime.datetime | None
    raider: str | None
    attack: int
    defense: int


class TerritoryDefender(TypedDict):
    id: int
    defenders: list[int]
    defense: int


class TerritoryOffense(TypedDict):
    id: int
    attackers: list[int]
    attack: int


class ItemUseInfo(TypedDict):
    id: int
    name: str
    quantity: int
    value: int
    benefit: Benefits
    cost: int


class Item(NamedTuple):
    name: str
    description: str
    cost: int
    quantity: int | None
