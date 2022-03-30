# -*- coding: utf-8 -*-
#  ----------------------------------------------------------------------------
#  MIT License
#
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
import os
import datetime as _datetime
from calendar import timegm
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

import aiohttp
import discord
from discord.utils import utcnow, format_dt
from discord.ext import commands, tasks
from dotenv import load_dotenv
from pytz import timezone
from validators import url

load_dotenv()

ytLink = "https://www.youtube.com/charliepryor/live"
chartime = ZoneInfo("US/Michigan")


def getUrl(mintime: datetime, maxtime: datetime):
    """Creates gcal API url"""
    baseUrl = "https://www.googleapis.com/calendar/v3/calendars"
    key = f"key={os.getenv('CALKEY')}"
    calendar = "u8n1onpbv9pb5du7gssv2md58s@group.calendar.google.com"
    minTime = f"timeMin={mintime.isoformat()}"
    maxTime = f"timeMax={maxtime.isoformat()}"
    return f"{baseUrl}/{calendar}/events?{key}&{minTime}&{maxTime}"


def datetime_range(start: datetime, end: datetime, delta: timedelta):
    """Timelist range generator"""
    current = start
    while current < end:
        yield current.time()
        current += delta


def ceil_dt(dt: datetime, delta: timedelta):
    """Rounds a datetime up to the nearest x minutes"""
    return dt + (datetime(_datetime.MINYEAR, 1, 1, tzinfo=timezone("UTC")) - dt) % delta


def default_field(dictionary: dict, add_time: datetime, item: dict) -> None:
    """Adds the default dict field"""
    dictionary.update(
        {
            timegm(add_time.utctimetuple()): {
                "value": f"{format_dt(add_time, 'F')}\n"
                f"[({add_time.astimezone(chartime).strftime('%X %x %Z')})]({ytLink})",
                "name": item["summary"],
                "inline": True,
            }
        }
    )


class Calendar(commands.Cog):
    """Calendar task cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message: Optional[discord.WebhookMessage] = None
        self.week_end = (
            utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            - timedelta(days=utcnow().weekday())
            + timedelta(days=7)
        )
        self.webhook: Optional[discord.Webhook] = None
        current = ceil_dt(utcnow(), timedelta(minutes=30))
        timeline = list(
            set(
                datetime_range(
                    current, current + timedelta(hours=24), timedelta(minutes=30)
                )
            )
        )
        self.calendar.change_interval(time=timeline)

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Unload function"""
        self.calendar.cancel()

    async def cog_load(self) -> None:
        """Cog setup hook"""
        webhook_id = int(os.getenv("WEBHOOK_ID"))  # type: ignore
        self.webhook = await self.bot.fetch_webhook(webhook_id)
        self.calendar.start()

    @tasks.loop()
    async def calendar(self):
        """Calendar update loop"""
        if self.webhook is None:
            webhook_id = int(os.getenv("WEBHOOK_ID"))  # type: ignore
            self.webhook = await self.bot.fetch_webhook(webhook_id)
        mindatetime = datetime.now(tz=timezone("US/Eastern"))
        maxdatetime = datetime.now(tz=timezone("US/Eastern")) + timedelta(weeks=1)
        callUrl = getUrl(mindatetime, maxdatetime)
        async with aiohttp.ClientSession() as session, session.get(callUrl) as response:
            items = await response.json()
        fields = {}
        cancelled_times = []
        times = set()
        for item in items["items"]:
            if item["status"] == "cancelled":
                sub_time = datetime.fromisoformat(item["originalStartTime"]["dateTime"])
                while sub_time < utcnow():
                    sub_time = sub_time + timedelta(days=7)
                cancelled_times.append(sub_time)
                continue
            sub_time = datetime.fromisoformat((item["start"]["dateTime"]))
            flag = True
            if mindatetime < sub_time + timedelta(hours=2):
                times.add(sub_time)
                flag = False
            while sub_time < utcnow():
                sub_time = sub_time + timedelta(days=7)
            if flag:
                times.add(sub_time)
            if mindatetime < sub_time > maxdatetime:
                continue
            if "description" not in item.keys():
                default_field(fields, sub_time, item)
            elif url(item["description"]):
                fields.update(
                    {
                        timegm(sub_time.utctimetuple()): {
                            "name": f"{item['summary']}",
                            "value": f"{format_dt(sub_time, 'F')}\n"
                            f"[({sub_time.astimezone(chartime).strftime('%X %x %Z')})"
                            f"]({item['description']})",
                            "inline": True,
                        }
                    }
                )
            else:
                default_field(fields, sub_time, item)
            for sub_time in cancelled_times:
                fields.pop(timegm(sub_time.utctimetuple()), None)
                times.discard(sub_time)
        next_event = min(times, default=None)
        # noinspection PyTypeChecker
        fields = dict(sorted(fields.items()))
        embed = discord.Embed(
            title="List of streams in the next 7 days",
            color=discord.Color.dark_blue(),
            timestamp=discord.utils.utcnow(),
            url="https://cpry.net/calendar",
            description=f"Click on the following links to go to Charlie's Calender,"
            f" YouTube channel, Twitch, or click on the times to go to the"
            f" corresponding streams. The blue time is the time of the stream in"
            f" Charlie's timezone, and they link to the platform where the stream is "
            f"being broadcast.\n"
            f" [Calendar](https://cpry.net/calendar)\n"
            f" [YouTube](https://www.youtube.com/charliepryor/live)\n"
            f" [Twitch](https://www.twitch.tv/charliepryor)\n Next stream: "
            f"{format_dt(next_event, 'R') if next_event else 'No streams scheduled'}",
        )
        for field in fields:
            field = fields[field]
            embed.add_field(
                name=field["name"], value=field["value"], inline=field["inline"]
            )

        embed.set_author(
            name="Charlie",
            icon_url="https://cdn.discordapp.com/avatars/225344348903047168/"
            "c093900592dfcd9b9e5c711f4e1c627d.webp?size=160",
        )
        embed.set_footer(text="Last Updated")

        if self.message is None:
            self.message = await self.webhook.send(
                username=self.bot.user.name,  # type: ignore
                avatar_url=self.bot.user.avatar.url,  # type: ignore
                embed=embed,
                wait=True,
            )
        elif utcnow() > self.week_end:
            await self.message.delete()
            self.message = await self.webhook.send(
                username=self.bot.user.name,  # type: ignore
                avatar_url=self.bot.user.avatar.url,  # type: ignore
                embed=embed,
                wait=True,
            )
            self.week_end += timedelta(days=7)
        else:
            self.message = await self.message.edit(embed=embed)


async def setup(bot: commands.Bot):
    """Loads extension"""
    await bot.add_cog(Calendar(bot))
