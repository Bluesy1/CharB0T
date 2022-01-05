import os
import time

import lightbulb
from lightbulb import commands

def Punished(context):
        roles = context.member.role_ids
        for role in roles:
            if role in [684936661745795088,676250179929636886]:
                return False
        #if context.author.id == 920994579342311465: return False
        return True 

QueryPlugin = lightbulb.Plugin("QueryPlugin")

@QueryPlugin.command
@lightbulb.add_checks(lightbulb.Check(Punished))
@lightbulb.command("time", "display's charlie's time",guilds=[225345178955808768])
@lightbulb.implements(commands.SlashCommand)
async def command(ctx):
    os.environ['TZ'] = 'US/Eastern'
    time.tzset()
    await ctx.respond("Charlie's time is: " + time.strftime('%X %x %Z'))

def load(bot):bot.add_plugin(QueryPlugin)
def unload(bot):bot.remove_plugin(QueryPlugin)
