# -*- coding: utf-8 -*-
"""Dynamic stream calendar generator for the next week."""

import datetime as _datetime
import re
from calendar import timegm
from datetime import datetime, time, timedelta, timezone
from typing import Literal, NamedTuple, Optional, TypedDict, cast
from zoneinfo import ZoneInfo

import discord
import itertools
import orjson
from discord.ext import commands, tasks
from discord.utils import MISSING, format_dt, utcnow
from typing_extensions import NotRequired
from validators import url

from . import CBot, Config


ytLink = "https://www.youtube.com/charliepryor/live"
chartime = ZoneInfo("US/Michigan")
time_format = "%H:%M %x %Z"


class EmbedField(NamedTuple):
    """A named tuple for an embed field."""

    name: str
    value: str
    inline: bool


class CalEventTime(TypedDict):
    """A typed dictionary for a calendar event time."""

    dateTime: str
    timeZone: str


class CalEvent(TypedDict):
    """A typed dictionary for a calendar event."""

    status: Literal["cancelled", "tentative", "confirmed"]
    created: str
    updated: str
    summary: str
    description: NotRequired[str]  # Not required, YT link is used as a fallback
    recurrence: NotRequired[list[str]]  # Not required, Only used if it exists to filter out an event
    start: CalEventTime
    end: CalEventTime
    originalStartTime: CalEventTime


class CalResponse(TypedDict):
    """A typed dictionary for the response from the Google calendar API."""

    items: list[CalEvent]


def get_params(mintime: datetime, maxtime: datetime) -> dict[str, str]:
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
    return {
        "key": Config["calendar"]["key"],
        "singleEvents": "True",
        "timeMin": mintime.isoformat(),
        "timeMax": maxtime.isoformat(),
    }


def half_hour_intervals():
    """Generate a list of half-hour intervals.

    Yields
    ------
    time
        The times for the interval.
    """
    for hour, minute in itertools.product(range(24), range(0, 60, 30)):
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


def default_field(dictionary: dict[int, EmbedField], add_time: datetime, item: CalEvent) -> None:
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
    dictionary[timegm(add_time.utctimetuple())] = EmbedField(
        item["summary"],
        f"{format_dt(add_time, 'F')}\n[({add_time.astimezone(chartime).strftime(time_format)})]({ytLink})",
        True,
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
    field: EmbedField
    for field in list(fields.values()):
        embed.add_field(name=field.name, value=field.value, inline=field.inline)

    embed.set_author(
        name="Charlie",
        icon_url="https://cdn.discordapp.com/avatars/225344348903047168/"
        "c093900592dfcd9b9e5c711f4e1c627d.webp?size=160",
    )
    return embed.set_footer(text="Last Updated")


def update_time(convert: datetime) -> datetime:  # pragma: no cover
    """Update the time to the correct week.

    Parameters
    ----------
    convert : datetime
        The time to update.

    Returns
    -------
    datetime
        The updated time.
    """
    while convert < utcnow():
        convert = convert + timedelta(days=7)
    return convert


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
    """

    reccurence_regex = re.compile(
        r"RRULE:FREQ=WEEKLY;UNTIL=(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})T"
        r"(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"
    )  # in case this is ever needed, leaving it in

    def __init__(self, bot: CBot):
        self.bot: CBot = bot
        self.message: discord.WebhookMessage = MISSING
        self.week_end = (
            utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            - timedelta(days=utcnow().weekday())
            + timedelta(days=7)
        )
        self.webhook: Optional[discord.Webhook] = MISSING
        self.calendar.change_interval(time=list(half_hour_intervals()))

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Unload hook."""
        self.calendar.cancel()
        self.bot.holder["message"] = self.message
        self.bot.holder["webhook"] = self.webhook

    async def cog_load(self) -> None:
        """Load hook."""
        self.webhook = self.bot.holder.pop("webhook", None) or await self.bot.fetch_webhook(
            Config["discord"]["webhooks"]["calendar"]
        )
        self.message = self.bot.holder.pop("message", MISSING)
        self.calendar.start()

    @commands.command(hidden=True, name="calendar")
    @commands.is_owner()
    async def refresh(self, ctx: commands.Context) -> None:  # pragma: no cover
        """Refresh the calendar message.

        Parameters
        ----------
        ctx : commands.Context
            The context of the command.
        """
        await self.calendar()
        await ctx.message.add_reaction("✅")

    @tasks.loop()
    async def calendar(self):
        """Calendar loop.

        This loop is responsible for posting the calendar every half hour.
        It queries the Google calendar API and posts the results to the
        webhook, after parsing and formatting the results.
        """
        mindatetime = datetime.now(tz=ZoneInfo("America/New_York"))
        maxdatetime = datetime.now(tz=ZoneInfo("America/New_York")) + timedelta(weeks=1)
        async with self.bot.session.get(
            "https://www.googleapis.com/calendar/v3/calendars/"
            "u8n1onpbv9pb5du7gssv2md58s@group.calendar.google.com/events",
            params=get_params(mindatetime, maxdatetime),
        ) as response:
            items: CalResponse = await response.json(loads=orjson.loads)
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
            if sub_time < utcnow():
                continue
            if flag:
                times.add(sub_time)  # pragma: no cover
            if mindatetime < sub_time > maxdatetime:
                continue
            desc = item.get("description", None)
            if desc is None:  # pragma: no cover
                default_field(fields, sub_time, item)
            else:  # pragma: no cover
                if url(desc):
                    fields[timegm(sub_time.utctimetuple())] = EmbedField(
                        f"{item['summary']}",
                        f"{format_dt(sub_time, 'F')}\n[({sub_time.astimezone(chartime).strftime(time_format)})"
                        f"]({desc})",
                        True,
                    )

                else:
                    default_field(fields, sub_time, item)
        for sub_time in cancelled_times:
            fields.pop(timegm(sub_time.utctimetuple()), None)
            times.discard(sub_time)
        if self.message is MISSING:  # pragma: no branch
            self.message = await cast(discord.Webhook, self.webhook).fetch_message(
                Config["discord"]["messages"]["calendar"]
            )
        self.message = await self.message.edit(embed=calendar_embed(fields, min(times, default=None)))


async def setup(bot: CBot):  # pragma: no cover
    """Load the cog to the bot.

    Parameters
    ----------
    bot : commands.Bot
        The bot to load the cog to.
    """
    await bot.add_cog(Calendar(bot))
