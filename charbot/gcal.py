# coding=utf-8
import os
import pprint
import datetime as _datetime
from calendar import timegm
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

import aiohttp
import discord
from discord.utils import utcnow
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


def default_field(dictionary: dict, add_time: datetime, item: dict[str, any]) -> None:
    """Adds the default dict field"""
    dictionary.update(
        {
            timegm(add_time.utctimetuple()): {
                "value": f"<t:{timegm(add_time.utctimetuple())}:F>\n"
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
            set(datetime_range(current, self.week_end, timedelta(minutes=30)))
        )
        self.calendar.change_interval(time=timeline)

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Unload function"""
        self.calendar.cancel()

    async def cog_load(self) -> None:
        """Cog setup hook"""
        self.webhook = await self.bot.fetch_webhook(int(os.getenv("WEBHOOK")))
        self.calendar.start()

    @tasks.loop()
    async def calendar(self):
        """Calendar update loop"""
        if self.webhook is None:
            self.webhook = await self.bot.fetch_webhook(int(os.getenv("WEBHOOK")))
        mindatetime = datetime.now(tz=timezone("US/Eastern"))
        maxdatetime = datetime.now(tz=timezone("US/Eastern")) + timedelta(weeks=1)
        callUrl = getUrl(mindatetime, maxdatetime)
        embed = discord.Embed(
            title="List of streams in the next 7 days",
            color=discord.Color.dark_blue(),
            timestamp=discord.utils.utcnow(),
            url="https://cpry.net/calendar",
        )
        async with aiohttp.ClientSession() as session, session.get(callUrl) as response:
            items = await response.json()
        pprint.pprint(items)
        fields = {}
        for item in items["items"]:
            if item["status"] == "cancelled":
                continue
            sub_time = datetime.fromisoformat((item["start"]["dateTime"]))
            if mindatetime < sub_time > maxdatetime:
                continue
            if "description" not in item.keys():
                default_field(fields, sub_time, item)
            elif url(item["description"]):
                fields.update(
                    {
                        timegm(sub_time.utctimetuple()): {
                            "name": f"{item['summary']}",
                            "value": f"<t:{timegm(sub_time.utctimetuple())}:F>\n"
                            f"[({sub_time.astimezone(chartime).strftime('%X %x %Z')})"
                            f"]({item['description']})",
                            "inline": True,
                        }
                    }
                )
            else:
                default_field(fields, sub_time, item)
        # noinspection PyTypeChecker
        fields = dict(sorted(fields.items()))

        for field in fields:
            field = fields[field]
            embed.add_field(
                name=field["name"], value=field["value"], inline=field["inline"]
            )

        if not embed.fields:
            embed = discord.Embed(
                title="List of streams in the next 7 days",
                description="There are no streams registered in the next 7 days.",
                color=discord.Color.dark_blue(),
                timestamp=discord.utils.utcnow(),
                url="https://cpry.net/calendar",
            )
        embed.set_author(
            name="Charlie",
            icon_url="https://cdn.discordapp.com/avatars/225344348903047168/"
            "c093900592dfcd9b9e5c711f4e1c627d.webp?size=160",
        )
        embed.set_footer(text="Last Updated")

        if self.message is None:
            self.message = await self.webhook.send(
                username=self.bot.user.name,
                avatar_url=self.bot.user.avatar.url,
                embed=embed,
                wait=True,
            )
        elif utcnow() > self.week_end:
            await self.message.delete()
            self.message = await self.webhook.send(
                username=self.bot.user.name,
                avatar_url=self.bot.user.avatar.url,
                embed=embed,
                wait=True,
            )
            self.week_end += timedelta(days=7)
        else:
            self.message = await self.message.edit(embed=embed)


async def setup(bot: commands.Bot):
    """Loads extension"""
    await bot.add_cog(Calendar(bot))
