import re

import pandas as pd
import auxone as a
from hikari import Embed
import lightbulb
from lightbulb import commands
from lightbulb.checks import has_roles

RPO_Plugin = lightbulb.Plugin("RPO_Plugin")

@RPO_Plugin.command()
@lightbulb.option("rpo", "RPO to join", required=True)
@lightbulb.add_checks(lightbulb.Check(has_roles(837812373451702303,837812586997219372,837812662116417566,837812728801525781,837812793914425455,400445639210827786,685331877057658888,337743478190637077,837813262417788988,338173415527677954,253752685357039617,mode=any)),lightbulb.Check(a.checks.check_econ_channel),lightbulb.Check(a.checks.Punished))
@lightbulb.add_cooldown(300,3,lightbulb.UserBucket)
@lightbulb.command("joinrpo", "Joins an RPO",guilds=[225345178955808768])
@lightbulb.implements(commands.SlashCommand)
async def joinRPO(ctx):
    author = ctx.member
    userid = author.id
    userInfo = a.userInfo.readUserInfo()
    RPO  = ctx.options.rpo.upper()
    if str(ctx.author.id) in list(a.userInfo.readUserInfo().index): #makes sure user isn't already in an RPO
        if a.userInfo.readUserInfo().loc[str(ctx.author.id), 'RPO'] == 'A':
            await ctx.respond("<:KSplodes:896043440872235028> Error: You have already been registered as undeclared. To change your status, please use `!changeRPO` followed by your new tag.")
            return
        else:
            await ctx.respond("<:KSplodes:896043440872235028> Error: You are already in an RPO: " + userInfo.loc[str(userid), 'RPO'])
            return
    elif RPO not in pd.read_csv(a.RPOInfoURL, index_col=0, usecols=['FULL NAME', 'TAG'])['TAG'].astype(str).to_list(): #makes sure RPO trying to be joined exists
        if RPO == 'A': a.undeclared(ctx)
        else:
            await ctx.respond("<:KSplodes:896043440872235028> Error: RPO " +RPO + " is not a registered RPO")
            return
    elif RPO == 'CP':
        await ctx.respond("<:KSplodes:896043440872235028> Error: You cannot join the RPO CP")
    elif str(userid) not in list(a.userInfo.readUserInfo().index):
        rpo = RPO
        newUser = {'userID':[str(userid)], 'RPO':RPO, 'Author':[str(author.username)], 'Coin Amount': [0], 'lastWorkAmount': [0], 'lastWork': [0], 'lastDaily': [0]}
        df = a.userInfo.readUserInfo()
        userList = df.append(pd.DataFrame(newUser).set_index('userID'))
        a.userInfo.writeUserInfo(userList)
        name = ctx.member.display_name
        try:
            newname, count = re.subn("(?<=\[)[^\[\]]{2,4}(?=\])",RPO,name)
            if (count == 0): newname = name + " [" + RPO + "]"
        except: None
        if len(newname) <=32:
            await ctx.member.edit(nick=newname)
            await ctx.member.add_role(906000578092621865)
        else:await ctx.member.add_role(906000578092621865)
        await ctx.respond(ctx.member.mention + " you are now in RPO " + rpo)

@RPO_Plugin.command()
@lightbulb.option("rpo", "RPO to change to", required=True)
@lightbulb.add_checks(lightbulb.Check(has_roles(837812373451702303,837812586997219372,837812662116417566,837812728801525781,837812793914425455,400445639210827786,685331877057658888,337743478190637077,837813262417788988,338173415527677954,253752685357039617,mode=any)),lightbulb.Check(a.checks.check_econ_channel),lightbulb.Check(a.checks.Punished))
@lightbulb.add_cooldown(86400,1,lightbulb.UserBucket)
@lightbulb.command("changerpo", "Changes what RPO you're in")
@lightbulb.implements(commands.SlashCommand)
async def changeRPO(ctx):
    author = ctx.author
    userid = author.id
    RPO  = ctx.options.rpo.upper()
    info = a.userInfo.readUserInfo()
    currentRPO = a.userInfo.readUserInfo().loc[str(ctx.author.id),"RPO"]
    if RPO not in pd.read_csv(a.RPOInfoURL, index_col=0, usecols=['FULL NAME', 'TAG'])['TAG'].astype(str).to_list():
        await ctx.respond("<:KSplodes:896043440872235028> Error: RPO " +RPO + " is not a registered RPO")
        return
    elif RPO == 'CP' or currentRPO=='CP':
        await ctx.respond("<:KSplodes:896043440872235028> Error: You cannot change to or leave the RPO CP")
    else:
        df = a.userInfo.readUserInfo()
        df.loc[str(ctx.author.id), 'RPO'] = RPO
        a.userInfo.writeUserInfo(df)
        name = ctx.member.display_name
        try:
            newname, count = re.subn("(?<=\[)[^\[\]]{2,4}(?=\])",RPO,name)
            if (count == 0): newname = name + " [" + RPO + "]"
        except: None
        if len(newname) <=32:
            await ctx.member.edit(nick=newname)
            await ctx.member.add_role(906000578092621865)
        else:await ctx.member.add_role(906000578092621865)
        await ctx.respond(ctx.author.mention + " you are now in RPO " + RPO)




def load(bot):
    bot.add_plugin(RPO_Plugin)

def unload(bot):
    bot.remove_plugin(RPO_Plugin)