import json
import os
import time

import hikari
import lightbulb
import pandas as pd
import sfsutils
from auxone import (RPOKnowledgeURL, checks, ksptime, render_mpl_table,
                    rpoPortfolio, userInfo)
from hikari import Embed
from lightbulb import commands
from lightbulb.checks import has_roles

QueryPlugin = lightbulb.Plugin("QueryPlugin")

@QueryPlugin.command
@lightbulb.command("coins", "coin group")
@lightbulb.implements(commands.SlashCommandGroup)
async def coins(ctx) -> None: await ctx.respond("invoked coins")

@coins.child
@lightbulb.command("query", "query group")
@lightbulb.implements(commands.SlashSubGroup)
async def query(ctx) -> None: await ctx.respond("invoked coins query")

@query.child
@lightbulb.add_checks(lightbulb.Check(checks.Punished))
@lightbulb.command("me", "querys your coins", ephemeral=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    funds = userInfo.getCoins(ctx.author.id)
    await ctx.respond(embed=Embed(description=ctx.author.mention+"has " + str(funds) + '<:HotTips2:465535606739697664>', color="60D1F6").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url),flags=64)

@query.child
@lightbulb.add_checks(lightbulb.owner_only|lightbulb.Check(has_roles(338173415527677954,253752685357039617,225413350874546176,mode=any)))
@lightbulb.option("member", "member to query",type=hikari.Member,required=True)
@lightbulb.command("mod", "querys a member's coins", ephemeral=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    funds = userInfo.getCoins(ctx.options.member.id)
    await ctx.respond(embed=Embed(description=ctx.options.member.mention+"has " + str(funds) + '<:HotTips2:465535606739697664>', color="60D1F6").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url),flags=64)

@coins.child
@lightbulb.add_checks(lightbulb.owner_only|lightbulb.Check(has_roles(338173415527677954,253752685357039617,225413350874546176,mode=any)))
@lightbulb.option("member", "member to query",type=hikari.Member,required=True)
@lightbulb.option("amount", "amount to add/remove", type=int)
@lightbulb.command("edit", "edits a member's coins")
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    if ctx.options.amount == 0:
        embed = Embed(description='<:KSplodes:896043440872235028> Error: Cannot Add 0 funds.', color="60D1F6").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url)
    elif ctx.options.amount>0:
        userInfo.editCoins(str(ctx.options.member.id),ctx.options.amount)
        embed = Embed(description='✅' + str(abs(ctx.options.amount)) +'<:HotTips2:465535606739697664> has been given to ' + ctx.options.member.mention, color="60D1F6").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url)
    else: 
        output = userInfo.editCoins(str(ctx.options.member.id),ctx.options.amount)
        embed = Embed(description='✅' + str(output['changed']) +'<:HotTips2:465535606739697664> has been removed from ' + ctx.options.member.mention, color="60D1F6").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url) 
    await ctx.respond(embed=embed)

@QueryPlugin.command
@lightbulb.add_checks(lightbulb.Check(checks.Punished))
@lightbulb.command("time", "display's charlie's time")
@lightbulb.implements(commands.SlashCommand)
async def command(ctx):
    os.environ['TZ'] = 'US/Eastern'
    time.tzset()
    await ctx.respond("Charlie's time is: " + time.strftime('%X %x %Z'))

@QueryPlugin.command
@lightbulb.command("wallet", "wallet group")
@lightbulb.implements(commands.SlashCommandGroup)
async def wallet(ctx) -> None: await ctx.respond("invoked wallet")

@wallet.child
@lightbulb.add_checks(lightbulb.Check(has_roles(338173415527677954,253752685357039617,225413350874546176,mode=any)))
@lightbulb.command("mod", "mod wallet group")
@lightbulb.implements(commands.SlashSubGroup)
async def mod(ctx) -> None: await ctx.respond("invoked wallet-mod")

