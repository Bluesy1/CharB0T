#pylint: disable=invalid-name
import json
import os
import sys
import time
from datetime import datetime, timedelta
import traceback

import hikari
import lightbulb
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from hikari import iterators, snowflakes
from hikari.embeds import Embed
from hikari.intents import Intents
from hikari.internal.time import utc_datetime
from hikari.messages import Message
from lightbulb import commands

def main():#pylint: disable=too-many-statements
    """Main"""
    global retries
    if os.name != "nt":
        import uvloop#pylint: disable=import-outside-toplevel
        uvloop.install()

    with open('token2.json') as file:
        token = json.load(file)['token']
    # Instantiate a Bot instance
    bot = lightbulb.BotApp(token=token, prefix="c?", default_enabled_guilds=225345178955808768, 
        owner_ids=[225344348903047168, 363095569515806722],logs={
            "version": 1,
            "incremental": True,
            "loggers": {
                "hikari": {"level": "INFO"},
                "hikari.ratelimits": {"level": "TRACE_HIKARI"},
                "lightbulb": {"level": "INFO"},
            },},case_insensitive_prefix_commands=True,delete_unbound_commands=False,intents=Intents.ALL)
    sched = AsyncIOScheduler()
    sched.start()

    async def create_task(run_time: datetime,
                          guild_id: snowflakes.Snowflakeish,member_id: snowflakes.Snowflakeish):
        """Creates a Scheduled Untimeout"""
        async def log_untimeout()->None:
            """Untimeout Report Method"""
            member = await bot.rest.fetch_member(guild_id, member_id)
            timeoutStill = member.communication_disabled_until()
            if not timeoutStill:
                await bot.rest.create_message(426016300439961601,
                                              embed=Embed(color="0x00ff00")
                                                .set_author(icon=member.avatar_url,
                                                            name=f"[UNTIMEOUT] {member.username}#{member.discriminator}")
                                                .add_field("User",member.mention,inline=True))
            elif timeoutStill:
                await create_task(timeoutStill, member.guild_id, member.id)
        sched.add_job(log_untimeout, DateTrigger(run_date=run_time),
                      id=f"{guild_id}-{member_id}", replace_existing=True)

    @bot.command()
    @lightbulb.add_checks(lightbulb.owner_only)
    @lightbulb.command("ping", "Checks that the bot is alive")
    @lightbulb.implements(commands.PrefixCommand)
    async def ping(ctx):#pylint: disable=unused-variable
        await ctx.event.message.delete()
        await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency*1000:.2f}ms")
    @bot.listen(hikari.DMMessageCreateEvent)
    async def on_dm_message(event: hikari.DMMessageCreateEvent) -> None:#pylint: disable=unused-variable
        if event.is_human:
            await event.author.send("Hi! If this was an attempt to reach the mod team through modmail, you've messaged the wrong bot sadly. Please message <@406885177281871902> (CharB0T#3153) instead. We apologize for the confusion of having 2 identically named bots, and hope you will still reach out if you were meaning to!")

    @bot.listen(hikari.MemberUpdateEvent)
    async def on_member_update(event: hikari.MemberUpdateEvent):#pylint: disable=unused-variable
        try:
            if event.member.communication_disabled_until() != event.old_member.communication_disabled_until():
                if event.member.raw_communication_disabled_until is not None:
                    td = event.member.communication_disabled_until() + timedelta(seconds=1) - utc_datetime()
                    timedeltastring = ""
                    if td.days // 7 != 0:
                        timedeltastring += f"{td.days // 7} Week{'s' if td.days // 7 > 1 else ''}"
                    if td.days % 7 !=0 :
                        timedeltastring += f"{', 'if bool(timedeltastring)else ''}{td.days % 7} Day{'s' if td.days % 7 > 1 else ''} "
                    if td.seconds // 3600 > 0:
                        timedeltastring += f"{', 'if bool(timedeltastring)else ''}{td.seconds // 3600} Hour{'s' if td.seconds // 3600 > 1 else ''} "
                    if (td.seconds % 3600) // 60 != 0:
                        timedeltastring += f"{', 'if bool(timedeltastring)else ''}{(td.seconds % 3600) // 60} Minute{'s' if (td.seconds % 3600) // 60 > 1 else ''} "
                    if (td.seconds % 3600) % 60 !=0 :
                        timedeltastring += f"{', 'if bool(timedeltastring)else ''}{(td.seconds % 3600) % 60} Second{'s' if (td.seconds % 3600) % 60 > 1 else ''}"
                    embed = Embed(color="0xff0000")
                    embed.set_author(icon=event.member.avatar_url,
                                     name=f"[TIMEOUT] {event.member.username}#{event.member.discriminator}")
                    embed.add_field("User", event.member.mention,inline=True)
                    embed.add_field("Duration", timedeltastring,inline=True)
                    await bot.rest.create_message(426016300439961601, embed=embed)
                    await create_task(event.member.communication_disabled_until(),
                                      event.guild_id, event.member.id)
                else:
                    embed = Embed(color="0x00ff00")
                    embed.set_author(icon=event.member.avatar_url,
                                     name=f"[UNTIMEOUT] {event.member.username}#{event.member.discriminator}")
                    embed.add_field("User", event.member.mention, inline=True)
                    await bot.rest.create_message(426016300439961601, embed=embed)
                    sched.remove_job(f"{event.guild_id}-{event.member.id}")
                
        except:#pylint: disable=bare-except
            if event.member.raw_communication_disabled_until is not None:
                td = event.member.communication_disabled_until() + timedelta(seconds=1) - utc_datetime()
                timedeltastring = ""
                if td.days // 7 != 0:
                    timedeltastring += f"{td.days // 7} Week{'s' if td.days // 7 > 1 else ''}"
                if td.days%7!=0:
                    timedeltastring += f"{', 'if bool(timedeltastring)else ''}{td.days % 7} Day{'s' if td.days % 7 > 1 else ''} "
                if td.seconds // 3600 > 0:
                    timedeltastring += f"{', 'if bool(timedeltastring)else ''}{td.seconds // 3600} Hour{'s' if td.seconds // 3600 > 1 else ''} "
                if (td.seconds % 3600) // 60 != 0:
                    timedeltastring += f"{', 'if bool(timedeltastring)else ''}{(td.seconds % 3600) // 60} Minute{'s' if (td.seconds % 3600) // 60 > 1 else ''} "
                if (td.seconds % 3600) % 60 != 0:
                    timedeltastring += f"{', 'if bool(timedeltastring)else ''}{(td.seconds % 3600) % 60} Second{'s' if (td.seconds% 3600) % 60 >1 else ''}"
                embed = Embed(color="0xff0000")
                embed.set_author(icon=event.member.avatar_url,
                                 name=f"[TIMEOUT] {event.member.username}#{event.member.discriminator}")
                embed.add_field("User", event.member.mention, inline=True)
                embed.add_field("Duration", timedeltastring, inline=True)
                await bot.rest.create_message(426016300439961601, embed=embed)
                await create_task(event.member.communication_disabled_until(), event.guild_id, event.member.id)

    @bot.listen(hikari.MemberDeleteEvent)
    async def on_member_leave(event: hikari.MemberDeleteEvent):#pylint: disable=unused-variable
        if event.old_member:
            delta = time.time() - time.mktime(event.old_member.joined_at.utctimetuple())
            minutes, sec = divmod(delta, 60)
            hour, minutes = divmod(minutes, 60)
            day, hour = divmod(hour, 24)
            year, day = divmod(day, 365)
            timedeltastring = ("{0} Year(s), {1} Day(s), {2} Hour(s), {3} Min(s), {4} Sec(s)"
                                .format(year, day, hour, minutes, sec))
        else:
            channel = await bot.rest.fetch_channel(430197357100138497)
            messages: iterators.LazyIterator[Message] = await channel.fetch_history(before=datetime.utcnow())
            try:
                messages = messages.filter(("message.author.is_bot",True))
            except:
                None#pylint: disable=pointless-statement
            messages = messages.reversed()
            timedeltastring = "None Found"
            async for item in messages:
                mentions = item.mentions.get_members()
                if event.user_id in mentions.keys:
                    delta = time.time() - time.mktime(item.created_at.utctimetuple())
                    minutes, sec = divmod(delta, 60)
                    hour, minutes = divmod(minutes, 60)
                    day, hour = divmod(hour, 24)
                    year, day = divmod(day, 365)
                    timedeltastring = ("{0} Year(s), {1} Day(s), {2} Hour(s), {3} Min(s), {4} Sec(s)"
                                        .format(year, day, hour, minutes, sec))
        await bot.rest.create_message(430197357100138497,
                                      f"**{event.user.username}#{event.user.discriminator}** has left the server. ID:{event.user_id}. Time on Server: {timedeltastring}")



    # Run the bot
    # Note that this is blocking meaning no code after this line will run
    # until the bot is shut off
    retries = 0
    def remove_retry():
        """Removes a Retry"""
        global retries
        retries -= 1
    try:
        bot.run()
    except KeyboardInterrupt:
        traceback.print_exc()
        sys.exit()
    except hikari.ComponentStateConflictError:
        traceback.print_exc()
        sys.exit()
    except TypeError:
        traceback.print_exc()
        sys.exit()
    except:
        if retries<11:
            time.sleep(10)
            retries+=1
            sched.add_job(remove_retry,DateTrigger(datetime.utcnow() + timedelta(minutes=30)))
            print(f"Bot Closed, Trying to restart, try {retries}/10")
            main()
        else:
            traceback.print_exc()
            sys.exit()

if __name__ == "__main__":
    main()
