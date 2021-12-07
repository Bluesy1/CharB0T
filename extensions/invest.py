import json
import os
import re

import lightbulb
import matplotlib.pyplot as plt
import pandas as pd
import sfsutils as sfs
from auxone import (URL, as_currency, checks, part_check, render_mpl_table_colors,
                    render_mpl_table_colors_pdf, userInfo)
from hikari import Embed
from lightbulb import commands
from matplotlib.backends.backend_pdf import PdfPages

InvestPlugin = lightbulb.Plugin("InvestPlugin")
@InvestPlugin.add_checks(lightbulb.Check(checks.Punished),lightbulb.has_roles(906000578092621865)|lightbulb.owner_only,lightbulb.Check(checks.check_invest_channel))

@InvestPlugin.command
@lightbulb.command("invest", "invest group")
@lightbulb.implements(commands.SlashCommandGroup)
async def invest(ctx) -> None: await ctx.respond("invoked invest")

@invest.child
@lightbulb.option("symbol", "symbol to sell", required=True)
@lightbulb.option("amount", "amount to sell", type=int, required=True)
@lightbulb.command("sell", "sells shares in a specified stock")
@lightbulb.implements(commands.SlashCommandGroup)
async def command(ctx):
    author = ctx.member
    userid = str(author.id)
    if ctx.member.id == 225344348903047168 or userInfo.readUserInfo().loc[str(ctx.member.id),"RPO"] == 'CP':
        await ctx.respond('<:KSplodes:896043440872235028> Error: Charlie and The Celestial Project are not allowed to invest.')
        return
    args = [ctx.options.symbol,ctx.options.amount]
    if str(ctx.member.id) not in list(userInfo.readUserInfo().index):
        await ctx.respond("<:KSplodes:896043440872235028> Error: Not registered in an RPO for the bot. Please register with the bot through !joinRPO <RPO_Tag>")
        return
    elif userInfo.readUserInfo().loc[str(ctx.member.id),"RPO"] == 'A':
        await ctx.respond("<:KSplodes:896043440872235028> Error: Invalid in an RPO for investing. Please change your RPO !changeRPO <New_RPO_Tag>")
        return
    elif str(userid) in list(userInfo.readUserInfo().index):
        userList = userInfo.readUserInfo()
        print(args)
        Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
        Marketdf = Marketdf.reset_index() #fixes the data frame so it can be concatenated with the specific investments data frame
        try:
            args[1] = args[1].upper()
            args[2]
            try:
                int(args[2])
            except:
                await ctx.respond("<:KSplodes:896043440872235028> Error: `"+ str(args[2]) +"` is invalid argument for number of shares.")
                return
        except:
            await ctx.respond("<:KSplodes:896043440872235028> Error: !sellShares requires 2 arguments separated by spaces: `Symbol` and `Amount to Sell`")
            return
        finally:
            rpo = userList.loc[str(ctx.member.id), 'RPO']
            investments = json.load(open('investments.json'))
            i=0
            length = len(investments[rpo]['Investments'])
            while i<length:
                if investments[rpo]['Investments'][i][1]==args[1]:
                    break
                i+=1
            if int(args[2]) > investments[rpo]['Investments'][i][0]:
                await ctx.respond("<:KSplodes:896043440872235028> Error: you cannot sell more shares than you own.")
                return
            elif args[1] in pd.read_csv(URL, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0)['Symbol'].to_list():
                if int(args[2]) > 0:
                    Marketdf.set_index('Symbol',inplace=True)
                    costForOne = Marketdf.loc[str(args[1]), 'Market Price']
                    costForAmount = round(costForOne * int(args[2]),2)
                    taxCost = round(costForAmount * .01,2)
                    payout = round(costForAmount - taxCost,2)
                    investments[rpo]['Investments'][i][0] -= int(args[2])
                    totalInvested = investments[rpo]['Investments'][i][0]
                    Marketdf = Marketdf.reset_index() #fixes the data frame so it can be concatenated with the specific investments data frame
                    investments[rpo]['Investments'][i][4] = round(float(str(investments[rpo]['Investments'][i][0]).replace(',','')) * float(str(investments[rpo]['Investments'][i][2]).replace(',','')),2)  #does the math to make the market value column
                    investments[rpo]['Investments'][i][5] = round(float(str(investments[rpo]['Investments'][i][5]).replace(',','')) - payout,2)
                    investments[rpo]['Investments'][i][6] = round(float(str(investments[rpo]['Investments'][i][5]).replace(',','')) / float(str(investments[rpo]['Investments'][i][0]).replace(',','')),2)
                    investments[rpo]['Investments'][i][4] = round(float(str(investments[rpo]['Investments'][i][0]).replace(',','')) * float(str(investments[rpo]['Investments'][i][2]).replace(',','')),2)
                    investments[rpo]['Investments'][i][7] = round(float(str(investments[rpo]['Investments'][i][4]).replace(',','')) - float(str(investments[rpo]['Investments'][i][5]).replace(',','')),2)
                    sum = 0 #Gets the sum of the stock prices
                    investments[rpo]['Market_History'].append(sum)
                    investments[rpo]['Total_Invested'] = 0
                    j=0
                    while j<length:
                        investments[rpo]['Total_Invested'] += float(investments[rpo]['Investments'][i][5])
                        sum += float(investments[rpo]['Investments'][i][4])
                        j+=1
                    json.dump(investments,open('investments.json','w'))
                    accountBalanceSheet = userInfo.getWallet()
                    accountBalanceSheet.loc[rpo, 'Account Balance'] += payout
                    coinsRemaining = accountBalanceSheet.loc[rpo, 'Account Balance']
                    userList.loc[str(225344348903047168), 'Coin Amount'] += taxCost
                    #embeddict = {'color': 6345206, 'type': 'rich', 'description': ctx.member.display_name + ', you have sold **'+ str(args[2]) + '** share(s) in **'+ str(args[1]) +'** for a total  of **'+as_currency(costForAmount)  +'** Funds, **'+ as_currency(taxCost) + '** have been diverted as a transaction fee. Your RPO recieved a payout of **'+str(payout) +'** Funds. Your RPO now has **' + as_currency(round(coinsRemaining,2)) +'**, and **' + str(totalInvested) +"** shares(s) left in **" +str(args[1])+"**."}
                    userInfo.writeUserInfo(userList)
                    userInfo.writeWallet(accountBalanceSheet)
                    await ctx.respond(embed=Embed(description=f"{ctx.member.display_name} , you have sold **{str(args[2])}** share(s) in **{str(args[1])}** for a total  of **{as_currency(costForAmount)}** Funds, **{as_currency(taxCost)}** have been diverted as a transaction fee. Your RPO recieved a payout of **{str(payout)}** Funds. Your RPO now has **{as_currency(round(coinsRemaining,2))}**, and **{str(totalInvested)}** shares(s) left in **{str(args[1])}**.", color="60D1F6"))
                elif int(args[2]) <= 0:
                    await ctx.respond("<:KSplodes:896043440872235028> Error: Invalid argument in position 2: " + str(args[2]) + ". Argument must be a positive integer.")
            else:
                await ctx.respond("<:KSplodes:896043440872235028> Error: Invalid argument in position 1: " + str(args[1]) + ". Argument one must be one of the public stocks.")

