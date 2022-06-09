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
"""Dynamic stream calendar generator for the next week."""
import datetime as _datetime
import os
from calendar import timegm
from datetime import datetime, time, timedelta, timezone
from typing import NamedTuple, Optional
from zoneinfo import ZoneInfo

import aiohttp
import discord
import orjson
from discord.ext import commands, tasks
from discord.utils import MISSING, format_dt, utcnow
from dotenv import load_dotenv
from validators import url

from . import CBot


load_dotenv()

ytLink = "https://www.youtube.com/charliepryor/live"
chartime = ZoneInfo("US/Michigan")
time_format = "%H:%M %x %Z"


class EmbedField(NamedTuple):
    """A named tuple for an embed field."""

    name: str
    value: str
    inline: bool


def getUrl(mintime: datetime, maxtime: datetime):
    """Create an url for the Google calendar API query.

    Parameters
    ----------
    mintime : datetime
        The minimum time to search for.
    maxtime : datetime
        The maximum time to search for.

    Returns
    -------
    str
        The url to query the Google calendar API.
    """
    baseUrl = "https://www.googleapis.com/calendar/v3/calendars"
    key = f"key={os.getenv('CALKEY')}"
    calendar = "u8n1onpbv9pb5du7gssv2md58s@group.calendar.google.com"
    minTime = f"timeMin={mintime.isoformat()}"
    maxTime = f"timeMax={maxtime.isoformat()}"
    return f"{baseUrl}/{calendar}/events?{key}&{minTime}&{maxTime}"


def half_hour_intervals():
    """Generate a list of half-hour intervals.

    Yields
    ------
    time
        The times for the interval.
    """
    for hour in range(24):
        for minute in range(0, 60, 30):
            yield time(hour, minute)


def ceil_dt(dt: datetime, delta: timedelta) -> datetime:
    """Round a datetime up to the nearest x minutes.

    Parameters
    ----------
    dt : datetime
        The datetime to round up.
    delta : timedelta
        The timedelta to round up to.

    Returns
    -------
    datetime
        The rounded datetime.
    """
    return dt + (datetime(_datetime.MINYEAR, 1, 1, tzinfo=timezone.utc) - dt) % delta


def default_field(dictionary: dict[int, EmbedField], add_time: datetime, item: dict) -> None:
    """Add the default dict field for a specific time.

    Parameters
    ----------
    dictionary : dict[int, EmbedField]
        The dictionary to add the field to.
    add_time : datetime
        The time to add the field to.
    item : dict
        The item to add to the dictionary.
    """
    dictionary.update(
        {
            timegm(add_time.utctimetuple()): EmbedField(
                item["summary"],
                f"{format_dt(add_time, 'F')}\n" f"[({add_time.astimezone(chartime).strftime(time_format)})]({ytLink})",
                True,
            )
        }
    )


def calendar_embed(fields: dict[int, EmbedField], next_event: datetime | None) -> discord.Embed:
    """Create an embed for the calendar.

    Parameters
    ----------
    fields : dict[int, dict[str, str | bool]]
        The dictionary to create the embed from.
    next_event : datetime
        The unix time for the next event.

    Returns
    -------
    discord.Embed
        The embed to send to the channel.
    """
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
    for field in list(fields.values()):  # type: EmbedField
        embed.add_field(name=field.name, value=field.value, inline=field.inline)

    embed.set_author(
        name="Charlie",
        icon_url="https://cdn.discordapp.com/avatars/225344348903047168/"
        "c093900592dfcd9b9e5c711f4e1c627d.webp?size=160",
    )
    return embed.set_footer(text="Last Updated")


# noinspection GrazieInspection
class Calendar(commands.Cog):
    """
    Calendar cog for the bot.

    Parameters
    ----------
    bot : commands.Bot
        The bot the cog is attached to.

    Attributes
    ----------
    bot : commands.Bot
        The bot the cog is attached to.
    message : discord.WebhookMessage
        The message the bot is editing.
    week_end : datetime
        The end of the week.
    webhook : discord.Webhook
        Webhook the bot is posting to.

    Methods
    -------
    get_calendar()
        Gets the calendar for the next week.
    cog_unload()
        Unloads the cog.
    cog_load()
        Loads the cog.
    """

    def __init__(self, bot: CBot):
        self.bot: CBot = bot
        self.message: discord.WebhookMessage = MISSING
        self.week_end = (
            utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            - timedelta(days=utcnow().weekday())
            + timedelta(days=7)
        )
        self.webhook: Optional[discord.Webhook] = None
        self.calendar.change_interval(time=list(half_hour_intervals()))

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Unload hook."""
        self.calendar.cancel()
        self.bot.holder["message"] = self.message
        self.bot.holder["webhook"] = self.webhook

    async def cog_load(self) -> None:
        """Load hook."""
        webhook_id = os.getenv("WEBHOOK_ID")
        assert isinstance(webhook_id, str)  # skipcq: BAN-B101
        self.webhook = self.bot.holder.pop("webhook", await self.bot.fetch_webhook(int(webhook_id)))
        self.message = self.bot.holder.pop("message", MISSING)
        self.calendar.start()

    @tasks.loop()
    async def calendar(self):
        """Calendar loop.

        This loop is responsible for posting the calendar every half hour.
        It queries the Google calendar API and posts the results to the
        webhook, after parding and formatting the results.
        """
        if self.webhook is None:
            webhook_id = os.getenv("WEBHOOK_ID")
            assert isinstance(webhook_id, str)  # skipcq: BAN-B101
            self.webhook = await self.bot.fetch_webhook(int(webhook_id))
        mindatetime = datetime.now(tz=ZoneInfo("America/New_York"))
        maxdatetime = datetime.now(tz=ZoneInfo("America/New_York")) + timedelta(weeks=1)
        async with aiohttp.ClientSession() as session, session.get(getUrl(mindatetime, maxdatetime)) as response:
            items = await response.json(loads=orjson.loads)
        fields: dict[int, EmbedField] = {}
        cancelled_times = []
        times: set[datetime] = set()
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
                        timegm(sub_time.utctimetuple()): EmbedField(
                            f"{item['summary']}",
                            f"{format_dt(sub_time, 'F')}\n[({sub_time.astimezone(chartime).strftime(time_format)})"
                            f"]({item['description']})",
                            True,
                        )
                    }
                )
            else:
                default_field(fields, sub_time, item)
        for sub_time in cancelled_times:
            fields.pop(timegm(sub_time.utctimetuple()), None)
            times.discard(sub_time)
        bot_user = self.bot.user
        assert isinstance(bot_user, discord.ClientUser)  # skipcq: BAN-B101
        if self.message is MISSING:
            self.message = await self.webhook.send(
                username=bot_user.name,
                avatar_url=bot_user.display_avatar.url,
                embed=calendar_embed(fields, min(times, default=None)),
                wait=True,
            )
        elif utcnow() > self.week_end:
            await self.message.delete()
            self.message = await self.webhook.send(
                username=bot_user.name,
                avatar_url=bot_user.display_avatar.url,
                embed=calendar_embed(fields, min(times, default=None)),
                wait=True,
            )
            self.week_end += timedelta(days=7)
        else:
            self.message = await self.message.edit(embed=calendar_embed(fields, min(times, default=None)))


async def setup(bot: CBot):
    """Load the cog to the bot.

    Parameters
    ----------
    bot : commands.Bot
        The bot to load the cog to.
    """
    await bot.add_cog(Calendar(bot))
