import datetime
import time
import auxone as a
from hikari import Embed
import lightbulb
from lightbulb import commands
import random
from lightbulb.checks import has_roles

Generating_Plugin = lightbulb.Plugin("Generating_Plugin")


# Adding the check to a command

@Generating_Plugin.command()
@lightbulb.add_checks(lightbulb.Check(has_roles(837812373451702303,837812586997219372,837812662116417566,837812728801525781,837812793914425455,400445639210827786,685331877057658888,337743478190637077,837813262417788988,338173415527677954,253752685357039617,mode=any)),lightbulb.Check(a.checks.check_econ_channel),lightbulb.Check(a.checks.Punished))
@lightbulb.add_cooldown(3600,5,lightbulb.UserBucket)
@lightbulb.command("daily", "daily command")
@lightbulb.implements(commands.SlashCommand)
async def command(ctx):
    if str(ctx.author.id) not in list(a.userInfo.readUserInfo().index): #makes sure user isn't already in an RPO
        a.undeclared(ctx)
    df = a.userInfo.readUserInfo()
    lastWork = df.loc[str(ctx.author.id), 'lastDaily']
    currentUse = round(time.time(),0)
    timeDifference = currentUse - lastWork
    if timeDifference < 71700:
        await ctx.author.send("<:KSplodes:896043440872235028> Error: **" + ctx.author.mention + "** You need to wait " + str(datetime.timedelta(seconds=71700-timeDifference)) + " more to use this command.")
    elif timeDifference > 71700:
        df.loc[str(ctx.author.id), 'lastDaily'] = currentUse
        amount = 1500 #assigned number for daily
        a.userInfo.writeUserInfo(df)
        a.userInfo.editCoins(ctx.author.id,amount)
        await ctx.author.send(embed=Embed(description= ctx.author.mention +', here is your daily reward: 1500 <:HotTips2:465535606739697664>', color="60D1F6").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url))

@Generating_Plugin.command()
@lightbulb.add_checks(lightbulb.Check(has_roles(837812373451702303,837812586997219372,837812662116417566,837812728801525781,837812793914425455,400445639210827786,685331877057658888,337743478190637077,837813262417788988,338173415527677954,253752685357039617,mode=any)),lightbulb.Check(a.checks.check_econ_channel),lightbulb.Check(a.checks.Punished))
@lightbulb.add_cooldown(3600,5,lightbulb.UserBucket)
@lightbulb.command("work", "work command")
@lightbulb.implements(commands.SlashCommand)
async def work(ctx):
    df = a.userInfo.readUserInfo()
    if str(ctx.author.id) not in list(a.userInfo.readUserInfo().index): #makes sure user isn't already in an RPO
        a.undeclared(ctx)
    lastWork = df.loc[str(ctx.author.id), 'lastWork']
    currentUse = round(time.time(),0)
    timeDifference = currentUse - lastWork
    if timeDifference < 41400:
        await ctx.respond("<:KSplodes:896043440872235028> Error: **" + ctx.author.mention + "** You need to wait " + str(datetime.timedelta(seconds=41400-timeDifference)) + " more to use this command.")
    elif timeDifference > 41400:
        df.loc[str(ctx.author.id), 'lastWork'] = currentUse
        amount = random.randrange(800, 1200, 5) #generates random number from 800 to 1200, in incrememnts of 5 (same as generating a radom number between 40 and 120, and multiplying it by 5)
        lastamount = int(df.loc[str(ctx.author.id), 'lastWorkAmount'])
        df.loc[str(ctx.author.id), 'lastWorkAmount'] = amount
        a.userInfo.writeUserInfo(df)
        a.userInfo.editCoins(ctx.author.id,lastamount)
        df.loc[str(ctx.author.id), 'lastWorkAmount'] = amount
        embed = Embed(description= ctx.author.mention + ', you started working again. You gain '+ str(lastamount) +' <:HotTips2:465535606739697664> from your last work. Come back in **12 hours** to claim your paycheck of '+ str(amount) + ' <:HotTips2:465535606739697664> and start working again with `!work`', color="60D1F6").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url)
        await ctx.respond(embed=embed)

def load(bot):
    bot.add_plugin(Generating_Plugin)

def unload(bot):
    bot.remove_plugin(Generating_Plugin)