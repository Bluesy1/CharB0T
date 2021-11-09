from __future__ import print_function
import enum
import os.path
from random import randrange
from discord import client
from discord.ext.commands.core import command
from googleapiclient.discovery import build
import gspread
from gspread.models import Spreadsheet
from gspread_dataframe import set_with_dataframe
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from httplib2 import Response
import pandas as pd
import numpy as np
import json
import discord
from discord.ext import commands
import logging
from pandas.io.pytables import dropna_doc
import pygsheets
import time
import datetime
import random
import re
#imports all needed packages
pyg = pygsheets.authorize(client_secret='credentials.json') #Inits the pygsheets api
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
#Creates a log for the discord bot, good for debugging
# If modifying these scopes, delete the file token.json. (The end user (In this case You charlie, shouldn't have to do that because i'm not changing the scope unless i have to later))
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
# The ID and range of a sample spreadsheet.
with open('details.json') as f:
    data = json.load(f) 

URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['googleSheetId'],
    data['workSheetName']
)
InvestorsURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['InvestersID'],
    data['Investorssheetgid']
)
SSaccessURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['SSaccessID'],
    data['SSaccessgid']
)
UserListURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['UserListID'],
    data['UserListgid']
)
RPOInfoURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['RPOinfoID'],
    data['RPOinfogid']
)  #these make the URLS needed for pandas to read the needed CSVs, in combination with the details.json file

# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
def refresh():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('sheets', 'v4', credentials=creds)
service = refresh()
Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
Investmentsdf = pd.read_csv(InvestorsURL, index_col=0).dropna(axis=1, how='all') #Creates the data fram for investors
RPOlist = list() #initializes empty list for list of RPOs with investments
spreadoutsdf = pd.read_csv(SSaccessURL, index_col=0)

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.channel.id != 893867549589131314:
            return
        else:
            if message.author.id != 82495450153750528 and message.author.id != 755539532924977262:
                return
            else:
                service = refresh()
                if message.content.startswith('buyShares') or message.content.startswith('Buyshares') or message.content.startswith('BuyShares'): #args: <Coins/Funds>, <Symbol>, <Amount> 
                    if message.channel.id != 687817008355737606 and message.channel.id != 900523609603313704:
                        return
                    author = message.author
                    userid = author.id
                    if message.author.id == 225344348903047168:
                        await message.channel.send('<:KSplodes:896043440872235028> Error: Charlie and The Celestial Project are not allowed to invest.')
                        return
                    args = message.content.split()
                    if str(userid) not in pd.read_csv(UserListURL)['userID'].astype(str).to_list():
                        await message.channel.send("<:KSplodes:896043440872235028> Error: Not registered in an RPO for the bot. Please register with the bot through !joinRPO <RPO_Tag>")
                        return
                    elif pd.read_csv(UserListURL, index_col=0).loc[userid,'RPO'] == 'A':
                        await message.channel.send("<:KSplodes:896043440872235028> Error: Not explicitly declared in RPO for investing. Please change your RPO !changeRPO <New_RPO_Tag>")
                        return
                    elif str(userid) in pd.read_csv(UserListURL)['userID'].astype(str).to_list():
                        Investmentsdf = pd.read_csv(InvestorsURL, index_col=0).dropna(axis=1, how='all')
                        await message.channel.send("Investing for: " + pd.read_csv(UserListURL, index_col=0).loc[userid,'RPO'])
                        if not pd.read_csv(SSaccessURL, index_col=0).loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'hasInvested']:
                            sheet = pyg.open_by_key(pd.read_csv(SSaccessURL, index_col=0).loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'sheetID'])
                            sheet.share("", role='reader', type='anyone')
                            SSaccess = pd.read_csv(SSaccessURL)
                            SSaccess['new'] = SSaccess['rpo']
                            SSaccess = SSaccess.set_index('new')
                            SSaccess.loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'hasInvested'] = True
                            gc = gspread.service_account(filename='service_account.json') #gets credentials
                            sh = gc.open_by_key(data['SSaccessID']) #gets sheetinfo
                            worksheet = sh.get_worksheet(7) #-> 0 - first sheet, 1 - second sheet etc. 
                            # APPEND DATA TO SHEET
                            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                            set_with_dataframe(worksheet, SSaccess) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                        await message.author.send('Link to Investment sheet: https://docs.google.com/spreadsheets/d/{0}'.format(pd.read_csv(SSaccessURL, index_col=0).loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'sheetID']))
                        userList = pd.read_csv(UserListURL)
                        userList["new"] = userList['userID']
                        userList = userList.set_index("new")
                        args = message.content.split()
                        print(args)
                        Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
                        Investmentsdf = pd.read_csv(InvestorsURL) #Creates the data frame for investors
                        Investmentsdf['new'] = Investmentsdf['RPO']
                        Investmentsdf = Investmentsdf.set_index('new')
                        spreadoutsdf = pd.read_csv(SSaccessURL, index_col=0) #creates the data frame that we reference to get the info needed to push stuff to spreadsheets
                        df = pd.DataFrame(Investmentsdf.loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO']]) #creates the data frame with the specific investments with just one rpo
                        df = df.reset_index() #fixes the data frame so it can be concatenated with with the market value data frame
                        Marketdf = Marketdf.reset_index() #fixes the data frame so it can be concatenated with the specific investments data frame
                        try:
                            args[1] = args[1].capitalize()
                            args[2] = args[2].upper()
                            args[3]
                            try:
                                int(args[3])
                            except:
                                await message.channel.send("<:KSplodes:896043440872235028> Error: `"+ str(args[3]) +"` is invalid argument for number of shares.")
                                return
                        except:
                            await message.channel.send("<:KSplodes:896043440872235028> Error: buyShares requires 3 arguments separated by spaces: `Coins/Funds`, `Symbol`, and `Amount to Buy`")
                            return
                        finally:
                            if args[1] == 'Coins':
                                wealth = int(userList.loc[message.author.id, 'Coin Amount'])
                                if args[2] in pd.read_csv(URL, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0)['Symbol'].to_list():
                                    if int(args[3]) > 0:
                                        Marketdf = pd.read_csv(URL, usecols=['Symbol', 'Market Price', 'Day change'])
                                        #print(Marketdf.head(35))
                                        Marketdf['new'] = Marketdf['Symbol']
                                        Marketdf = Marketdf.set_index('new')
                                        costForOne = Marketdf.loc[args[2], 'Market Price']
                                        costForAmount = round(costForOne * int(args[3]),2)
                                        taxCost = round(costForAmount * .02,2)
                                        totalCost = round(costForAmount + taxCost,2)
                                        if wealth >= totalCost:
                                            rpo = pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO']
                                            Investmentsdf = pd.read_csv(InvestorsURL).dropna(axis=1, how='all')
                                            Investmentsdf['new'] = Investmentsdf['RPO']
                                            Investmentsdf = Investmentsdf.set_index('new')
                                            Investmentsdf.loc[rpo, str(args[2])] += int(args[3])
                                            totalInvested = Investmentsdf.loc[rpo, str(args[2])]
                                            gc = gspread.service_account(filename='service_account.json') #gets credentials
                                            sh = gc.open_by_key(data['InvestersID']) #gets sheetinfo
                                            worksheet = sh.get_worksheet(6) #-> 0 - first sheet, 1 - second sheet etc. 
                                            # APPEND DATA TO SHEET
                                            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                                            set_with_dataframe(worksheet, Investmentsdf) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                                            df = df.drop(0, axis=0).reset_index() #fixes the data frame so it can be concatenated with with the market value data frame
                                            Marketdf = Marketdf.reset_index() #fixes the data frame so it can be concatenated with the specific investments data frame
                                            print(df.head())
                                            print(Marketdf.head())
                                            df = pd.concat([df, Marketdf], axis = 1).dropna(axis=0).rename(columns={rpo:'Shares'}) #concatenates the two dataframes, removes private companies, and fixes a column title
                                            df['Market Value'] = df['Shares'].astype(float) * df['Market Price'].astype(float)  #does the math to make the market value column
                                            df['new'] = df['Symbol']
                                            df = df.set_index('new')
                                            df['Total Invested (includes fees) '] = 0
                                            df['Cost Basis '] = 0
                                            print('https://docs.google.com/spreadsheets/d/{0}'.format(spreadoutsdf.loc[rpo, 'sheetID']))
                                            #portfolio = pd.read_csv('https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(spreadoutsdf.loc[rpo, 'sheetID'],spreadoutsdf.loc[rpo, 'gid1']), dtype={'Market Value':str, 'Total Invested (includes fees) ': str}, skiprows=0).dropna(axis=1,how='all').dropna(axis=0,thresh=6)
                                            sheet = service.spreadsheets()
                                            result = sheet.values().get(spreadsheetId=spreadoutsdf.loc[rpo, 'sheetID'],
                                                                    range='A11:H44', majorDimension='COLUMNS').execute()
                                            values = result.get('values', [])
                                            #print(type(values), values)
                                            portfoliodict = {'Shares': values[0],'Symbol ': values[1],'Price': values[2],'Day Change': values[3],'Market Value': values[4],'Total Invested (includes fees) ': values[5],'Cost Basis ': values[6],'Profit / Loss ': values[7]}
                                            portfolio = pd.DataFrame(data=portfoliodict).dropna(axis=1,how='all').dropna(axis=0,thresh=6)
                                            df['Market Value'] = df['Market Value'].apply(lambda x: x.replace('$', '').replace(',', '')
                                                                    if isinstance(x, str) else x).astype(float)
                                            #print(portfolio.columns)
                                            #print(df.head(35))
                                            for i in portfolio['Total Invested (includes fees) '].to_list():
                                                portfolio2 = portfolio
                                                portfolio2['new'] = portfolio2['Total Invested (includes fees) ']
                                                portfolio2 = portfolio2.set_index('new')
                                                df.loc[portfolio2.loc[i,'Symbol '], 'Total Invested (includes fees) '] = i
                                            #print(df.loc[portfolio2.loc[i,'Symbol '], 'Total Invested (includes fees) '])
                                            for i in portfolio['Cost Basis '].to_list():
                                                portfolio2 = portfolio
                                                portfolio2['new'] = portfolio2['Cost Basis ']
                                                portfolio2 = portfolio2.set_index('new')
                                            #print(portfolio2.head(30))
                                            #return
                                                df.loc[portfolio2.loc[i,'Symbol '], 'Cost Basis '] = i
                                                #print(i)
                                            #print(df.loc[portfolio2.loc[i,'Symbol '], 'Cost Basis '])
                                            df['Total Invested (includes fees) '] = df['Total Invested (includes fees) '].apply(lambda x: x.replace('$', '').replace(',', '')
                                                            if isinstance(x, str) else x).astype(float)
                                            df.loc[str(args[2]),'Shares'] = totalInvested
                                            df.loc[str(args[2]),'Total Invested (includes fees) '] += totalCost
                                            df["Market Value"] = df['Shares'] * df['Market Price']
                                            df.loc[str(args[2]),'Cost Basis '] = df.loc[str(args[2]),'Total Invested (includes fees) '] / df.loc[str(args[2]),'Shares']
                                            df['Profit / Loss '] = df['Market Value'].astype(float) - df['Total Invested (includes fees) '].astype(float)
                                            request = service.spreadsheets().values().get(spreadsheetId=spreadoutsdf.loc[rpo, 'sheetID'], range='Visuals!C31:C39', majorDimension = 'COLUMNS', valueRenderOption = 'UNFORMATTED_VALUE')
                                            response = request.execute()
                                            history = response['values']
                                            history = [ item for elem in history for item in elem]
                                            sum = df['Market Value'].sum() #Gets the sum of the stock prices
                                            history.append(sum)
                                            history.insert(0, sum)
                                            history = np.array(history)
                                            history = history.astype(float)
                                            minimum = min(history)*0.8
                                            maximum = max(history)*1.2
                                            minmax = [minimum, maximum] #these lines do stuff to get the min and max values for the line graph
                                            history = [str(round(x,2)) for x in history]
                                            history = list(history)
                                            totalInvested = df['Total Invested (includes fees) '].sum()*1.02
                                            print(rpo)
                                            df['Market Value'] = df['Market Value'].apply(lambda x: x.replace('$', '').replace(',', '')
                                            if isinstance(x, str) else x).astype(float)
                                            df = df.dropna(axis=0, thresh=6)
                                            batch_update_values_request_body = {
                                                "value_input_option" : 'USER_ENTERED',  # How the input data should be interpreted.
                                                "data": [
                                                    {"range": 'A11:H44',
                                                    "majorDimension":'COLUMNS',
                                                    "values": [
                                                        df['Shares'].astype(float).tolist(),
                                                        df['Symbol'].tolist(),
                                                        df['Market Price'].astype(float).tolist(),
                                                        df['Day change'].tolist(),
                                                        df['Market Value'].astype(float).tolist(),
                                                        df['Total Invested (includes fees) '].astype(float).tolist(),
                                                        df['Cost Basis '].tolist(),
                                                        df['Profit / Loss '].astype(float).tolist()]},#Converts dataframe into the form needed to send to google sheets
                                                    {"range": 'E4:H4',
                                                    "majorDimension":'ROWS',
                                                    "values":[[sum, totalInvested, "", sum - totalInvested]]
                                                    },
                                                    {"range": 'Visuals!C30:C40',
                                                    "majorDimension":'COLUMNS',
                                                    "values":[history]
                                                    },
                                                    {"range": 'Visuals!A14:A15',
                                                    "majorDimension":'COLUMNS',
                                                    "values":[minmax]
                                                    }
                                                    ]#Prepares full list of values that need to be sent to the spreadsheet 
                                            }
                                            request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadoutsdf.loc[rpo, 'sheetID'], body=batch_update_values_request_body)
                                            response = request.execute() #updates spreadsheet
                                            df2 = pd.read_csv(UserListURL)
                                            df2['userID'] = df2['userID'].astype(str)
                                            df2['new'] = df2['userID']
                                            df2 = df2.set_index('new')
                                            df2.loc[str(message.author.id), 'Coin Amount'] -= totalCost
                                            coinsRemaining = df2.loc[str(message.author.id), 'Coin Amount']
                                            df2.loc[str(225344348903047168), 'Coin Amount'] += taxCost
                                            remainingCoins = df2.loc[str(message.author.id), 'Coin Amount']
                                            embeddict = {'color': 6345206, 'type': 'rich', 'description': message.author.display_name + ', you have bought **'+ str(args[3]) + '** share(s) in **'+ str(args[2]) +'** for a total cost of **'+str(totalCost)  +'** <:HotTips2:465535606739697664>, **'+ str(costForAmount) + '** <:HotTips2:465535606739697664> for that shares and **'+str(taxCost) +'** <:HotTips2:465535606739697664> in transaction fees. You now have **' + str(round(coinsRemaining,2)) +'** <:HotTips2:465535606739697664> left.'}
                                            gc = gspread.service_account(filename='service_account.json') #gets credentials
                                            sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
                                            worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
                                            # APPEND DATA TO SHEET
                                            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                                            set_with_dataframe(worksheet, df2) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                                            await message.channel.send(embed=discord.Embed.from_dict(embeddict))
                                        else:
                                            await message.channel.send("<:KSplodes:896043440872235028> Error: Cost for requested transaction: " + str(totalCost) +" is greater than the amount of currency you have on your discord account: " +str(wealth)+'.') 
                                    elif int(args[3]) <= 0:
                                        await message.channel.send("<:KSplodes:896043440872235028> Error: Invalid argument in position 3: " + str(args[3]) + ". Argument must be a positive integer.")
                                else:
                                    await message.channel.send("<:KSplodes:896043440872235028> Error: Invalid argument in position 2: " + str(args[2]) + ". Argument one must be one of the public stocks.")
                            elif args[1] == 'Funds':
                                accountBalanceSheet = pd.read_csv(RPOInfoURL)
                                accountBalanceSheet['new'] = accountBalanceSheet['TAG']
                                accountBalanceSheet = accountBalanceSheet.set_index('new')
                                accountBalanceSheet['Account Balance'] = accountBalanceSheet['Account Balance'].apply(lambda x: x.replace('$', '').replace(',', '')
                                if isinstance(x, str) else x).astype(float)
                                wealth = float(accountBalanceSheet.loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'Account Balance'])
                                if args[2] in pd.read_csv(URL, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0)['Symbol'].to_list():
                                    if int(args[3]) > 0:
                                        Marketdf['new'] = Marketdf['Symbol']
                                        Marketdf = Marketdf.set_index('new')
                                        costForOne = Marketdf.loc[str(args[2]), 'Market Price']
                                        costForAmount = round(costForOne * int(args[3]),2)
                                        taxCost = round(costForAmount * .02,2)
                                        totalCost = round(costForAmount + taxCost,2)
                                        if wealth >= totalCost:
                                            rpo = pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO']
                                            Investmentsdf = pd.read_csv(InvestorsURL).dropna(axis=1, how='all')
                                            Investmentsdf['new'] = Investmentsdf['RPO']
                                            Investmentsdf = Investmentsdf.set_index('new')
                                            Investmentsdf.loc[rpo, str(args[2])] += int(args[3])
                                            totalInvested = Investmentsdf.loc[rpo, str(args[2])]
                                            gc = gspread.service_account(filename='service_account.json') #gets credentials
                                            sh = gc.open_by_key(data['InvestersID']) #gets sheetinfo
                                            worksheet = sh.get_worksheet(6) #-> 0 - first sheet, 1 - second sheet etc. 
                                            # APPEND DATA TO SHEET
                                            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                                            set_with_dataframe(worksheet, Investmentsdf) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                                            df = df.drop(0, axis=0).reset_index() #fixes the data frame so it can be concatenated with with the market value data frame
                                            Marketdf = Marketdf.reset_index() #fixes the data frame so it can be concatenated with the specific investments data frame
                                            print(df.head())
                                            print(Marketdf.head())
                                            df = pd.concat([df, Marketdf], axis = 1).dropna(axis=0).rename(columns={rpo:'Shares'}) #concatenates the two dataframes, removes private companies, and fixes a column title
                                            df['Market Value'] = df['Shares'].astype(float) * df['Market Price'].astype(float)  #does the math to make the market value column
                                            df['new'] = df['Symbol']
                                            df = df.set_index('new')
                                            df['Total Invested (includes fees) '] = 0
                                            df['Cost Basis '] = 0
                                            print('https://docs.google.com/spreadsheets/d/{0}'.format(spreadoutsdf.loc[rpo, 'sheetID']))
                                            #portfolio = pd.read_csv('https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(spreadoutsdf.loc[rpo, 'sheetID'],spreadoutsdf.loc[rpo, 'gid1']), dtype={'Market Value':str, 'Total Invested (includes fees) ': str}, skiprows=0).dropna(axis=1,how='all').dropna(axis=0,thresh=6)
                                            sheet = service.spreadsheets()
                                            result = sheet.values().get(spreadsheetId=spreadoutsdf.loc[rpo, 'sheetID'],
                                                                    range='A11:H44', majorDimension='COLUMNS').execute()
                                            values = result.get('values', [])
                                            #print(type(values), values)
                                            portfoliodict = {'Shares': values[0],'Symbol ': values[1],'Price': values[2],'Day Change': values[3],'Market Value': values[4],'Total Invested (includes fees) ': values[5],'Cost Basis ': values[6],'Profit / Loss ': values[7]}
                                            portfolio = pd.DataFrame(data=portfoliodict).dropna(axis=1,how='all').dropna(axis=0,thresh=6)
                                            df['Market Value'] = df['Market Value'].apply(lambda x: x.replace('$', '').replace(',', '')
                                                                    if isinstance(x, str) else x).astype(float)
                                            #print(portfolio.columns)
                                            for i in portfolio['Total Invested (includes fees) '].to_list():
                                                portfolio2 = portfolio
                                                portfolio2['new'] = portfolio2['Total Invested (includes fees) ']
                                                portfolio2 = portfolio2.set_index('new')
                                                df.loc[portfolio2.loc[i,'Symbol '], 'Total Invested (includes fees) '] = i
                                            #print(df.loc[portfolio2.loc[i,'Symbol '], 'Total Invested (includes fees) '])
                                            for i in portfolio['Cost Basis '].to_list():
                                                portfolio2 = portfolio
                                                portfolio2['new'] = portfolio2['Cost Basis ']
                                                portfolio2 = portfolio2.set_index('new')
                                            #print(portfolio2.head(30))
                                            #return
                                                df.loc[portfolio2.loc[i,'Symbol '], 'Cost Basis '] = i
                                                #print(i)
                                            #print(df.loc[portfolio2.loc[i,'Symbol '], 'Cost Basis '])
                                            df['Total Invested (includes fees) '] = df['Total Invested (includes fees) '].apply(lambda x: x.replace('$', '').replace(',', '')
                                                            if isinstance(x, str) else x).astype(float)
                                            df.loc[str(args[2]),'Shares'] = totalInvested
                                            df.loc[str(args[2]),'Total Invested (includes fees) '] += totalCost
                                            df.loc[str(args[2]),'Cost Basis '] = df.loc[str(args[2]),'Total Invested (includes fees) '] / df.loc[str(args[2]),'Shares']
                                            df["Market Value"] = df['Shares'] * df['Market Price']
                                            df['Profit / Loss '] = df['Market Value'].astype(float) - df['Total Invested (includes fees) '].astype(float)
                                            request = service.spreadsheets().values().get(spreadsheetId=spreadoutsdf.loc[rpo, 'sheetID'], range='Visuals!C31:C39', majorDimension = 'COLUMNS', valueRenderOption = 'UNFORMATTED_VALUE')
                                            response = request.execute()
                                            history = response['values']
                                            history = [ item for elem in history for item in elem]
                                            sum = df['Market Value'].sum() #Gets the sum of the stock prices
                                            history.append(sum)
                                            history.insert(0, sum)
                                            history = np.array(history)
                                            history = history.astype(float)
                                            minimum = min(history)*0.8
                                            maximum = max(history)*1.2
                                            minmax = [minimum, maximum] #these lines do stuff to get the min and max values for the line graph
                                            history = [str(round(x,2)) for x in history]
                                            history = list(history)
                                            totalInvested = df['Total Invested (includes fees) '].sum()*1.02
                                            print(rpo)
                                            batch_update_values_request_body = {
                                                "value_input_option" : 'USER_ENTERED',  # How the input data should be interpreted.
                                                "data": [
                                                    {"range": 'A11:H44',
                                                    "majorDimension":'COLUMNS',
                                                    "values": [
                                                        df['Shares'].astype(float).tolist(),
                                                        df['Symbol'].tolist(),
                                                        df['Market Price'].astype(float).tolist(),
                                                        df['Day change'].tolist(),
                                                        df['Market Value'].astype(float).tolist(),
                                                        df['Total Invested (includes fees) '].astype(float).tolist(),
                                                        df['Cost Basis '].tolist(),
                                                        df['Profit / Loss '].astype(float).tolist()]},#Converts dataframe into the form needed to send to google sheets
                                                    {"range": 'E4:H4',
                                                    "majorDimension":'ROWS',
                                                    "values":[[sum, totalInvested, "", sum - totalInvested]]
                                                    },
                                                    {"range": 'Visuals!C30:C40',
                                                    "majorDimension":'COLUMNS',
                                                    "values":[history]
                                                    },
                                                    {"range": 'Visuals!A14:A15',
                                                    "majorDimension":'COLUMNS',
                                                    "values":[minmax]
                                                    }
                                                    ]#Prepares full list of values that need to be sent to the spreadsheet 
                                            }
                                            request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadoutsdf.loc[rpo, 'sheetID'], body=batch_update_values_request_body)
                                            response = request.execute() #updates spreadsheet
                                            df2 = pd.read_csv(UserListURL)
                                            df2['userID'] = df2['userID'].astype(str)
                                            df2['new'] = df2['userID']
                                            df2 = df2.set_index('new')
                                            accountBalanceSheet.loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'Account Balance'] -= totalCost
                                            coinsRemaining = accountBalanceSheet.loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'Account Balance']
                                            df2.loc[str(225344348903047168), 'Coin Amount'] += taxCost
                                            remainingCoins = df2.loc[str(message.author.id), 'Coin Amount']
                                            embeddict = {'color': 6345206, 'type': 'rich', 'description': message.author.display_name + ', you have bought **'+ str(args[3]) + '** share(s) in **'+ str(args[2]) +'** for a total cost of **'+str(totalCost)  +'** Funds, **'+ str(costForAmount) + '** Funds for that shares and **'+str(taxCost) +'** Funds in transaction fees. Your RPO now has **' + str(round(coinsRemaining,2)) +'** Funds left.'}
                                            gc = gspread.service_account(filename='service_account.json') #gets credentials
                                            sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
                                            worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
                                            # APPEND DATA TO SHEET
                                            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                                            set_with_dataframe(worksheet, df2) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                                            gc = gspread.service_account(filename='service_account.json') #gets credentials
                                            sh = gc.open_by_key(data['RPOinfoID'])
                                            worksheet = sh.get_worksheet(0)
                                            set_with_dataframe(worksheet, accountBalanceSheet)
                                            await message.channel.send(embed=discord.Embed.from_dict(embeddict))
                                        else:
                                            await message.channel.send("<:KSplodes:896043440872235028> Error: Cost for requested transaction: " + str(totalCost) +" is greater than the amount of currency your RPO has in it's account: " +str(wealth)+'.') 
                                    elif int(args[3]) <= 0:
                                        await message.channel.send("<:KSplodes:896043440872235028> Error: Invalid argument in position 3: " + str(args[3]) + ". Argument must be a positive integer.")
                                else:
                                    await message.channel.send("<:KSplodes:896043440872235028> Error: Invalid argument in position 2: " + str(args[2]) + ". Argument one must be one of the public stocks.")
                            else:
                                await message.channel.send("<:KSplodes:896043440872235028> Error: Invalid argument in position 1: " + str(args[1]) + ". Argument one must be `Coins` for discord currency, or `Funds` for the currency in your RPO's account.")

                elif message.content.startswith('sellShares') or message.content.startswith('SellShares') or message.content.startswith('Sellshares'): #args: <Symbol> <Amount>:
                    if message.channel.id != 687817008355737606:
                        return
                    author = message.author
                    userid = author.id
                    if message.author.id == 225344348903047168:
                        await message.channel.send('<:KSplodes:896043440872235028> Error: Charlie and The Celestial Project are not allowed to invest.')
                        return
                    args = message.content.split()
                    if str(userid) not in pd.read_csv(UserListURL)['userID'].astype(str).to_list():
                        await message.channel.send("<:KSplodes:896043440872235028> Error: Not registered in an RPO for the bot. Please register with the bot through !joinRPO <RPO_Tag>")
                        return
                    elif pd.read_csv(UserListURL, index_col=0).loc[userid,'RPO'] == 'A':
                        await message.channel.send("<:KSplodes:896043440872235028> Error: Invalid in an RPO for investing. Please change your RPO !changeRPO <New_RPO_Tag>")
                        return
                    elif str(userid) in pd.read_csv(UserListURL)['userID'].astype(str).to_list():
                        Investmentsdf = pd.read_csv(InvestorsURL, index_col=0).dropna(axis=1, how='all')
                        await message.channel.send("Investing for: " + pd.read_csv(UserListURL, index_col=0).loc[userid,'RPO'])
                        if not pd.read_csv(SSaccessURL, index_col=0).loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'hasInvested']:
                            sheet = pyg.open_by_key(pd.read_csv(SSaccessURL, index_col=0).loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'sheetID'])
                            sheet.share("", role='reader', type='anyone')
                            SSaccess = pd.read_csv(SSaccessURL)
                            SSaccess['new'] = SSaccess['rpo']
                            SSaccess = SSaccess.set_index('new')
                            SSaccess.loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'hasInvested'] = True
                            gc = gspread.service_account(filename='service_account.json') #gets credentials
                            sh = gc.open_by_key(data['SSaccessID']) #gets sheetinfo
                            worksheet = sh.get_worksheet(7) #-> 0 - first sheet, 1 - second sheet etc. 
                            # APPEND DATA TO SHEET
                            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                            set_with_dataframe(worksheet, SSaccess) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                        await message.author.send('Link to Investment sheet: https://docs.google.com/spreadsheets/d/{0}'.format(pd.read_csv(SSaccessURL, index_col=0).loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'sheetID']))
                        userList = pd.read_csv(UserListURL)
                        userList["new"] = userList['userID']
                        userList = userList.set_index("new")
                        args = message.content.split()
                        print(args)
                        Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
                        Investmentsdf = pd.read_csv(InvestorsURL) #Creates the data frame for investors
                        Investmentsdf['new'] = Investmentsdf['RPO']
                        Investmentsdf = Investmentsdf.set_index('new')
                        spreadoutsdf = pd.read_csv(SSaccessURL, index_col=0) #creates the data frame that we reference to get the info needed to push stuff to spreadsheets
                        df = pd.DataFrame(Investmentsdf.loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO']]) #creates the data frame with the specific investments with just one rpo
                        df = df.reset_index() #fixes the data frame so it can be concatenated with with the market value data frame
                        Marketdf = Marketdf.reset_index() #fixes the data frame so it can be concatenated with the specific investments data frame
                        try:
                            args[1] = args[1].upper()
                            args[2]
                            try:
                                int(args[2])
                            except:
                                await message.channel.send("<:KSplodes:896043440872235028> Error: `"+ str(args[2]) +"` is invalid argument for number of shares.")
                                return
                        except:
                            await message.channel.send("<:KSplodes:896043440872235028> Error: sellShares requires 2 arguments separated by spaces: `Symbol` and `Amount to Sell`")
                            return
                        finally:
                            accountBalanceSheet = pd.read_csv(RPOInfoURL)
                            accountBalanceSheet['new'] = accountBalanceSheet['TAG']
                            accountBalanceSheet = accountBalanceSheet.set_index('new')
                            accountBalanceSheet['Account Balance'] = accountBalanceSheet['Account Balance'].apply(lambda x: x.replace('$', '').replace(',', '')
                            if isinstance(x, str) else x).astype(float)
                            rpo = pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO']
                            wealth = float(accountBalanceSheet.loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'Account Balance'])
                            if int(args[2]) > Investmentsdf.loc[rpo, str(args[1])]:
                                await message.channel.send("<:KSplodes:896043440872235028> Error: you cannot sell more shares than you own.")
                                return
                            elif args[1] in pd.read_csv(URL, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0)['Symbol'].to_list():
                                if int(args[2]) > 0:
                                    Marketdf['new'] = Marketdf['Symbol']
                                    Marketdf = Marketdf.set_index('new')
                                    costForOne = Marketdf.loc[str(args[1]), 'Market Price']
                                    costForAmount = round(costForOne * int(args[2]),2)
                                    taxCost = round(costForAmount * .02,2)
                                    payout = round(costForAmount - taxCost,2)
                                    Investmentsdf = pd.read_csv(InvestorsURL).dropna(axis=1, how='all')
                                    Investmentsdf['new'] = Investmentsdf['RPO']
                                    Investmentsdf = Investmentsdf.set_index('new')
                                    Investmentsdf.loc[rpo, str(args[1])] -= int(args[2])
                                    totalInvested = Investmentsdf.loc[rpo, str(args[1])]
                                    print(totalInvested)
                                    gc = gspread.service_account(filename='service_account.json') #gets credentials
                                    sh = gc.open_by_key(data['InvestersID']) #gets sheetinfo
                                    worksheet = sh.get_worksheet(6) #-> 0 - first sheet, 1 - second sheet etc. 
                                    # APPEND DATA TO SHEET
                                    #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                                    set_with_dataframe(worksheet, Investmentsdf) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                                    df = df.drop(0, axis=0).reset_index() #fixes the data frame so it can be concatenated with with the market value data frame
                                    Marketdf = Marketdf.reset_index() #fixes the data frame so it can be concatenated with the specific investments data frame
                                    print(df.head())
                                    print(Marketdf.head())
                                    df = pd.concat([df, Marketdf], axis = 1).dropna(axis=0).rename(columns={rpo:'Shares'}) #concatenates the two dataframes, removes private companies, and fixes a column title
                                    df['Market Value'] = df['Shares'].astype(float) * df['Market Price'].astype(float)  #does the math to make the market value column
                                    df['new'] = df['Symbol']
                                    df = df.set_index('new')
                                    df['Total Invested (includes fees) '] = 0
                                    df['Cost Basis '] = 0
                                    print('https://docs.google.com/spreadsheets/d/{0}'.format(spreadoutsdf.loc[rpo, 'sheetID']))
                                    #portfolio = pd.read_csv('https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(spreadoutsdf.loc[rpo, 'sheetID'],spreadoutsdf.loc[rpo, 'gid1']), dtype={'Market Value':str, 'Total Invested (includes fees) ': str}, skiprows=0).dropna(axis=1,how='all').dropna(axis=0,thresh=6)
                                    sheet = service.spreadsheets()
                                    result = sheet.values().get(spreadsheetId=spreadoutsdf.loc[rpo, 'sheetID'],
                                                            range='A11:H44', majorDimension='COLUMNS').execute()
                                    values = result.get('values', [])
                                    #print(type(values), values)
                                    portfoliodict = {'Shares': values[0],'Symbol ': values[1],'Price': values[2],'Day Change': values[3],'Market Value': values[4],'Total Invested (includes fees) ': values[5],'Cost Basis ': values[6],'Profit / Loss ': values[7]}
                                    portfolio = pd.DataFrame(data=portfoliodict).dropna(axis=1,how='all').dropna(axis=0,thresh=6)
                                    df['Market Value'] = df['Market Value'].apply(lambda x: x.replace('$', '').replace(',', '')
                                                            if isinstance(x, str) else x).astype(float)
                                    #print(portfolio.columns)
                                    for i in portfolio['Total Invested (includes fees) '].to_list():
                                        portfolio2 = portfolio
                                        portfolio2['new'] = portfolio2['Total Invested (includes fees) ']
                                        portfolio2 = portfolio2.set_index('new')
                                        df.loc[portfolio2.loc[i,'Symbol '], 'Total Invested (includes fees) '] = i
                                    #print(df.loc[portfolio2.loc[i,'Symbol '], 'Total Invested (includes fees) '])
                                    for i in portfolio['Cost Basis '].to_list():
                                        portfolio2 = portfolio
                                        portfolio2['new'] = portfolio2['Cost Basis ']
                                        portfolio2 = portfolio2.set_index('new')
                                    #print(portfolio2.head(30))
                                    #return
                                        df.loc[portfolio2.loc[i,'Symbol '], 'Cost Basis '] = i
                                        #print(i)
                                    #print(df.loc[portfolio2.loc[i,'Symbol '], 'Cost Basis '])
                                    df['Total Invested (includes fees) '] = df['Total Invested (includes fees) '].apply(lambda x: x.replace('$', '').replace(',', '')
                                                    if isinstance(x, str) else x).astype(float)
                                    df.loc[str(args[1]),'Shares'] = totalInvested
                                    print(df.loc[str(args[1]),'Shares'])
                                    df.loc[str(args[1]),'Total Invested (includes fees) '] -= payout
                                    Invested = df.loc[str(args[1]),'Total Invested (includes fees) ']
                                    df.loc[str(args[1]),'Cost Basis '] = df.loc[str(args[1]),'Total Invested (includes fees) '] / df.loc[str(args[1]),'Shares']
                                    df["Market Value"] = df['Shares'] * df['Market Price']
                                    df['Profit / Loss '] = df['Market Value'].astype(float) - df['Total Invested (includes fees) '].astype(float)
                                    profit = df.loc[str(args[1]),'Profit / Loss ']
                                    request = service.spreadsheets().values().get(spreadsheetId=spreadoutsdf.loc[rpo, 'sheetID'], range='Visuals!C31:C39', majorDimension = 'COLUMNS', valueRenderOption = 'UNFORMATTED_VALUE')
                                    response = request.execute()
                                    history = response['values']
                                    history = [ item for elem in history for item in elem]
                                    sum = df['Market Value'].sum() #Gets the sum of the stock prices
                                    history.append(sum)
                                    history.insert(0, sum)
                                    history = np.array(history)
                                    history = history.astype(float)
                                    minimum = min(history)*0.8
                                    maximum = max(history)*1.2
                                    minmax = [minimum, maximum] #these lines do stuff to get the min and max values for the line graph
                                    history = [str(round(x,2)) for x in history]
                                    history = list(history)
                                    totalInvested2 = df['Total Invested (includes fees) '].sum()*1.02
                                    print(rpo)
                                    df.replace([np.inf, -np.inf], 0, inplace=True)
                                    df.loc[str(args[1]),'Total Invested (includes fees) '] = Invested
                                    df.loc[str(args[1]),'Profit / Loss '] = profit
                                    df = df.dropna(axis=0)
                                    print(df.head())
                                    batch_update_values_request_body = {
                                        "value_input_option" : 'USER_ENTERED',  # How the input data should be interpreted.
                                        "data": [
                                            {"range": 'A11:H44',
                                            "majorDimension":'COLUMNS',
                                            "values": [
                                                df['Shares'].astype(float).tolist(),
                                                df['Symbol'].tolist(),
                                                df['Market Price'].astype(float).tolist(),
                                                df['Day change'].tolist(),
                                                df['Market Value'].astype(float).tolist(),
                                                df['Total Invested (includes fees) '].astype(float).tolist(),
                                                df['Cost Basis '].tolist(),
                                                df['Profit / Loss '].astype(float).tolist()]},#Converts dataframe into the form needed to send to google sheets
                                            {"range": 'E4:H4',
                                            "majorDimension":'ROWS',
                                            "values":[[sum, totalInvested2, "", sum - totalInvested2]]
                                            },
                                            {"range": 'Visuals!C30:C40',
                                            "majorDimension":'COLUMNS',
                                            "values":[history]
                                            },
                                            {"range": 'Visuals!A14:A15',
                                            "majorDimension":'COLUMNS',
                                            "values":[minmax]
                                            }
                                            ]#Prepares full list of values that need to be sent to the spreadsheet 
                                    }
                                    request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadoutsdf.loc[rpo, 'sheetID'], body=batch_update_values_request_body)
                                    response = request.execute() #updates spreadsheet
                                    df2 = pd.read_csv(UserListURL)
                                    df2['userID'] = df2['userID'].astype(str)
                                    df2['new'] = df2['userID']
                                    df2 = df2.set_index('new')
                                    accountBalanceSheet.loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'Account Balance'] += payout
                                    coinsRemaining = accountBalanceSheet.loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'Account Balance']
                                    df2.loc[str(225344348903047168), 'Coin Amount'] += taxCost
                                    embeddict = {'color': 6345206, 'type': 'rich', 'description': message.author.display_name + ', you have sold **'+ str(args[2]) + '** share(s) in **'+ str(args[1]) +'** for a total  of **'+str(costForAmount)  +'** Funds, **'+ str(taxCost) + '** have been diverted as a transaction fee. Your RPO recieved a payout of **'+str(payout) +'** Funds. Your RPO now has **' + str(round(coinsRemaining,2)) +'** Funds, and **' + str(totalInvested) +"** stocks left in **" +str(args[1])+"**."}
                                    gc = gspread.service_account(filename='service_account.json') #gets credentials
                                    sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
                                    worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
                                    # APPEND DATA TO SHEET
                                    #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                                    set_with_dataframe(worksheet, df2) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                                    gc = gspread.service_account(filename='service_account.json') #gets credentials
                                    sh = gc.open_by_key(data['RPOinfoID'])
                                    worksheet = sh.get_worksheet(0)
                                    set_with_dataframe(worksheet, accountBalanceSheet)
                                    await message.channel.send(embed=discord.Embed.from_dict(embeddict))
                                elif int(args[2]) <= 0:
                                    await message.channel.send("<:KSplodes:896043440872235028> Error: Invalid argument in position 2: " + str(args[2]) + ". Argument must be a positive integer.")
                            else:
                                await message.channel.send("<:KSplodes:896043440872235028> Error: Invalid argument in position 1: " + str(args[1]) + ". Argument one must be one of the public stocks.")
                                
                elif message.content.startswith('daily') or message.content.startswith('Daily'):
                    message = message
                    await message.delete()
                    isAllowed = False
                    for role in ['733541021488513035','225414319938994186','225414600101724170','225414953820094465','377254753907769355','338173415527677954','253752685357039617']:
                        if discord.utils.get(message.guild.roles, id=int(role)) in message.author.roles:
                            isAllowed = True
                        else:
                            isAllowed
                    if isAllowed:
                        df = pd.read_csv(UserListURL)
                        df['userID'] = df['userID'].astype(str)
                        df['new'] = df['userID']
                        df = df.set_index('new')
                        lastWork = df.loc[str(message.author.id), 'lastDaily']
                        currentUse = time.mktime(message.created_at.timetuple())
                        timeDifference = currentUse - lastWork
                        if timeDifference < 71700:
                            await message.author.send("<:KSplodes:896043440872235028> Error: **" + message.author.display_name + "** You need to wait " + str(datetime.timedelta(seconds=71700-timeDifference)) + " more to use this command.")
                        elif timeDifference > 71700:
                            df.loc[str(message.author.id), 'lastDaily'] = currentUse
                            amount = 1500 #assigned number for daily
                            df.loc[str(message.author.id), 'Coin Amount'] += amount
                            embeddict = {'color': 6345206, 'type': 'rich', 'description': '<@!'+str(message.author.id) +'>, here is your daily reward: 1500 <:HotTips2:465535606739697664>'}
                            gc = gspread.service_account(filename='service_account.json') #gets credentials
                            sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
                            worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
                            # APPEND DATA TO SHEET
                            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                            set_with_dataframe(worksheet, df) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                            await message.author.send(embed=discord.Embed.from_dict(embeddict))
                    elif isAllowed == False:
                        await message.author.send("<:KSplodes:896043440872235028> Error: You are not allowed to use that command.")

                elif message.content.startswith('work') or message.content.startswith('Work'):
                    isAllowed = False
                    allowedids = ['837812373451702303','837812586997219372','837812662116417566','837812728801525781','837812793914425455','400445639210827786','685331877057658888','337743478190637077','837813262417788988','338173415527677954','253752685357039617']
                    for id in allowedids:
                        if discord.utils.get(message.guild.roles, id=int(id)) in message.author.roles:
                            isAllowed = True
                        else:
                            isAllowed
                    if isAllowed:
                        df = pd.read_csv(UserListURL)
                        df['userID'] = df['userID'].astype(str)
                        df['new'] = df['userID']
                        df = df.set_index('new')
                        lastWork = df.loc[str(message.author.id), 'lastWork']
                        currentUse = time.mktime(message.created_at.timetuple())
                        timeDifference = currentUse - lastWork
                        if timeDifference < 43200:
                            await message.channel.send("<:KSplodes:896043440872235028> Error: **" + message.author.display_name + "** You need to wait " + str(datetime.timedelta(seconds=43200-timeDifference)) + " more to use this command.")
                        elif timeDifference > 43200:
                            df.loc[str(message.author.id), 'lastWork'] = currentUse
                            amount = random.randrange(800, 1200, 5) #generates random number from 800 to 1200, in incrememnts of 5 (same as generating a radom number between 40 and 120, and multiplying it by 5)
                            lastamount = int(df.loc[str(message.author.id), 'lastWorkAmount'])
                            df.loc[str(message.author.id), 'Coin Amount'] += lastamount
                            df.loc[str(message.author.id), 'lastWorkAmount'] = amount
                            embeddict = {'color': 6345206, 'type': 'rich', 'description': message.author.display_name + ', you started working again. You gain '+ str(lastamount) +' <:HotTips2:465535606739697664> from your last work. Come back in **12 hours** to claim your paycheck of '+ str(amount) + ' <:HotTips2:465535606739697664> and start working again with `!work`'}
                            gc = gspread.service_account(filename='service_account.json') #gets credentials
                            sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
                            worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
                            # APPEND DATA TO SHEET
                            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                            set_with_dataframe(worksheet, df) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                            await message.channel.send(embed=discord.Embed.from_dict(embeddict))
                    elif isAllowed == False:
                        await message.channel.send("<:KSplodes:896043440872235028> Error: You are not allowed to use that command.")
                    await message.delete()

                elif message.content.startswith('coins') or message.content.startswith('Coins'):
                    if str(message.author.id) not in pd.read_csv(UserListURL)['userID'].astype(str).to_list(): #makes sure user isn't already in an RPO
                        await message.channel.send("<:KSplodes:896043440872235028> Error: You are not registered in an RPO to me.")
                        return
                    elif message.mentions == []:
                        df = pd.read_csv(UserListURL, index_col=0)
                        funds = df.loc[message.author.id, 'Coin Amount']
                        embeddict = {'color': 6345206, 'type': 'rich', 'description': '<@!'+ str(message.author.id) + '> has ' + str(funds) + '<:HotTips2:465535606739697664>'}
                        await message.author.send(embed=discord.Embed.from_dict(embeddict))
                    elif message.mentions != []:
                        df = pd.read_csv(UserListURL, index_col=0)
                        funds = df.loc[message.mentions[0].id, 'Coin Amount']
                        embeddict = {'color': 6345206, 'type': 'rich', 'description': '<@!'+ str(message.mentions[0].id) + '> has ' + str(funds) + '<:HotTips2:465535606739697664>'}
                        await message.author.send(embed=discord.Embed.from_dict(embeddict))
                    await message.delete()
                    


                return



with open('bottoken.json') as t:
    token = json.load(t)['Token']
client = MyClient()
client.run(token)