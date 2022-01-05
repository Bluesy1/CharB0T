import json
import logging
import os
import re
from cryptography.fernet import Fernet
import hikari
from hikari import guilds
from hikari.intents import Intents
from hikari.presences import Activity, ActivityType

import lightbulb
from lightbulb import commands
import pandas as pd

import auxone as a
from auxone import userInfo as user
if os.name != "nt":
    import uvloop
    uvloop.install()

with open('bottoken.json') as t:
    token = json.load(t)['Token']
# Instantiate a Bot instance
bot = lightbulb.BotApp(token=token, prefix="!", help_slash_command=True,owner_ids=[225344348903047168, 363095569515806722],logs={
        "version": 1,
        "incremental": True,
        "loggers": {
            "hikari": {"level": "INFO"},
            "hikari.ratelimits": {"level": "TRACE_HIKARI"},
            "lightbulb": {"level": "INFO"},
        },},case_insensitive_prefix_commands=True,intents=Intents.ALL, default_enabled_guilds=225345178955808768)

#bot.load_extensions("extensions.events")

def check_author_is_me(context):
    # Returns True if the author's ID is the same as the given one
    return context.author.id == 363095569515806722
def check_econ_channel(context):
    return context.channel_id in [893867549589131314, 687817008355737606, 839690221083820032]


@bot.command()
@lightbulb.option("module", "module to reload", required=True)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("reload", "reloads extensions")
@lightbulb.implements(commands.PrefixCommand)
async def reload(ctx) -> None:
    # Send a message to the channel the command was used in
    bot.reload_extensions("extensions."+ctx.options.module)
    await ctx.respond("Reloaded!")

@bot.command()
@lightbulb.option("module", "module to load", required=True)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("load", "loads given extensions")
@lightbulb.implements(commands.PrefixCommand)
async def load(ctx) -> None:
    # Send a message to the channel the command was used in
    bot.load_extensions("extensions."+ctx.options.module)
    await ctx.respond("Loaded!")

@bot.command()
@lightbulb.option("module", "module to unload", required=True)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("unload", "unloads given extensions")
@lightbulb.implements(commands.PrefixCommand)
async def load(ctx) -> None:
    # Send a message to the channel the command was used in
    bot.unload_extensions("extensions."+ctx.options.module)
    await ctx.respond("Unloaded!")

@bot.command()
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("ping", "Checks that the bot is alive")
@lightbulb.implements(commands.PrefixCommand)
async def ping(ctx):
    await ctx.event.message.delete()
    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency*1000:.2f}ms")
    with open('filekey.key','rb') as file:
        key = file.read()
    fernet = Fernet(key)
    df = pd.DataFrame(json.loads(fernet.decrypt(open('UserInfo.json',"rb").read())))
    with open('UserInfo.json','wb') as t:
        t.write(fernet.encrypt(json.dumps(df.to_dict()).encode('utf-8')))
    for id in list(df.index):
        try:member:guilds.Member = await bot.rest.fetch_member(225345178955808768,int(id))
        except: continue
        name = member.display_name
        newname, count = re.subn("(?<=[\[\(])[^\[\]]{2,4}(?=\]\()","",name)
        if newname != name:
            await member.edit(nick=newname)
bot.load_extensions_from("extensions")
bot.load_extensions("extensions.__help")


# Run the bot
# Note that this is blocking meaning no code after this line will run
# until the bot is shut off
bot.run(activity=Activity(name="for scammers",type=ActivityType.WATCHING))#activity=Activity())
