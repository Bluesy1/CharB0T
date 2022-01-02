import asyncio
from datetime import timedelta
import json
import os
import hikari
from hikari.embeds import Embed
from hikari.intents import Intents
from hikari.internal.time import utc_datetime

import lightbulb
from lightbulb import commands

if os.name != "nt":
    import uvloop
    uvloop.install()

with open('token2.json') as t:
    token = json.load(t)['token']
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

@bot.command()
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("ping", "Checks that the bot is alive")
@lightbulb.implements(commands.PrefixCommand)
async def ping(ctx):
    await ctx.event.message.delete()
    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency*1000:.2f}ms")
@bot.listen(hikari.DMMessageCreateEvent)
async def on_dm_message(event: hikari.DMMessageCreateEvent) -> None:
    if event.is_human:
        await event.author.send("Hi! If this was an attempt to reach the mod team through modmail, you've messaged the wrong bot sadly. Please message <@406885177281871902> (CharB0T#3153) instead. We apologize for the confusion of having 2 identically named bots, and hope you will still reach out if you were meaning to!")

@bot.listen(hikari.MemberUpdateEvent)
async def on_member_update(event: hikari.MemberUpdateEvent):
    try:
        if event.member.communication_disabled_until() != event.old_member.communication_disabled_until():
            if event.member.raw_communication_disabled_until is not None:
                td = event.member.communication_disabled_until() +timedelta(seconds=1) - utc_datetime()
                timedeltastring = ""
                if td.days//7!=0:timedeltastring+=f"{td.days//7} Week{'s' if td.days//7>1 else ''}"
                if td.days%7!=0:timedeltastring+=f"{', 'if bool(timedeltastring)else ''}{td.days%7} Day{'s' if td.days%7>1 else ''} "
                if td.seconds//3600 >0:timedeltastring+=f"{', 'if bool(timedeltastring)else ''}{td.seconds//3600} Hour{'s' if td.seconds//3600>1 else ''} "
                if (td.seconds%3600)//60!=0:timedeltastring+=f"{', 'if bool(timedeltastring)else ''}{(td.seconds%3600)//60} Minute{'s' if (td.seconds%3600)//60>1 else ''} "
                if (td.seconds%3600)%60!=0:timedeltastring+=f"{', 'if bool(timedeltastring)else ''}{(td.seconds%3600)%60} Second{'s' if (td.seconds%3600)%60>1 else ''}"
                embed = Embed(color="0xff0000").set_author(icon=event.member.avatar_url,name=f"[TIMEOUT] {event.member.username}#{event.member.discriminator}").add_field("User",event.member.mention,inline=True).add_field("Duration",timedeltastring,inline=True)
                await bot.rest.create_message(926532222398369812,embed=embed)
                if td.days< 0 or td.seconds <0:
                    embed = Embed(color="0x00ff00").set_author(icon=event.member.avatar_url,name=f"[UNTIMEOUT] {event.member.username}#{event.member.discriminator}").add_field("User",event.member.mention,inline=True)
                    member_id=event.member.id;guild_id = event.guild_id
                    await asyncio.sleep(td.seconds+(td.days*86400)-3)
                    member = await bot.rest.fetch_member(guild_id,member_id)
                    timeout_still = member.communication_disabled_until()
                    if timeout_still: await bot.rest.create_message(926532222398369812,embed=embed)
            else:
                embed = Embed(color="0x00ff00").set_author(icon=event.member.avatar_url,name=f"[UNTIMEOUT] {event.member.username}#{event.member.discriminator}").add_field("User",event.member.mention,inline=True)
                await bot.rest.create_message(926532222398369812,embed=embed)
            
    except:
        if event.member.raw_communication_disabled_until is not None:
            td = event.member.communication_disabled_until() +timedelta(seconds=1) - utc_datetime()
            timedeltastring = ""
            if td.days//7!=0:timedeltastring+=f"{td.days//7} Week{'s' if td.days//7>1 else ''}"
            if td.days%7!=0:timedeltastring+=f"{', 'if bool(timedeltastring)else ''}{td.days%7} Day{'s' if td.days%7>1 else ''} "
            if td.seconds//3600 >0:timedeltastring+=f"{', 'if bool(timedeltastring)else ''}{td.seconds//3600} Hour{'s' if td.seconds//3600>1 else ''} "
            if (td.seconds%3600)//60!=0:timedeltastring+=f"{', 'if bool(timedeltastring)else ''}{(td.seconds%3600)//60} Minute{'s' if (td.seconds%3600)//60>1 else ''} "
            if (td.seconds%3600)%60!=0:timedeltastring+=f"{', 'if bool(timedeltastring)else ''}{(td.seconds%3600)%60} Second{'s' if (td.seconds%3600)%60>1 else ''}"
            embed = Embed(color="0xff0000").set_author(icon=event.member.avatar_url,name=f"[TIMEOUT] {event.member.username}#{event.member.discriminator}").add_field("User",event.member.mention,inline=True).add_field("Duration",timedeltastring,inline=True)
            await bot.rest.create_message(926532222398369812,embed=embed)
        if td.days< 0 or td.seconds <0:
            embed = Embed(color="0x00ff00").set_author(icon=event.member.avatar_url,name=f"[UNTIMEOUT] {event.member.username}#{event.member.discriminator}").add_field("User",event.member.mention,inline=True)
            member_id=event.member.id;guild_id = event.guild_id
            await asyncio.sleep(td.seconds+(td.days*86400)-3)
            member = await bot.rest.fetch_member(guild_id,member_id)
            timeout_still = member.communication_disabled_until()
            if timeout_still: await bot.rest.create_message(926532222398369812,embed=embed)



# Run the bot
# Note that this is blocking meaning no code after this line will run
# until the bot is shut off
bot.run()#activity=Activity())