@invest.child
@lightbulb.command("invest", "buy subgroup")
@lightbulb.implements(commands.SlashSubGroup)
async def buy(ctx) -> None: await ctx.respond("invoked invest-buy")

@buy.child
@lightbulb.option("symbol", "symbol to buy", required=True)
@lightbulb.option("amount", "amount to buy", type=int, required=True)
@lightbulb.command("coins", "buys a secified amount of a specified stock using coins")
@lightbulb.implements(commands.SlashCommandGroup)
async def command(ctx):
    author = ctx.member
    userid = str(author.id)
    if ctx.member.id == 225344348903047168 or userInfo.readUserInfo().loc[str(ctx.member.id),"RPO"] == 'CP':
        await ctx.respond('<:KSplodes:896043440872235028> Error: Charlie and The Celestial Project are not allowed to invest.')
        return
    args = [ctx.options.symbol,ctx.options.amount]
    if str(ctx.member.id) not in list(userInfo.readUserInfo().index):
        await ctx.respond("<:KSplodes:896043440872235028> Error: Not registered in an RPO for the bot. Please register with the bot through !joinRPO <RPO_Tag>")
        return
    elif userInfo.readUserInfo().loc[str(ctx.member.id),"RPO"] == 'A':
        await ctx.respond("<:KSplodes:896043440872235028> Error: Invalid in an RPO for investing. Please change your RPO !changeRPO <New_RPO_Tag>")
        return
    userList = userInfo.readUserInfo()
    rpo = userList.loc[str(ctx.member.id), 'RPO']
    investments = json.load(open('investments.json'))
    if rpo not in list(investments.keys()):
        investments.update({rpo:{"Market_Value": 0, "Total_Invested": 0, "Profit/Loss": 0, "Investments": [], "Market_History": []}})
    print(args)
    Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
    Marketdf = Marketdf.reset_index() #fixes the data frame so it can be concatenated with the specific investments data frame
    args = [ctx.options.symbol, abs(ctx.options.amount)]
    wealth = int(userList.loc[str(ctx.member.id), 'Coin Amount'])
    if args[2] in pd.read_csv(URL, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0)['Symbol'].to_list():
        i=0
        length = len(investments[rpo]['Investments'])
        newInvest = True
        while i<length:
            if investments[rpo]['Investments'][i][1]==args[2]:
                newInvest = False
                break
            i+=1
        if newInvest:
            Marketdf = pd.read_csv(URL, usecols=['Symbol', 'Market Price', 'Day change'],index_col=0)
            investments[rpo]['Investments'].append([0,args[2],Marketdf.loc[args[2],'Market Price'],Marketdf.loc[args[2],'Day change'],0,0,0,0])
        if int(args[3]) > 0:
            Marketdf.set_index('Symbol',inplace=True)
            costForOne = Marketdf.loc[args[2], 'Market Price']
            costForAmount = round(costForOne * int(args[3]),2)
            taxCost = round(costForAmount * .01,2)
            totalCost = round(costForAmount + taxCost,2)
            if wealth >= totalCost:
                investments[rpo]['Investments'][i][0] += int(args[3])
                investments[rpo]['Investments'][i][5] = round(float(str(investments[rpo]['Investments'][i][5]).replace(',','')) + totalCost,2)
                investments[rpo]['Investments'][i][4] = round(investments[rpo]['Investments'][i][0] * float(str(investments[rpo]['Investments'][i][2]).replace(',','')),2)
                investments[rpo]['Investments'][i][6] = round(float(str(investments[rpo]['Investments'][i][5]).replace(',','')) / float(str(investments[rpo]['Investments'][i][0]).replace(',','')),2)
                investments[rpo]['Investments'][i][7] = round(float(str(investments[rpo]['Investments'][i][4]).replace(',','')) - float(str(investments[rpo]['Investments'][i][5]).replace(',','')),2)
                investments[rpo]['Total_Invested'] = 0
                sum=0
                j=0
                while j<length:
                    investments[rpo]['Total_Invested'] += float(investments[rpo]['Investments'][i][5])
                    sum += float(investments[rpo]['Investments'][i][4])
                    j+=1
                investments[rpo]["Market_History"].append(sum)
                json.dump(investments,open('investments.json','w'))
                coinsRemaining = userInfo.editCoins(userid,0-totalCost)['final']
                userInfo.editCoins(str(225344348903047168), taxCost)
                #embeddict = {'color': 6345206, 'type': 'rich', 'description': ctx.member.display_name + ', you have bought **'+ str(args[3]) + '** share(s) in **'+ str(args[2]) +'** for a total cost of **'+as_currency(totalCost)  +'** <:HotTips2:465535606739697664>, **'+ as_currency(costForAmount) + '** <:HotTips2:465535606739697664> for these shares and **'+as_currency(taxCost) +'** <:HotTips2:465535606739697664> as a transaction fees. You now have **' + as_currency(round(coinsRemaining,2)) +'** <:HotTips2:465535606739697664> left.'}
                await ctx.respond(embed=Embed(description=f"{ctx.member.display_name}, you have bought **{str(args[3])}** share(s) in **{str(args[2])}** for a total cost of **{as_currency(totalCost)}** <:HotTips2:465535606739697664>, **{as_currency(costForAmount)}** <:HotTips2:465535606739697664> for these shares and **{as_currency(taxCost)}** <:HotTips2:465535606739697664> as a transaction fees. You now have **{as_currency(round(coinsRemaining,2))}** <:HotTips2:465535606739697664> left.", color="60D1F6"))
            else:
                await ctx.respond("<:KSplodes:896043440872235028> Error: Cost for requested transaction: " + str(totalCost) +" is greater than the amount of currency you have on your discord account: " +str(wealth)+'.') 
        elif int(args[3]) <= 0:
            await ctx.respond("<:KSplodes:896043440872235028> Error: Invalid argument in position 3: " + str(args[3]) + ". Argument must be a positive integer.")
    else:
        await ctx.respond("<:KSplodes:896043440872235028> Error: Invalid argument in position 2: " + str(args[2]) + ". Argument one must be one of the public stocks.")

