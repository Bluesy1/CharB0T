# -*- coding: utf-8 -*-
import datetime
from typing import TypedDict


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
