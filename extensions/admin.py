import json

import lightbulb
import pandas as pd
import sfsutils
from auxone import URL, ksptime, render_mpl_table, userInfo
from hikari.channels import PermissionOverwriteType
from hikari.permissions import Permissions
from lightbulb import commands
from lightbulb.checks import has_roles

AdminPlugin = lightbulb.Plugin("AdminPlugin")
AdminPlugin.add_checks(lightbulb.Check(has_roles(338173415527677954,253752685357039617,225413350874546176,mode=any)))



@AdminPlugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("update", "update group")
@lightbulb.implements(commands.SlashCommandGroup)
async def update(ctx) -> None: await ctx.respond("invoked update")

@update.child
@lightbulb.command("portfolio", "updates porfolios", inherit_checks=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    if ctx.author.id not in [225344348903047168, 363095569515806722]:
        return
    else:
        await ctx.respond("Starting")
        investChannel = await AdminPlugin.bot.rest.fetch_channel(900523609603313704)
        await investChannel.edit_overwrite(225345178955808768, PermissionOverwriteType.ROLE, deny=Permissions.SEND_MESSAGES)
        await investChannel.send("**MARKET UPDATING. INVESTMENTS LOCKED UNTIL COMPLETE**")
        RPOlist = list() #initializes empty list for list of RPOs with investments
        investments = json.load(open('investments.json'))
        Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change'])
        for rpo in list(investments.keys()):
            i=0
            length = len(investments[rpo]['Investments'])
            investments[rpo]['Total_Invested'] = 0
            investments[rpo]['Market_Value'] = 0
            investments[rpo]['Profit/Loss'] = 0
            sum=0
            while i<length:
                investments[rpo]['Investments'][i][2] = Marketdf.loc[investments[rpo]['Investments'][i][1],'Market Price']
                investments[rpo]['Investments'][i][3] = Marketdf.loc[investments[rpo]['Investments'][i][1],'Day change']
                investments[rpo]['Investments'][i][4] = round(float(str(investments[rpo]['Investments'][i][0]).replace(',','')) * float(str(investments[rpo]['Investments'][i][2]).replace(',','')),2)
                investments[rpo]['Investments'][i][7] = round(float(str(investments[rpo]['Investments'][i][4]).replace(',','')) - float(str(investments[rpo]['Investments'][i][5]).replace(',','')),2)
                investments[rpo]['Total_Invested'] += round(float(str(investments[rpo]['Investments'][i][5]).replace(',','')),2)
                investments[rpo]['Market_Value'] += round(float(str(investments[rpo]['Investments'][i][4]).replace(',','')),2)
                investments[rpo]['Profit/Loss'] += round(float(str(investments[rpo]['Investments'][i][7]).replace(',','')),2)
                sum += round(float(investments[rpo]['Investments'][i][4]),2)
                i+=1
            investments[rpo]["Market_History"].append(sum)
        json.dump(investments,open('investments.json','w'))
        await investChannel.send("**MARKET UPDATED. INVESTMENTS UNLOCKED.**")
        await investChannel.edit_overwrite(225345178955808768, PermissionOverwriteType.ROLE, allow=Permissions.SEND_MESSAGES)
        await ctx.respond("Portfolio's updated!")

@update.child
@lightbulb.command("time", "updates KSP time, and runs reccuring income", inherit_checks=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    data = sfsutils.parse_savefile('persistent.sfs')
    Ksptime = ksptime(data)
    reccuring = json.load(open("recurring.json"))
    df = pd.DataFrame()
    df["RPO"] = []
    df["name"] = []
    df["amount"] = []
    df["nextPayment"] = []
    for rpo in list(reccuring.keys()):
        length = len(reccuring[rpo])
        i=0
        while i<length:
            if reccuring[rpo][i]["nextPayment"]<Ksptime[0]:
                userInfo.editWallet(rpo.upper(),float(reccuring[rpo][i]["amount"]))
                reccuring[rpo][i]["nextPayment"] += reccuring[rpo][i]["interval"]
                df.loc[-1] = [rpo.upper(),reccuring[rpo][i]["name"],reccuring[rpo][i]["amount"],reccuring[rpo][i]["nextPayment"]]
            i+=1    
    try:
        render_mpl_table(df,header_columns=0,col_width=10)
        await ctx.respond("See Below:")
        await ctx.edit_last_response(attachment='table.png')
    except:await ctx.send("No recurring events have happened")
    await ctx.send("Current Time: Year: {0}, Day: {1}, Hour: {2}, Minute: {3}, Second {4}".format(Ksptime[0]//462,Ksptime[0]%462,Ksptime[1],Ksptime[2],Ksptime[3]))
    with open("recurring.json","w") as r:
        json.dump(reccuring,r)

@AdminPlugin.command
@lightbulb.command("reccuring", "reccuring group")
@lightbulb.implements(commands.SlashCommandGroup)
async def reccuring(ctx) -> None: await ctx.respond("invoked reccuring")

@reccuring.child
@lightbulb.option("rpo", "RPO to query",required=True)
@lightbulb.option("name","Name for the recourring event.",required=True)
@lightbulb.option('next',"First day for event to trigger",type=int,required=True)
@lightbulb.option("interval","How long between triggers of event",type=int,required=True)
@lightbulb.option("amount","Amount to add/remove on event (can be 0 for a tracker event)",type=int,required=True)
@lightbulb.command("new","adds new reccuring event")
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    rpo = ctx.options.rpo;name = ctx.options.name;next = ctx.options.next;interval = ctx.options.interval;amount = ctx.options.amount
    reccuring = json.load(open("recurring.json"))
    if rpo.upper() in list(reccuring.keys()):
        reccuring[rpo.upper()].append({"name":str(name),"nextPayment":int(next),"interval":int(interval),"amount":int(amount)})
    else:
        reccuring.update({rpo.upper():[{"name":str(name),"nextPayment":int(next),"interval":int(interval),"amount":int(amount)}]})
    with open("recurring.json","w") as r:
        json.dump(reccuring,r)
    await ctx.respond("Added new reccuring event to RPO "+str(rpo.upper())+": "+str(name)+" every "+str(interval)+" days, starting on day "+str(next)+" for a change in balance of "+str(amount)+".")

@reccuring.child
@lightbulb.option("rpo", "RPO to query",required=True)
@lightbulb.option("name", "OPTIONAL. recurring event to look at, if none given, will show all for the RPO.",required=False, default=None)
@lightbulb.command("query","queries one/all reccuring event(s) for an RPO")
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    rpo = ctx.options.rpo;name=ctx.options.name
    reccuring = json.load(open("recurring.json"))
    if name is None:
        if len(reccuring[rpo.upper()]) == 0:
            await ctx.respond("No reccuring events have been recorded for this RPO")
        else:
            try:await ctx.respond("This RPO has the following recorded events: "+str([x['name'] for x in reccuring[rpo.upper()]]))
            except:await ctx.respond("No reccuring events have been recorded for this RPO")
    else:
        for event in reccuring[rpo.upper()]:
            if event['name'] is name:
                await ctx.respond(str(event))
                return
        await ctx.respond(f"No reccuring event with name {name} have been recorded for this RPO")

@reccuring.child
@lightbulb.option("rpo", "RPO to query",required=True)
@lightbulb.option("name", "OPTIONAL. recurring event to look at, if none given, will show all for the RPO.",required=True)
@lightbulb.command("remove","removes one reccuring event for an RPO")
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    reccuring = json.load(open("recurring.json"))
    rpo = ctx.options.rpo;name=ctx.options.name;i = 0;length = len(reccuring[rpo.upper()])
    while i<length:
        if name==reccuring[rpo.upper()][i]['name']:
            reccuring[rpo.upper()].pop(i)
            break
        i+=1
    with open("recurring.json","w") as r:
        json.dump(reccuring,r)
    await ctx.respond("Specified Event has been removed.")




def load(bot):bot.add_plugin(AdminPlugin)
def unload(bot):bot.remove_plugin(AdminPlugin)
