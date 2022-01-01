import json
import os
import hikari

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
        },},case_insensitive_prefix_commands=True,)

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


# Run the bot
# Note that this is blocking meaning no code after this line will run
# until the bot is shut off
bot.run()#activity=Activity())
