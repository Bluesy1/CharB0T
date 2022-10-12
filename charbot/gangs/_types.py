# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal
from typing import TypedDict, Any


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
    id: int
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


class GangMember(TypedDict):
    user_id: int
    gang: Gang


class Territory(TypedDict):
    id: int
    gang: Gang | None
    members: list[GangMember]
    control: Decimal  # numeric type in postgres
    benefit: Any  # Placeholder type TODO: add concrete type
    raid_end: datetime.datetime | None
    raider: Gang | None