@mod.child
@lightbulb.option("member", "member to query",type=hikari.Member,required=True)
@lightbulb.command("query", "querys a member's rpo wallet", ephemeral=True, inherit_checks=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    wallets = userInfo.getWallet()
    UserInfo = userInfo.readUserInfo()
    rpo = UserInfo.loc[str(ctx.options.member.id),'RPO']
    wallet = wallets.loc[rpo, "Account Balance"]
    await ctx.respond(rpo+"'s balance is: "+str(wallet),flags=64)

@mod.child
@lightbulb.option("member", "member to query",type=hikari.Member,required=True)
@lightbulb.option("amount", "amount to add/remove", type=int)
@lightbulb.command("edit", "edits a member's rpo wallet", ephemeral=True, inherit_checks=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    rpo = userInfo.readUserInfo().loc[str(ctx.options.member.id),'RPO']
    output = userInfo.editWallet(rpo, ctx.options.amount)
    charged = output['changed']
    if ctx.options.amount>=0:
        embed = Embed(description='✅' + str(ctx.options.amount) +' 🪙 has been given to ' + str(rpo), color="60D1F6").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url)
    else:
        embed = Embed(description='✅' + str(charged) +' 🪙 has been removed from ' + str(rpo), color="60D1F6").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url)
    await ctx.respond(embed=embed, flags=64)

@wallet.child
@lightbulb.add_checks(lightbulb.Check(checks.Punished, has_roles(906000578092621865)))
@lightbulb.command("user", "user wallet group")
@lightbulb.implements(commands.SlashSubGroup)
async def user(ctx) -> None: await ctx.respond("invoked wallet-user")