@buy.child
@lightbulb.option("symbol", "symbol to buy", required=True)
@lightbulb.option("amount", "amount to buy", type=int, required=True)
@lightbulb.command("funds", "buys a secified amount of a specified stock using funds")
@lightbulb.implements(commands.SlashCommandGroup)
async def command(ctx):
    author = ctx.member
    userid = str(author.id)
    if ctx.member.id == 225344348903047168 or userInfo.readUserInfo().loc[str(ctx.member.id),"RPO"] == 'CP':
        await ctx.respond('<:KSplodes:896043440872235028> Error: Charlie and The Celestial Project are not allowed to invest.')
        return
    args = [ctx.options.symbol,ctx.options.amount]
    if str(ctx.member.id) not in list(userInfo.readUserInfo().index):
        await ctx.respond("<:KSplodes:896043440872235028> Error: Not registered in an RPO for the bot. Please register with the bot through !joinRPO <RPO_Tag>")
        return
    elif userInfo.readUserInfo().loc[str(ctx.member.id),"RPO"] == 'A':
        await ctx.respond("<:KSplodes:896043440872235028> Error: Invalid in an RPO for investing. Please change your RPO !changeRPO <New_RPO_Tag>")
        return
    userList = userInfo.readUserInfo()
    rpo = userList.loc[str(ctx.member.id), 'RPO']
    investments = json.load(open('investments.json'))
    if rpo not in list(investments.keys()):
        investments.update({rpo:{"Market_Value": 0, "Total_Invested": 0, "Profit/Loss": 0, "Investments": [], "Market_History": []}})
    print(args)
    Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
    Marketdf = Marketdf.reset_index() #fixes the data frame so it can be concatenated with the specific investments data frame
    args = [ctx.options.symbol, abs(ctx.options.amount)]
    accountBalanceSheet = userInfo.getWallet()
    wealth = float(str(accountBalanceSheet.loc[rpo, 'Account Balance']).replace(',',''))
    if args[2] in pd.read_csv(URL, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0)['Symbol'].to_list():
        i=0
        length = len(investments[rpo]['Investments'])
        newInvest = True
        while i<length:
            if investments[rpo]['Investments'][i][1]==args[2]:
                newInvest = False
                break
            i+=1
        if newInvest:
            Marketdf = pd.read_csv(URL, usecols=['Symbol', 'Market Price', 'Day change'],index_col=0)
            investments[rpo]['Investments'].append([0,args[2],Marketdf.loc[args[2],'Market Price'],Marketdf.loc[args[2],'Day change'],0,0,0,0])
        if int(args[3]) > 0:
            Marketdf.set_index('Symbol',inplace=True)
            costForOne = Marketdf.loc[str(args[2]), 'Market Price']
            costForAmount = round(costForOne * int(args[3]),2)
            taxCost = round(costForAmount * .01,2)
            totalCost = round(costForAmount + taxCost,2)
            if wealth >= totalCost:
                investments[rpo]['Investments'][i][0] += int(args[3])
                investments[rpo]['Investments'][i][5] = round(float(str(investments[rpo]['Investments'][i][5]).replace(',','')) + totalCost,2)
                investments[rpo]['Investments'][i][4] = round(investments[rpo]['Investments'][i][0] * float(str(investments[rpo]['Investments'][i][2]).replace(',','')),2)
                investments[rpo]['Investments'][i][6] = round(float(str(investments[rpo]['Investments'][i][5]).replace(',','')) / float(str(investments[rpo]['Investments'][i][0]).replace(',','')),2)
                investments[rpo]['Investments'][i][7] = round(float(str(investments[rpo]['Investments'][i][4]).replace(',','')) - float(str(investments[rpo]['Investments'][i][5]).replace(',','')),2)
                investments[rpo]['Total_Invested'] = 0
                sum=0
                j=0
                while j<length:
                    investments[rpo]['Total_Invested'] += float(investments[rpo]['Investments'][i][5])
                    sum += float(investments[rpo]['Investments'][i][4])
                    j+=1
                investments[rpo]["Market_History"].append(sum)
                json.dump(investments,open('investments.json','w'))
                json.dump(investments,open('investments.json','w'))
                coinsRemaining = userInfo.editWallet(rpo,0-totalCost)['final']
                userInfo.editCoins(str(225344348903047168), taxCost)
                #embeddict = {'color': 6345206, 'type': 'rich', 'description': ctx.member.display_name + ', you have bought **'+ str(args[3]) + '** share(s) in **'+ str(args[2]) +'** for a total cost of **'+as_currency(totalCost)  +'** Funds, **'+ as_currency(costForAmount) + '** Funds for those shares and **'+as_currency(taxCost) +'** Funds as transaction fees. Your RPO now has **' + str(round(coinsRemaining,2)) +'** Funds left.'}
                await ctx.respond(embed=Embed(f"{ctx.member.display_name} + ', you have bought **{str(args[3])}** share(s) in **{str(args[2])}** for a total cost of **{as_currency(totalCost)}** Funds, **{as_currency(costForAmount)}** Funds for those shares and **{as_currency(taxCost)}** Funds as transaction fees. Your RPO now has **{str(round(coinsRemaining,2))} +'** Funds left.",color="60D1F6"))
            else:
                await ctx.respond("<:KSplodes:896043440872235028> Error: Cost for requested transaction: " + str(totalCost) +" is greater than the amount of currency your RPO has in it's account: " +str(wealth)+'.') 
        elif int(args[3]) <= 0:
            await ctx.respond("<:KSplodes:896043440872235028> Error: Invalid argument in position 3: " + str(args[3]) + ". Argument must be a positive integer.")
    else:
        await ctx.respond("<:KSplodes:896043440872235028> Error: Invalid argument in position 2: " + str(args[2]) + ". Argument one must be one of the public stocks.")


def load(bot):bot.add_plugin(InvestPlugin)
def unload(bot):bot.remove_plugin(InvestPlugin)
