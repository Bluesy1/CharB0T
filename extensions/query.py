import os
import time

import lightbulb
from lightbulb import commands

from helper import punished

QueryPlugin = lightbulb.Plugin("QueryPlugin")


@QueryPlugin.command
@lightbulb.add_checks(punished)
@lightbulb.command("time", "display's charlie's time", guilds=[225345178955808768])
@lightbulb.implements(commands.SlashCommand)
async def command(ctx):
    """Returns eastern time"""
    os.environ["TZ"] = "US/Eastern"
    time.tzset()
    await ctx.respond("Charlie's time is: " + time.strftime("%X %x %Z"))


def load(bot):
    """Loads the plugin"""
    bot.add_plugin(QueryPlugin)


def unload(bot):
    """Unloads the plugin"""
    bot.remove_plugin(QueryPlugin)