@user.child
@lightbulb.command("query", "querys your RPO's wallet", ephemeral=True, inherit_checks=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    wallets = userInfo.getWallet()
    UserInfo = userInfo.readUserInfo()
    rpo = UserInfo.loc[str(ctx.author.id),'RPO']
    wallet = wallets.loc[rpo, "Account Balance"]
    await ctx.respond(rpo+"'s balance is: "+str(wallet),flags=64)

@user.child
@lightbulb.option("amount", "amount to send to wallet", type=int)
@lightbulb.command("send", "sends coins to your RPO's wallet", ephemeral=True, inherit_checks=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    rpo = userInfo.readUserInfo().loc[str(ctx.author.id),'RPO']
    if rpo == 'A' or rpo=='CP': 
        await ctx.respond("You are not registered in a valid RPO to the bot")
        return
    output = userInfo.editCoins(ctx.author.id, 0-ctx.options.amount)
    charged = output['changed']
    userInfo.editWallet(rpo,abs(charged))
    embed = Embed(description='✅' + str(charged) +'<:HotTips2:465535606739697664> has been removed from ' + str(ctx.author.mention) + ', and added to your RPO funds.', color="60D1F6").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url)
    await ctx.respond(embed=embed,flags=64)

@QueryPlugin.command
@lightbulb.command("rpo", "rpo group")
@lightbulb.implements(commands.SlashCommandGroup)
async def rpo_(ctx) -> None: await ctx.respond("invoked coins")

@rpo_.child
@lightbulb.add_checks(lightbulb.Check(checks.Punished, has_roles(906000578092621865)))
@lightbulb.command("user", "user wallet group")
@lightbulb.implements(commands.SlashSubGroup)
async def user(ctx) -> None: await ctx.respond("invoked rpo-user")

@user.child
@lightbulb.command("knowledge", "querys your RPO's knowledge", ephemeral=True, inherit_checks=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    author = ctx.author
    userid = author.id
    RPO = userInfo.readUserInfo().loc[str(ctx.author.id),'RPO']
    Knowledgedf = pd.read_csv(RPOKnowledgeURL).set_index("TAG").loc[RPO]
    Knowledgedict = Knowledgedf.to_dict()
    with open("ranges.json") as r:
        ranges = json.load(r)
    Keysname = list()
    Fieldsname = list()
    for item in list(Knowledgedict.keys()):
        for Range in list(ranges.keys()):
            if str(Knowledgedict[item]) == '-%':
                Keysname.append(item)
                Fieldsname.append("Little/none")
                break
            try:
                val = float(str(Knowledgedict[item])[:-1])/100
            except:
                break
            lowerBound = float(ranges[Range]['lowerBound'])
            upperBound = float(ranges[Range]['upperBound'])
            if (val >= lowerBound) and (val <= upperBound):
                Keysname.append(item)
                Fieldsname.append(ranges[Range]["name"])
                break
    dfOut = pd.DataFrame()
    dfOut['Field'] = Keysname
    dfOut['Knowledge Level'] = Fieldsname
    #imageTable = render_mpl_table(dfOut, header_columns=0, col_width=2.0)
    render_mpl_table(dfOut, header_columns=0, col_width=5.0)
    await ctx.respond(Embed(title="Knowledge").set_image('table.png'),flags=64)
    os.remove('table.png')

@user.child
@lightbulb.command("portfolio", "querys your RPO's portfolio, if it exists", ephemeral=True, inherit_checks=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    rpo = userInfo.readUserInfo().loc[str(ctx.author.id),'RPO']
    hasInvested = rpoPortfolio(rpo.upper())
    if hasInvested:
        message = await ctx.author.send("See attached")
        await message.edit(attachment='multipage.pdf')
    else:
        await ctx.respond("No investments recorded for your RPO.", flags=64)

@rpo_.child
@lightbulb.add_checks(lightbulb.Check(has_roles(914969502037467176))|lightbulb.owner_only)
@lightbulb.command("cp", "user wallet group")
@lightbulb.implements(commands.SlashSubGroup)
async def cp(ctx) -> None: await ctx.respond("invoked rpo-cp")

@cp.child
@lightbulb.option("member", "member to query",type=hikari.Member,required=True)
@lightbulb.command("knowledge", "querys a member RPO's knowledge", ephemeral=True, inherit_checks=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    author = ctx.author
    userid = author.id
    RPO = userInfo.readUserInfo().loc[str(ctx.options.member.id),'RPO']
    Knowledgedf = pd.read_csv(RPOKnowledgeURL).set_index("TAG").loc[RPO]
    Knowledgedict = Knowledgedf.to_dict()
    with open("ranges.json") as r:
        ranges = json.load(r)
    Keysname = list()
    Fieldsname = list()
    for item in list(Knowledgedict.keys()):
        for Range in list(ranges.keys()):
            if str(Knowledgedict[item]) == '-%':
                Keysname.append(item)
                Fieldsname.append("Little/none")
                break
            try:
                val = float(str(Knowledgedict[item])[:-1])/100
            except:
                break
            lowerBound = float(ranges[Range]['lowerBound'])
            upperBound = float(ranges[Range]['upperBound'])
            if (val >= lowerBound) and (val <= upperBound):
                Keysname.append(item)
                Fieldsname.append(ranges[Range]["name"])
                break
    dfOut = pd.DataFrame()
    dfOut['Field'] = Keysname
    dfOut['Knowledge Level'] = Fieldsname
    #imageTable = render_mpl_table(dfOut, header_columns=0, col_width=2.0)
    render_mpl_table(dfOut, header_columns=0, col_width=5.0)
    await ctx.respond(Embed(title=f"{RPO}'s Knowledge").set_image('table.png'),flags=64)
    os.remove('table.png')

@cp.child
@lightbulb.option("member", "member to query",type=hikari.Member,required=True)
@lightbulb.command("portfolio", "querys a member's RPO portfolio, if it exists", ephemeral=True, inherit_checks=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    rpo = userInfo.readUserInfo().loc[str(ctx.options.member.id),'RPO']
    hasInvested = rpoPortfolio(rpo.upper())
    if hasInvested:
        message = await ctx.author.send("See attached")
        await message.edit(attachment='multipage.pdf')
    else:
        await ctx.respond("No investments recorded for your RPO.", flags=64)

@QueryPlugin.command
@lightbulb.add_checks(lightbulb.Check(checks.Punished))
@lightbulb.command("ksptime", "display's the time in charlie's ksp save")
@lightbulb.implements(commands.SlashCommand)
async def command(ctx):
    data = sfsutils.parse_savefile('persistent.sfs')
    Ksptime = ksptime(data)
    await ctx.respond("Current Time: Year: {0}, Day: {1}, Hour: {2}, Minute: {3}, Second {4}".format((Ksptime[0]//462)+1,Ksptime[0]%462,Ksptime[1],Ksptime[2],Ksptime[3]))



def load(bot):bot.add_plugin(QueryPlugin)
def unload(bot):bot.remove_plugin(QueryPlugin)
