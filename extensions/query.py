import os
import time

import lightbulb
from lightbulb import commands

from auxone import checks

QueryPlugin = lightbulb.Plugin("QueryPlugin")

@QueryPlugin.command
@lightbulb.add_checks(lightbulb.Check(checks.Punished))
@lightbulb.command("time", "display's charlie's time",guilds=[225345178955808768])
@lightbulb.implements(commands.SlashCommand)
async def command(ctx):
    os.environ['TZ'] = 'US/Eastern'
    time.tzset()
    await ctx.respond("Charlie's time is: " + time.strftime('%X %x %Z'))

def load(bot):bot.add_plugin(QueryPlugin)
def unload(bot):bot.remove_plugin(QueryPlugin)
