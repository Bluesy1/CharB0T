from __future__ import print_function
import asyncio
from collections import namedtuple
import os.path
from pydoc import cli
from discord import channel, client
from discord.ext.commands.bot import Bot
from googleapiclient.discovery import build
import gspread
from gspread.models import Spreadsheet
from gspread_dataframe import set_with_dataframe
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pandas as pd
import numpy as np
import json
import discord
from discord.ext import commands
import logging
from pandas._config.config import options
import pygsheets
import time
import datetime
import random
import re
import sfsutils as sfs
from discord_ui import *
import discord_ui
import os
import matplotlib.pyplot as plt
from logging.handlers import RotatingFileHandler
from matplotlib.backends.backend_pdf import PdfPages
import auxone as a
import grabber
from cryptography.fernet import Fernet
import fpdf
#imports all needed packages
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(filename='discord.log', encoding='utf-8', mode='w', maxBytes=2000000, backupCount=10)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
#Creates a log for the discord bot, good for debugging
# If modifying these scopes, delete the file token.json. (The end user (In this case You charlie, shouldn't have to do that because i'm not changing the scope unless i have to later))
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
# The ID and range of a sample spreadsheet.
with open('details.json') as f:
    data = json.load(f) 
with open('filekey.key','rb') as file:
    key = file.read()
    fernet = Fernet(key)
URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['googleSheetId'],
    data['workSheetName'])
InvestorsURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['InvestersID'],
    data['Investorssheetgid'])
SSaccessURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['SSaccessID'],
    data['SSaccessgid'])
UserListURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['UserListID'],
    data['UserListgid'])
RPOInfoURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['RPOinfoID'],
    data['RPOinfogid']) 
RPOKnowledgeURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['RPOKnowledgeID'],
    data['RPOKnowledgegid']) #these make the URLS needed for pandas to read the needed CSVs, in combination with the details.json file
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
def refreshToken():
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
    service = build('sheets', 'v4', credentials=creds)
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
pyg = pygsheets.authorize(client_secret='credentials.json') #Inits the pygsheets api
service = build('sheets', 'v4', credentials=creds)


Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
Investmentsdf = pd.read_csv(InvestorsURL, index_col=0).dropna(axis=1, how='all') #Creates the data fram for investors
RPOlist = list() #initializes empty list for list of RPOs with investments
spreadoutsdf = pd.read_csv(SSaccessURL, index_col=0)
techdict = {}

userList = pd.read_csv(UserListURL, index_col=0) 

with open('bottoken.json') as t:
    token = json.load(t)['Token']

client = commands.Bot(command_prefix='!')
ui = discord_ui.UI(client)
client.remove_command('help')

@client.command()
@commands.cooldown(1, 30.0, commands.BucketType.guild)
async def buyShares(message):
    refreshToken()
    if a.channel_check(message, [687817008355737606,893867549589131314,900523609603313704]) != True:
        return
    author = message.author
    userid = author.id
    if message.author.id == 225344348903047168:
        await message.channel.send('<:KSplodes:896043440872235028> Error: Charlie and The Celestial Project are not allowed to invest.')
        return
    args = message.message.content.split()
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
            gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
            sh = gc.open_by_key(data['SSaccessID']) #gets sheetinfo
            worksheet = sh.get_worksheet(7) #-> 0 - first sheet, 1 - second sheet etc. 
            # APPEND DATA TO SHEET
            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
            set_with_dataframe(worksheet, SSaccess) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
        await message.author.send('Link to Investment sheet: https://docs.google.com/spreadsheets/d/{0}'.format(pd.read_csv(SSaccessURL, index_col=0).loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'sheetID']))
        userList = pd.read_csv(UserListURL)
        userList["new"] = userList['userID']
        userList = userList.set_index("new")
        args = message.message.content.split()
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
            await message.channel.send("<:KSplodes:896043440872235028> Error: !buyShares requires 3 arguments separated by spaces: `Coins/Funds`, `Symbol`, and `Amount to Buy`")
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
                            gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
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
                            totalInvested = df['Total Invested (includes fees) '].sum()
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
                                    "values":[['$'+str(sum), totalInvested, "", "$"+str(sum - totalInvested)]]
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
                            gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
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
                            gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
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
                            totalInvested = df['Total Invested (includes fees) '].sum()
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
                                    "values":[['$'+str(sum), totalInvested, "", "$"+str(sum - totalInvested)]]
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
                            gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
                            sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
                            worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
                            # APPEND DATA TO SHEET
                            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                            set_with_dataframe(worksheet, df2) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                            gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
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

@client.command()
@commands.cooldown(1, 30.0, commands.BucketType.guild)
async def sellShares(message):
    refreshToken()
    if a.channel_check(message, [687817008355737606,893867549589131314,900523609603313704]) != True:
        return
    author = message.author
    userid = author.id
    if message.author.id == 225344348903047168:
        await message.channel.send('<:KSplodes:896043440872235028> Error: Charlie and The Celestial Project are not allowed to invest.')
        return
    args = message.message.content.split()
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
            gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
            sh = gc.open_by_key(data['SSaccessID']) #gets sheetinfo
            worksheet = sh.get_worksheet(7) #-> 0 - first sheet, 1 - second sheet etc. 
            # APPEND DATA TO SHEET
            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
            set_with_dataframe(worksheet, SSaccess) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
        await message.author.send('Link to Investment sheet: https://docs.google.com/spreadsheets/d/{0}'.format(pd.read_csv(SSaccessURL, index_col=0).loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'sheetID']))
        userList = pd.read_csv(UserListURL)
        userList["new"] = userList['userID']
        userList = userList.set_index("new")
        args = message.message.content.split()
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
            await message.channel.send("<:KSplodes:896043440872235028> Error: !sellShares requires 2 arguments separated by spaces: `Symbol` and `Amount to Sell`")
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
                    gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
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
                    totalInvested2 = df['Total Invested (includes fees) '].sum()
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
                            "values":[['$'+str(sum), totalInvested2, "", "$"+str(sum - totalInvested2)]]
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
                    gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
                    sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
                    worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
                    # APPEND DATA TO SHEET
                    #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                    set_with_dataframe(worksheet, df2) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                    gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
                    sh = gc.open_by_key(data['RPOinfoID'])
                    worksheet = sh.get_worksheet(0)
                    set_with_dataframe(worksheet, accountBalanceSheet)
                    await message.channel.send(embed=discord.Embed.from_dict(embeddict))
                elif int(args[2]) <= 0:
                    await message.channel.send("<:KSplodes:896043440872235028> Error: Invalid argument in position 2: " + str(args[2]) + ". Argument must be a positive integer.")
            else:
                await message.channel.send("<:KSplodes:896043440872235028> Error: Invalid argument in position 1: " + str(args[1]) + ". Argument one must be one of the public stocks.")

@client.command()
@commands.cooldown(1, 86400.0, commands.BucketType.user)
async def changeRPO(message):
    refreshToken()
    if a.channel_check(message, [687817008355737606,893867549589131314]) != True:
        await message.message.delete()
        return
    author = message.author
    userid = author.id
    RPO  = message.message.content.split()[-1].upper()
    if RPO not in pd.read_csv(RPOInfoURL, index_col=0, usecols=['FULL NAME', 'TAG', 'Account Balance'])['TAG'].astype(str).to_list():
        await message.channel.send("<:KSplodes:896043440872235028> Error: RPO " +RPO + " is not a registered RPO")
        return
    elif RPO == 'CP':
        await message.channel.send("<:KSplodes:896043440872235028> Error: You cannot change to the RPO CP")
    else:
        df = pd.read_csv(UserListURL)
        df['userID'] = df['userID'].astype(str)
        df['new'] = df['userID']
        df = df.set_index('new')
        df.loc[str(message.author.id), 'RPO'] = RPO
        gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
        sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
        worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
        # APPEND DATA TO SHEET
        #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
        set_with_dataframe(worksheet, df) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
        print("<@!"+str(message.author.id) + "> you are now in RPO " + str(RPO))
        name = message.author.display_name
        try:
            newname, count = re.subn("(?<=\[)[^\[\]]{2,4}(?=\])",RPO,name)
            if (count == 0):
                newname = name + " [" + RPO + "]"
            await message.author.edit(nick=newname)
        finally:
            Kerbal = message.guild.get_role(906000578092621865)
            await message.author.add_roles(Kerbal)
            await message.channel.send("<@!"+str(message.author.id) + "> you are now in RPO " + RPO + ".")

@client.command()
@commands.cooldown(5, 3600.0, commands.BucketType.user)
async def daily(message):
    if a.author_check2(message,[82495450153750528,755539532924977262]):
        await message.message.delete()
        return
    elif a.channel_check(message, [893867549589131314, 687817008355737606, 839690221083820032]) != True:
        await message.message.delete()
        return
    message = message
    await message.message.delete()
    if str(message.author.id) not in pd.read_csv(UserListURL)['userID'].astype(str).to_list(): #makes sure user isn't already in an RPO
        a.undeclared(message)
    isAllowed = False
    if a.role_check(message, ['733541021488513035','225414319938994186','225414600101724170','225414953820094465','377254753907769355','338173415527677954','253752685357039617']):
        df = pd.read_csv(UserListURL)
        df['userID'] = df['userID'].astype(str)
        df['new'] = df['userID']
        df = df.set_index('new')
        lastWork = df.loc[str(message.author.id), 'lastDaily']
        currentUse = time.mktime(message.message.created_at.timetuple())
        timeDifference = currentUse - lastWork
        if timeDifference < 71700:
            await message.author.send("<:KSplodes:896043440872235028> Error: **" + message.author.display_name + "** You need to wait " + str(datetime.timedelta(seconds=71700-timeDifference)) + " more to use this command.")
        elif timeDifference > 71700:
            df.loc[str(message.author.id), 'lastDaily'] = currentUse
            amount = 1500 #assigned number for daily
            df.loc[str(message.author.id), 'Coin Amount'] += amount
            embeddict = {'color': 6345206, 'type': 'rich', 'description': '<@!'+str(message.author.id) +'>, here is your daily reward: 1500 <:HotTips2:465535606739697664>'}
            gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
            sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
            worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
            # APPEND DATA TO SHEET
            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
            set_with_dataframe(worksheet, df) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
            await message.author.send(embed=discord.Embed.from_dict(embeddict))
    elif isAllowed == False:
        await message.author.send("<:KSplodes:896043440872235028> Error: You are not allowed to use that command.")

@client.command()
@commands.cooldown(5, 3600.0, commands.BucketType.user)
async def work(message):
    if a.author_check2(message,[82495450153750528,755539532924977262]):
        await message.message.delete()
        return
    elif a.channel_check(message, [893867549589131314, 687817008355737606, 839690221083820032]) != True:
        await message.message.delete()
        return
    elif str(message.author.id) not in pd.read_csv(UserListURL)['userID'].astype(str).to_list():
        a.undeclared(message)
    if a.role_check(message, ['837812373451702303','837812586997219372','837812662116417566','837812728801525781','837812793914425455','400445639210827786','685331877057658888','337743478190637077','837813262417788988','338173415527677954','253752685357039617']):
        df = pd.read_csv(UserListURL)
        df['userID'] = df['userID'].astype(str)
        df['new'] = df['userID']
        df = df.set_index('new')
        lastWork = df.loc[str(message.author.id), 'lastWork']
        currentUse = time.mktime(message.message.created_at.timetuple())
        timeDifference = currentUse - lastWork
        if timeDifference < 41400:
            await message.channel.send("<:KSplodes:896043440872235028> Error: **" + message.author.display_name + "** You need to wait " + str(datetime.timedelta(seconds=41400-timeDifference)) + " more to use this command.")
        elif timeDifference > 41400:
            df.loc[str(message.author.id), 'lastWork'] = currentUse
            amount = random.randrange(800, 1200, 5) #generates random number from 800 to 1200, in incrememnts of 5 (same as generating a radom number between 40 and 120, and multiplying it by 5)
            lastamount = int(df.loc[str(message.author.id), 'lastWorkAmount'])
            df.loc[str(message.author.id), 'Coin Amount'] += lastamount
            df.loc[str(message.author.id), 'lastWorkAmount'] = amount
            embeddict = {'color': 6345206, 'type': 'rich', 'description': message.author.display_name + ', you started working again. You gain '+ str(lastamount) +' <:HotTips2:465535606739697664> from your last work. Come back in **12 hours** to claim your paycheck of '+ str(amount) + ' <:HotTips2:465535606739697664> and start working again with `!work`'}
            gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
            sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
            worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
            # APPEND DATA TO SHEET
            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
            set_with_dataframe(worksheet, df) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
            await message.channel.send(embed=discord.Embed.from_dict(embeddict))
    else:
        await message.channel.send("<:KSplodes:896043440872235028> Error: You are not allowed to use that command.")

@client.command()
@commands.cooldown(3, 300.0, commands.BucketType.user)
async def joinRPO(message):
    refreshToken()
    if message.channel.id != 687817008355737606 and message.channel.id != 893867549589131314:
        await message.message.delete()
        return
    author = message.author
    userid = author.id
    RPO  = message.message.content.split()[-1].upper()
    if str(userid) in pd.read_csv(UserListURL)['userID'].astype(str).to_list(): #makes sure user isn't already in an RPO
        if pd.read_csv(UserListURL)['userID'].astype(str).to_list() == 'A':
            await message.channel.send("<:KSplodes:896043440872235028> Error: You have already been registered as undeclared. To change your status, please use `!changeRPO` followed by your new tag.")
        else:
            await message.channel.send("<:KSplodes:896043440872235028> Error: You are already in an RPO: " + pd.read_csv(UserListURL, index_col=0).loc[userid, 'RPO'])
        return

    elif RPO not in pd.read_csv(RPOInfoURL, index_col=0, usecols=['FULL NAME', 'TAG', 'Account Balance'])['TAG'].astype(str).to_list(): #makes sure RPO trying to be joined exists
        if RPO == 'A':
                rpo = RPO
                newUser = {'userID':[str(userid)], 'RPO':RPO, 'Author':[author], 'Coin Amount': [0], 'lastWorkAmount': [0], 'lastWork': [0], 'lastDaily': [0]}
                df = pd.DataFrame(newUser).set_index('userID')
                df2 = pd.DataFrame(newUser)
                userList = pd.read_csv(UserListURL, index_col=0).append(pd.DataFrame(newUser))
                userListOutput = pd.read_csv(UserListURL).append(df2)
                userListOutput['userID'] = userListOutput['userID'].astype(str)
                gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
                sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
                worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
                # APPEND DATA TO SHEET
                #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                set_with_dataframe(worksheet, userListOutput) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                print("<@!"+str(message.author.id) + "> you are now in RPO " + str(newUser['RPO'][0]))
                await message.channel.send("<@!"+str(message.author.id) + "> you are registered with the bot.")
        else:
            await message.channel.send("<:KSplodes:896043440872235028> Error: RPO " +RPO + " is not a registered RPO")
            return
    elif RPO == 'CP':
        await message.channel.send("<:KSplodes:896043440872235028> Error: You cannot join the RPO CP")
    elif str(userid) not in pd.read_csv(UserListURL)['userID'].astype(str).to_list():
        rpo = RPO
        newUser = {'userID':[str(userid)], 'RPO':RPO, 'Author':[author], 'Coin Amount': [0], 'lastWorkAmount': [0], 'lastWork': [0], 'lastDaily': [0]}
        df = pd.DataFrame(newUser).set_index('userID')
        df2 = pd.DataFrame(newUser)
        userList = pd.read_csv(UserListURL, index_col=0).append(pd.DataFrame(newUser))
        userListOutput = pd.read_csv(UserListURL).append(df2)
        userListOutput['userID'] = userListOutput['userID'].astype(str)
        gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
        sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
        worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
        # APPEND DATA TO SHEET
        #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
        set_with_dataframe(worksheet, userListOutput) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
        print("<@!"+str(message.author.id) + "> you are now in RPO " + str(newUser['RPO'][0]))
        name = message.author.display_name
        try:
            newname, count = re.subn("(?<=\[)[^\[\]]{2,4}(?=\])",RPO,name)
            if (count == 0):
                newname = name + " [" + RPO + "]"
            await message.author.edit(nick=newname)
        except:
            RPO
        Kerbal = message.guild.get_role(906000578092621865)
        await message.author.add_roles(Kerbal)
        await message.channel.send("<@!"+str(message.author.id) + "> you are now in RPO " + rpo)

@ui.slash.command(name='key', description="Key for colors in part tables", guild_ids=[225345178955808768], guild_permissions={225345178955808768: SlashPermission(allowed={"225345178955808768": SlashPermission.ROLE},forbidden={"684936661745795088":SlashPermission.ROLE,"676250179929636886":SlashPermission.ROLE})})
async def command(ctx):
    df = pd.DataFrame()
    colors = ["dark teal","rose","chartreuse","blue","goldenrod","grape","kelly green","ocean blue","puke green","light violet","robin's egg blue","puce","neon green","canary yellow","light navy","bright pink","rust","grey","periwinkle","dark red"]
    df['Color'] = colors
    df['Type'] = ["Aerodynamics","Balloon","Camera","Capsule","Comms","Control","Coupling","Engine","Equipment","Landing","Lights","Mining","Parachute","Power","Probe","Science","Storage","Structure","Tank","Thermal"]
    colorList = list()
    for i in colors:
        subList = ["xkcd:"+i,"xkcd:"+i]
        colorList.append(subList)
    a.render_mpl_table_colors(df,Colors=colorList, header_columns=0, col_width=5.0, alpha=0.5)
    await ctx.author.send(file=discord.File(r'table.png'))

@ui.slash.command(name='allparts', description="All parts in the game, only unlocked ones will be highlighted.", guild_ids=[225345178955808768], guild_permissions={225345178955808768: SlashPermission(allowed={"225345178955808768": SlashPermission.ROLE},forbidden={"684936661745795088":SlashPermission.ROLE,"676250179929636886":SlashPermission.ROLE})})
async def command(ctx):
    await ctx.defer(hidden=True)
    with open('parts.json') as p:
        partsDict = json.load(p)
    data2 = sfs.parse_savefile('completed.sfs')
    tech = data2['GAME']['SCENARIO'][7]['Tech'] #6 current, 7 new
    data = sfs.parse_savefile('persistent.sfs')
    tech2 = data['GAME']['SCENARIO'][6]['Tech']
    length = len(tech)
    i = 0
    techdict = {}
    while i < length:
        if tech[i]['id'] not in ['tremendousEfficiencyPropulsion', 'veryHighEfficiencyPropulsion', 'advColonization', 'exoticRadiators', 'microwavePowerTransmission', 'exoticElectricalSystems', 'experimentalElectricalSystems', 'highPowerElectricalSystems', 'exoticPlasmaPropulsion', 'appliedHighEnergyPhysics', 'highEnergyScience', 'scientificOutposts', 'resourceExploitation', 'advOffworldMining', 'advAerospaceEngineering', 'expAircraftEngines', 'offworldManufacturing', 'extremeFuelStorage', 'colossalRocketry', 'giganticRocketry', 'fusionRockets', 'ultraHighEnergyPhysics', 'unifiedFieldTheory', 'antimatterPower', 'quantumReactions', 'exoticReactions', 'advFusionReactions', 'fusionPower', 'experimentalMotors']:
            techdict.update({tech[i]['id']:tech[i]['part']})
        i += 1
    dfOut=pd.DataFrame()
    maxLen = 0
    for i in list(techdict.keys()):
        #techdict[i] = [re.sub(r".v[1-9]","",item) for item in techdict[i]]
        if i in ["highEfficiencyPropulsion","heatManagementSystems","expGriddedThrusters","longTermScienceTech","heavyLanders","specializedLanders","exoticNuclearPropulsion","exoticNuclearPower","advNuclearPower","largeNuclearPower","nuclearPower","aerospaceTech"]:
            techdict[i] = [techdict[i]]
        elif type(techdict[i])==list:
            techdict[i] = list(set(techdict[i]))
        elif type(techdict[i])==str:
            techdict[i] = [techdict[i]]
        maxLen = max(maxLen, len(techdict[i]))
    for i in list(techdict.keys()):
        if techdict[i] != None:
            diff = maxLen-len(techdict[i])
            while diff >0:
                techdict[i].append('')
                diff = maxLen-len(techdict[i])
    columns = 0
    with PdfPages(r'Tables.pdf') as export_pdf:
        for i in list(techdict.keys()):
            dfOut[i] = techdict[i]
            columns +=1
            if columns==5:
                dfOut.drop_duplicates(inplace=True)
                colDepth = len(dfOut.columns.tolist())
                rowDepth = len(dfOut.index.tolist())-1
                onRow = 0
                onCol = 0
                colorList = list()
                while onRow<rowDepth:
                    tempList = list()
                    while onCol<colDepth:
                        if a.part_check(tech2,dfOut.iloc[onRow,onCol]):
                            tempList.append("w")
                        elif bool(re.search(r"Aerodynamics",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:dark teal")
                        elif bool(re.search(r"balloon",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:rose")
                        elif bool(re.search(r"Camera",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:chartreuse")
                        elif bool(re.search(r"Capsule ",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:blue")
                        elif bool(re.search(r"antenna",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:goldenrod")
                        elif bool(re.search(r"comms",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:goldenrod")
                        elif bool(re.search(r"Control",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:grape")
                        elif bool(re.search(r"Coupling",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:kelly green")
                        elif bool(re.search(r"Engine",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:ocean blue")
                        elif bool(re.search(r"Equipment",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:puke green")
                        elif bool(re.search(r"Landing",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:light violet")
                        elif bool(re.search(r"Lights",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:robin's egg blue")
                        elif bool(re.search(r"Mining",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:puce")
                        elif bool(re.search(r"Parachute",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:neon green")
                        elif bool(re.search(r"Power",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:canary yellow")
                        elif bool(re.search(r"Probe",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:light navy")
                        elif bool(re.search(r"Science",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:bright pink")
                        elif bool(re.search(r"Sensor",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:bright pink")
                        elif bool(re.search(r"Storage",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:rust")
                        elif bool(re.search(r"Structure",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:grey")
                        elif bool(re.search(r"Tank",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:periwinkle")
                        elif bool(re.search(r"Thermal",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:dark red")
                        else:
                            tempList.append('xkcd:cloudy blue')
                        try:dfOut.iloc[onRow,onCol] = partsDict[dfOut.iloc[onRow,onCol]]['name']
                        except:dfOut.iloc[onRow,onCol]=dfOut.iloc[onRow,onCol]
                        onCol+=1
                    onCol=0
                    onRow+=1
                    colorList.append(tempList)
                a.render_mpl_table_colors_pdf(export_pdf, dfOut[:-1],colorList, header_columns=0, col_width=7.5)
                dfOut = pd.DataFrame(None)
                columns = 0
        dfOut.drop_duplicates(inplace=True)
        colDepth = len(dfOut.columns.tolist())
        rowDepth = len(dfOut.index.tolist())-1
        onRow = 0
        onCol = 0
        colorList = list()
        while onRow<rowDepth:
            tempList = list()
            while onCol<colDepth:
                if a.part_check(tech2,dfOut.iloc[onRow,onCol]):
                    tempList.append("w")
                elif bool(re.search(r"Aerodynamics",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:dark teal")
                elif bool(re.search(r"balloon",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:rose")
                elif bool(re.search(r"Camera",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:chartreuse")
                elif bool(re.search(r"Capsule ",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:blue")
                elif bool(re.search(r"antenna",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:goldenrod")
                elif bool(re.search(r"comms",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:goldenrod")
                elif bool(re.search(r"Control",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:grape")
                elif bool(re.search(r"Coupling",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:kelly green")
                elif bool(re.search(r"Engine",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:ocean blue")
                elif bool(re.search(r"Equipment",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:puke green")
                elif bool(re.search(r"Landing",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:light violet")
                elif bool(re.search(r"Lights",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:robin's egg blue")
                elif bool(re.search(r"Mining",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:puce")
                elif bool(re.search(r"Parachute",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:neon green")
                elif bool(re.search(r"Power",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:canary yellow")
                elif bool(re.search(r"Probe",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:light navy")
                elif bool(re.search(r"Science",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:bright pink")
                elif bool(re.search(r"Sensor",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:bright pink")
                elif bool(re.search(r"Storage",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:rust")
                elif bool(re.search(r"Structure",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:grey")
                elif bool(re.search(r"Tank",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:periwinkle")
                elif bool(re.search(r"Thermal",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:dark red")
                else:
                    tempList.append('xkcd:cloudy blue')
                try:dfOut.iloc[onRow,onCol] = partsDict[dfOut.iloc[onRow,onCol]]['name']
                except:dfOut.iloc[onRow,onCol]=dfOut.iloc[onRow,onCol]
                onCol+=1
            onCol=0
            onRow+=1
            colorList.append(tempList)
        a.render_mpl_table_colors_pdf(export_pdf, dfOut[:-1],Colors=colorList, header_columns=0, col_width=10)
    plt.close('all')
    await ctx.author.send(file=discord.File(r'Tables.pdf'))

#/researched upgrades all
@ui.slash.subcommand(base_names='researched', name='upgrades', description="All unlocked upgrades", guild_ids=[225345178955808768], guild_permissions={225345178955808768: SlashPermission(allowed={"225345178955808768": SlashPermission.ROLE},forbidden={"684936661745795088":SlashPermission.ROLE,"676250179929636886":SlashPermission.ROLE})})
async def command(ctx):
    data2 = sfs.parse_savefile('persistent.sfs')
    tech = data2['GAME']['SCENARIO'][2]['UPGRADES']['Unlocks']
    await ctx.respond(str(list(tech.keys()))[1:-1].replace("'", ''),hidden=True)

#researched nodes all
@ui.slash.subcommand(base_names='researched', name='nodes', description="All researched nodes", guild_ids=[225345178955808768], guild_permissions={225345178955808768: SlashPermission(allowed={"225345178955808768": SlashPermission.ROLE},forbidden={"684936661745795088":SlashPermission.ROLE,"676250179929636886":SlashPermission.ROLE})})
async def command(ctx):
    data2 = sfs.parse_savefile('persistent.sfs')
    tech = data2['GAME']['SCENARIO'][6]['Tech']
    length = len(tech)
    i = 0
    techdict = {}
    print(tech[i])
    while i < length:
        techdict.update({tech[i]['id']:tech[i]['part']})
        i += 1
    strlist = str(techdict.keys())[11:-2]
    strlist = strlist.replace("'", '')
    print(strlist)
    await ctx.respond(strlist,hidden=True)

@ui.slash.command(name='Time', description="Displays Charlie's Current time and timezone.", guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(allowed={
            "225345178955808768": SlashPermission.ROLE
        },forbidden={
            "684936661745795088":SlashPermission.ROLE,
            "676250179929636886":SlashPermission.ROLE})})
async def command(ctx):
    os.environ['TZ'] = 'US/Eastern'
    time.tzset()
    await ctx.send("Charlie's time is: " + time.strftime('%X %x %Z'))

@ui.slash.user_command(guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(
        allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE
        },
        forbidden={
            "225345178955808768": SlashPermission.ROLE
        }
    )
    })
async def Coins(ctx, user):
    isAllowed = False
    for role in [338173415527677954,253752685357039617,225413350874546176]:
        if discord.utils.get(ctx.guild.roles, id=int(role)) in ctx.author.roles:
            isAllowed = True
        else:
            isAllowed
    if isAllowed:
        df = pd.read_csv(UserListURL, index_col=0)
        funds = df.loc[int(user.id), 'Coin Amount']
        embeddict = {'color': 6345206, 'type': 'rich', 'description': '<@!'+ str(user.id) + '> has ' + str(funds) + '<:HotTips2:465535606739697664>'}
        await ctx.author.send(embed=discord.Embed.from_dict(embeddict))

@ui.slash.command(name="toggleChannel", description="Locks Channel the command is run in, if another channel isn't specified.", options=[
    SlashOption(str, name="Reason", description="Reason for locking/unlocking channel", required=True), SlashOption(str, name="Direction", description="Tell the bot wether to lock or unlock a channel", choices=[create_choice('lock', 'lock'),create_choice('unlock','unlock')], required=True), SlashOption(str, name="Channel", description="Channel to lock, optional. Exclude if channel to lock is current channel., input as reference", required=False)
    ],guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(
        allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE
        },
        forbidden={
            "225345178955808768": SlashPermission.ROLE
        }
    )
    })
async def command(ctx, reason, direction, channel="ctx"):
    print(channel)
    if channel == "ctx":
        channelPublish = client.get_channel(ctx.channel.id)
    else:
        channelPublish = client.get_channel(int(channel[2:-1]))
    print(channelPublish)
    if direction == "lock":
        perms = channelPublish.overwrites_for(ctx.guild.default_role)
        perms.send_messages=False
        await channelPublish.set_permissions(ctx.guild.default_role, overwrite=perms)
        await channelPublish.send("Channel locked because: " + reason)
    elif direction == "unlock":
        perms = channelPublish.overwrites_for(ctx.guild.default_role)
        perms.send_messages=True
        await channelPublish.set_permissions(ctx.guild.default_role, overwrite=perms)
        await channelPublish.send("Channel unlocked because: " + reason)

@ui.slash.command(name="Help", description="Gives you help for Bluesy's custom commands", guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(

        allowed={
            "225345178955808768": SlashPermission.ROLE
        },
        forbidden={
            "684936661745795088":SlashPermission.ROLE,
            "676250179929636886":SlashPermission.ROLE
        }
    )
    })
async def command(ctx):
    message = ["```","buyShares <Coins/Funds> <Symbol> <Amount>","changeRPO <RPO_TAG>","joinRPO <RPO_TAG>","sellShares <Symbol> <Amount>","```"]
    output_text = '\n'.join(line for line in message)
    await ctx.respond(output_text,hidden=True)

@ui.slash.command(name="RPOKnowledge", description="DMs you the knoweldge your RPO has.", guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(

        allowed={
            "225345178955808768": SlashPermission.ROLE
        },
        forbidden={
            "684936661745795088":SlashPermission.ROLE,
            "676250179929636886":SlashPermission.ROLE
        }
    )
    })
async def command(ctx):
    refreshToken()
    author = ctx.author
    userid = author.id
    if str(userid) not in pd.read_csv(UserListURL)['userID'].astype(str).to_list():
        await ctx.author.send("<:KSplodes:896043440872235028> Error: Not registered in an RPO for the bot. Please register with the bot through !joinRPO <RPO_Tag>")
        return
    elif pd.read_csv(UserListURL, index_col=0).loc[userid,'RPO'] == 'A':
        await ctx.author.send("<:KSplodes:896043440872235028> Error: Invalid RPO for knowledge processing. Please change your RPO !changeRPO <New_RPO_Tag>")
        return
    elif str(userid) in pd.read_csv(UserListURL)['userID'].astype(str).to_list():
        RPO = pd.read_csv(UserListURL, index_col=0).loc[userid,'RPO']
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
        a.render_mpl_table(dfOut, header_columns=0, col_width=5.0)
        await ctx.author.send(file=discord.File('table.png'))
    return

@ui.slash.subcommand(base_names=['coins','query'], name='me', description="Querys how many coins you have", guild_ids=[225345178955808768], guild_permissions={225345178955808768: SlashPermission(allowed={"225345178955808768": SlashPermission.ROLE},forbidden={"684936661745795088":SlashPermission.ROLE,"676250179929636886":SlashPermission.ROLE})})
async def command(ctx):
    refreshToken()
    if str(ctx.author.id) not in pd.read_csv(UserListURL)['userID'].astype(str).to_list(): #makes sure user isn't already in an RPO
        a.undeclared(ctx)
    df = pd.read_csv(UserListURL, index_col=0)
    funds = df.loc[ctx.author.id, 'Coin Amount']
    embeddict = {'color': 6345206, 'type': 'rich', 'description': '<@!'+ str(ctx.author.id) + '> has ' + str(funds) + '<:HotTips2:465535606739697664>'}
    await ctx.respond(embed=discord.Embed.from_dict(embeddict),hidden=True)

@ui.slash.subcommand(base_names=['coins','query'], name='mod', description="Querys how many coins someone else has", options=[SlashOption(str, name="user", description='user to query', required=True)], guild_ids=[225345178955808768],guild_permissions={
    225345178955808768: SlashPermission(
        allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE
        },
        forbidden={
            "225345178955808768": SlashPermission.ROLE}
    )})
async def command(ctx, user):
    refreshToken()
    isAllowed = False
    if a.role_check(ctx, [338173415527677954,253752685357039617,225413350874546176])!=True:
        return
    df = pd.read_csv(UserListURL, index_col=0)
    funds = df.loc[int(user[3:-1]), 'Coin Amount']
    embeddict = {'color': 6345206, 'type': 'rich', 'description': '<@!'+ str(user[3:-1]) + '> has ' + str(funds) + '<:HotTips2:465535606739697664>'}
    await ctx.respond(embed=discord.Embed.from_dict(embeddict),hidden=True)

@ui.slash.subcommand(base_names=['coins','edit'], name='add', description="Adds coins to someone", options=[SlashOption(str, name="user", description='user to query', required=True), SlashOption(int,name='amount',description='amount to add',required=True )], guild_ids=[225345178955808768],guild_permissions={
    225345178955808768: SlashPermission(
        allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE
        },
        forbidden={
            "225345178955808768": SlashPermission.ROLE}
    )})
async def command(ctx, user, amount):
    refreshToken()
    if a.role_check(ctx, [338173415527677954,253752685357039617,225413350874546176])!=True:
        return
    if amount == 0:
        embeddict = {'color': 6345206, 'type': 'rich', 'description': '<:KSplodes:896043440872235028> Error: Cannot Add 0 funds.'}
        await ctx.send(embed=discord.Embed.from_dict(embeddict))
    df = pd.read_csv(UserListURL)
    df['userID'] = df['userID'].astype(str)
    df['new'] = df['userID']
    df = df.set_index('new');
    df.loc[str(user[3:-1]), 'Coin Amount'] += abs(amount)
    embeddict = {'color': 6345206, 'type': 'rich', 'description': '✅' + str(abs(amount)) +'<:HotTips2:465535606739697664> has been given to <@!' + str(user[3:-1]) + '>'}
    await ctx.send(embed=discord.Embed.from_dict(embeddict))
    gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
    sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
    worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
    # APPEND DATA TO SHEET
    #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
    set_with_dataframe(worksheet, df) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET

@ui.slash.subcommand(base_names=['coins','edit'], name='remove', description="Removes coins from someone", options=[SlashOption(str, name="user", description='user to query', required=True), SlashOption(int,name='amount',description='amount to remove',required=True)], guild_ids=[225345178955808768],guild_permissions={
    225345178955808768: SlashPermission(
        allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE
        },
        forbidden={
            "225345178955808768": SlashPermission.ROLE}
    )})
async def command(ctx, user, amount):
    refreshToken()
    isAllowed = False
    if a.role_check(ctx, [338173415527677954,253752685357039617,225413350874546176])!=True:
        return
    if amount == 0:
        embeddict = {'color': 6345206, 'type': 'rich', 'description': '<:KSplodes:896043440872235028> Error: Cannot Remove 0 funds.'}
        await ctx.send(embed=discord.Embed.from_dict(embeddict))
    df = pd.read_csv(UserListURL)
    df['userID'] = df['userID'].astype(str)
    df['new'] = df['userID']
    df = df.set_index('new')
    charged = min(df.loc[str(user[3:-1]), 'Coin Amount'], abs(amount))
    df.loc[str(user[3:-1]), 'Coin Amount'] -= min(df.loc[str(user[3:-1]), 'Coin Amount'], abs(amount))
    embeddict = {'color': 6345206, 'type': 'rich', 'description': '✅' + str(charged) +'<:HotTips2:465535606739697664> has been removed from <@!' + str(user[3:-1]) + '>'}
    await ctx.send(embed=discord.Embed.from_dict(embeddict))
    gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
    sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
    worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
    # APPEND DATA TO SHEET
    #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
    set_with_dataframe(worksheet, df) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET

@ui.slash.subcommand(base_names='wallet', name='remove', description="Removes funds from an RPO", options=[SlashOption(str, name="user", description='user to query', required=True), SlashOption(int,name='amount',description='amount to remove',required=True)], guild_ids=[225345178955808768],guild_permissions={
    225345178955808768: SlashPermission(
        allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE
        },
        forbidden={
            "225345178955808768": SlashPermission.ROLE}
    )})
async def command(ctx, user,amount):
    accountBalanceSheet = pd.read_csv(RPOInfoURL)
    accountBalanceSheet['new'] = accountBalanceSheet['TAG']
    accountBalanceSheet = accountBalanceSheet.set_index('new')
    accountBalanceSheet['Account Balance'] = accountBalanceSheet['Account Balance'].astype(str).apply(lambda x: x.replace('$', '').replace(',', '')).astype(float)
    wealth = float(accountBalanceSheet.loc[pd.read_csv(UserListURL, index_col=0).loc[int(user[3:-1]), 'RPO'], 'Account Balance'])
    charged = min(wealth, abs(amount))
    accountBalanceSheet.loc[pd.read_csv(UserListURL, index_col=0).loc[int(user[3:-1]), 'RPO'], 'Account Balance'] -= min(wealth, abs(amount))
    embeddict = {'color': 6345206, 'type': 'rich', 'description': '✅' + str(charged) +' 🪙 has been removed from ' + str(pd.read_csv(UserListURL, index_col=0).loc[int(user[3:-1]), 'RPO'])}
    await ctx.send(embed=discord.Embed.from_dict(embeddict))
    gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
    sh = gc.open_by_key(data['RPOinfoID'])
    worksheet = sh.get_worksheet(0)
    set_with_dataframe(worksheet, accountBalanceSheet)

@ui.slash.subcommand(base_names='wallet', name='add', description="Add funds to an RPO", options=[SlashOption(str, name="user", description='user to query', required=True), SlashOption(int,name='amount',description='amount to add',required=True)], guild_ids=[225345178955808768],guild_permissions={
    225345178955808768: SlashPermission(
        allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE
        },
        forbidden={
            "225345178955808768": SlashPermission.ROLE}
    )})
async def command(ctx, user,amount):
    accountBalanceSheet = pd.read_csv(RPOInfoURL)
    accountBalanceSheet['new'] = accountBalanceSheet['TAG']
    accountBalanceSheet = accountBalanceSheet.set_index('new')
    accountBalanceSheet['Account Balance'] = accountBalanceSheet['Account Balance'].astype(str).apply(lambda x: x.replace('$', '').replace(',', '')).astype(float)
    accountBalanceSheet.loc[pd.read_csv(UserListURL, index_col=0).loc[int(user[3:-1]), 'RPO'], 'Account Balance'] += abs(amount)
    embeddict = {'color': 6345206, 'type': 'rich', 'description': '✅' + str(amount) +' 🪙 has been added to ' + str(pd.read_csv(UserListURL, index_col=0).loc[int(user[3:-1]), 'RPO'])}
    await ctx.send(embed=discord.Embed.from_dict(embeddict))
    gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
    sh = gc.open_by_key(data['RPOinfoID'])
    worksheet = sh.get_worksheet(0)
    set_with_dataframe(worksheet, accountBalanceSheet)

@ui.slash.subcommand(base_names='transfer', name='wallet', description="Transfers ALL coins to RPO's funds. Irreversible.", options=[
    SlashOption(int, name="Amount",required=True)
    ], guild_ids=[225345178955808768], guild_permissions={225345178955808768: SlashPermission(allowed={"225345178955808768": SlashPermission.ROLE},forbidden={"684936661745795088":SlashPermission.ROLE,"676250179929636886":SlashPermission.ROLE})})
async def command(ctx,amount):
    refreshToken()
    if pd.read_csv(UserListURL, index_col=0).loc[ctx.author.id,'RPO'] == 'A': await ctx.respond("You are not registered in a valid RPO to the bot",hidden=True)
    df = pd.read_csv(UserListURL)
    df['userID'] = df['userID'].astype(str)
    df['new'] = df['userID']
    df = df.set_index('new')
    charged = min(df.loc[str(ctx.author.id), 'Coin Amount'],amount)
    df.loc[str(ctx.author.id), 'Coin Amount'] -= charged
    gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
    sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
    worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
    # APPEND DATA TO SHEET
    #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
    set_with_dataframe(worksheet, df) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
    accountBalanceSheet = pd.read_csv(RPOInfoURL)
    accountBalanceSheet['new'] = accountBalanceSheet['TAG']
    accountBalanceSheet = accountBalanceSheet.set_index('new')
    accountBalanceSheet['Account Balance'] = accountBalanceSheet['Account Balance'].astype(str).apply(lambda x: x.replace('$', '').replace(',', '')).astype(float)
    accountBalanceSheet.loc[pd.read_csv(UserListURL, index_col=0).loc[int(ctx.author.id), 'RPO'], 'Account Balance'] += abs(charged)
    embeddict = {'color': 6345206, 'type': 'rich', 'description': '✅' + str(charged) +'<:HotTips2:465535606739697664> has been removed from <@!' + str(ctx.author.id) + '>, and added to your RPO funds.'}
    await ctx.respond(embed=discord.Embed.from_dict(embeddict),hidden=True)
    gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
    sh = gc.open_by_key(data['RPOinfoID'])
    worksheet = sh.get_worksheet(0)
    set_with_dataframe(worksheet, accountBalanceSheet)

@ui.slash.command(name="updatePortfolios", description="Updates Portfolios", guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(
        allowed={
            "363095569515806722": SlashPermission.USER,
            "225344348903047168": SlashPermission.USER
        },
        forbidden={
            "225345178955808768": SlashPermission.ROLE}
    )})
async def command(message):
    refreshToken()
    if message.author.id not in [225344348903047168, 363095569515806722]:
        return
    else:
        await message.send("Starting")
        investChannel = client.get_channel(900523609603313704)
        perms = investChannel.overwrites_for(message.guild.default_role)
        perms.send_messages=False
        await investChannel.send("**MARKET UPDATING. INVESTMENTS LOCKED UNTIL COMPLETE**")
        await investChannel.set_permissions(message.guild.default_role, overwrite=perms)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=data['Master_SPREADSHEET_ID'],
            range=data['Master_RANGE_NAME']).execute()
        values = result.get('values', [])
        #Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
        Investmentsdf = pd.read_csv(InvestorsURL, index_col=0).dropna(axis=1, how='all') #Creates the data frame for investors
        RPOlist = list() #initializes empty list for list of RPOs with investments
        spreadoutsdf = pd.read_csv(SSaccessURL, index_col=0)
        spreadoutsdf2 = pd.read_csv(SSaccessURL)
        for row in values:
            RPOlist.append(row[0]) #Adds all RPOs with investments to a list
        #print(RPOlist)
        for i in RPOlist:
            a.Portfolio(i,service)
            await asyncio.sleep(1)
        await investChannel.send("**MARKET UPDATED. INVESTMENTS UNLOCKED.**")
        perms.send_messages=True
        await investChannel.set_permissions(message.guild.default_role, overwrite=perms)
        await message.channel.send("Portfolio's updated!")

@ui.slash.command(name="roll", description="rolls dice", options=[
    SlashOption(str, name="dice", description="Dice to roll, accepts d2s, d4s, d6s, d8s, d10s, d12s, d20s, and d100s.", required=True)
    ],guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(
        allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE
        },
        forbidden={
            "225345178955808768": SlashPermission.ROLE
        }
    )
    })
async def roll(ctx, dice):
    arg = dice
    if "+" in arg:
        dice = arg.split("+")
    #elif arg == 'patent':
    #    dice = ['','','']
    else:
        dice = [str(arg)]
    try:
        sum = 0
        rolls = list()
        allowedDice = [2,4,6,8,10,12,20,100]
        for die in dice:
            if 'd' in die:
                if int(die[die.find('d')+1:]) not in allowedDice:
                    await ctx.send("<:KSplodes:896043440872235028> Error invalid argument: specified dice can only be d2s, d4s, d6s, d8s, d10s, d12s, d20s, or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
                    return
                try:
                    numRolls = int(die[:die.find('d')])
                except:
                    numRolls = 1
                i = 1
                roll = 0
                while i <= numRolls:
                    roll += random.randint(1, int(die[die.find('d')+1:]))
                    i += 1
                sum += roll
                rolls.append(roll)
            else:
                try:
                    rolls.append(int(die))
                    sum += int(die)
                except:
                    await ctx.send("<:KSplodes:896043440872235028> Error invalid argument: specified dice can only be d2s, d4s, d6s, d8s, d10s, d12s, d20s,  or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
                    return
        output = '`'
        for x in rolls:
            output += str(x) + ', '
        output = output[:-2]
        await ctx.send("<@!"+str(ctx.author.id)+">: Rolled `" +arg+"` got "+output+"` for a total value of: "+str(sum))        
    except:
        await ctx.send("<:KSplodes:896043440872235028> Error invalid argument: specified dice can only be d2s, d4s, d6s, d8s, d10s, d12s, d20s,  or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
        return

@ui.slash.subcommand(base_names="Publish", name="post", description="Press Releases and Stuff", options=[
        SlashOption(str, name="Title", description="This is the title of the embed", required=True), SlashOption(str, name="Body", description="This is the body of the command", required=True), SlashOption(int, name="Color", description="Embed color", choices=[
                {"name": "Breaking News", "value": 16705372}, {"name": "Financial", "value": 5763719},{"name": "Patents/Info Sector Updates", "value": 5793266}, {"name": "Other", "value": 12370112}], required=True), SlashOption(str, name="Time", description="This is the publishing time info (Must include Published at: if you want that to show up.)", required=True),SlashOption(str, name='channel', description='channel to post embed to', choices=[create_choice('news', '902335372321755196'), create_choice('Bot-Dev', '687817008355737606')], required=True) ,SlashOption(str, name="Author", description="Article Author, default Author Kerman"), SlashOption(str, name="Image", description="URL of image to use as logo.")], guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(
        allowed={
            "363095569515806722": SlashPermission.USER,
            "225344348903047168": SlashPermission.USER,
            "146285543146127361": SlashPermission.USER
        },
        forbidden={
            "225345178955808768": SlashPermission.ROLE}
    )})
async def command(ctx, title, body, color, time, channel, author="Author Kerman", image="https://cdn.discordapp.com/attachments/687817008355737606/902619514808729682/KNN-blue.png"):
    publishTo = client.get_channel(int(channel))
    morePars = True
    body1 = body
    addImage = False
    while morePars:
        btn = await (
                await ctx.send("Do you want to add another paragraph?", components=[
                    Button("another", "Yes", color=ButtonStyles.green), Button("done", "No", color=ButtonStyles.red)
                ])
            ).wait_for("button", client)
        if btn.author.id != ctx.author.id:
            await ctx.send("Error: wrong user. User <@!" +str(ctx.author.id)+"> expected. Cancelling operation.")
            return
        elif btn.author.id == ctx.author.id:
            if btn.label == "No":
                morePars = False
                btn = await (
                        await ctx.send("Done adding paragraphs. Add an image?", components=[
                            Button("Yes", "Yes", color=ButtonStyles.green), Button("No", "No", color=ButtonStyles.red)
                        ])
                    ).wait_for("button", client)
                if btn.label == 'No':
                    await ctx.send("No photo.")
                elif btn.label == "Yes":
                    await ctx.send("Please upload the photo:")
                    msg = await client.wait_for("message", check=a.author_check(ctx.author), timeout=180)
                    addedImage = msg.attachments[0].url
                    addImage = True
            elif btn.label == "Yes":
                await ctx.send("Please enter your next paragraph:")
                msg = await client.wait_for("message", check=a.author_check(ctx.author), timeout=180)
                add = " \n \n "+(str(msg.content))
                if (len(body1+add)>4096):
                    await ctx.send("Error, too long. ignoring last entry.")
                    break
                body1 += add
                msg = await ctx.send("Paragraph added.")
                if len(body1) >=3900:
                    await msg.edit("Max length Reached")
                    break
    embed=discord.Embed(title=title, description=body1, color=color)
    embed.set_author(name=author)
    embed.set_thumbnail(url=image)
    if addImage:
        embed.set_image(url=addedImage)
    embed.set_footer(text=time)
    while True:
        btn = await (
                    await ctx.send(content = "is this good?", embed=embed, components=[
                        Button("Yes", "Yes", color=ButtonStyles.green), Button("No", "No", color=ButtonStyles.red)
                    ])
                ).wait_for("button", client)
        if btn.label == "Yes":
            await publishTo.send(embed=embed)
            break
        elif btn.label == "No":
            btn = await (
                await ctx.send(content = "What to change?", components=[
                    Button("Title", "Title", color=ButtonStyles.blurple), Button("Body", "Body", color=ButtonStyles.blurple), Button("Footer", "Footer", color=ButtonStyles.blurple), Button("Author", "Author", color=ButtonStyles.blurple)
                ])
            ).wait_for("button", client)
        if btn.label == "Title":
            await ctx.send("Please enter the new Title:")
            msg = await client.wait_for("message", check=a.author_check(ctx.author), timeout=180)
            title = msg.content
            embed=discord.Embed(title=title, description=body1, color=color)
            embed.set_author(name=author)
            embed.set_thumbnail(url=image)
            if addImage:
                embed.set_image(url=addedImage)
            embed.set_footer(text=time)
        elif btn.label == "Body":
            await ctx.send("Re-adding paragraphs")
            body1 = str()
            while True:
                btn = await (
                    await ctx.send("Do you want to add another paragraph?", components=[
                        Button("another", "Yes", color=ButtonStyles.green), Button("done", "No", color=ButtonStyles.red)
                    ])
                ).wait_for("button", client)
                if btn.author.id != ctx.author.id:
                    await ctx.send("Error: wrong user. User <@!" +str(ctx.author.id)+"> expected. Cancelling operation.")
                    return
                elif btn.author.id == ctx.author.id:
                    if btn.label == "No":
                        await ctx.send("Done adding paragraphs")
                        break
                    elif btn.label == "Yes":
                        await ctx.send("Please enter your next paragraph:")
                        msg = await client.wait_for("message", check=a.author_check(ctx.author), timeout=180)
                        add = " \n \n "+(str(msg.content))
                        if (len(body1+add)>4096):
                            await ctx.send("Error, too long. ignoring last entry.")
                            break
                        body1 += add
                        msg = await msg.channel.send("Paragraph added.")
                        if len(body1) >=4000:
                            await msg.edit("Max length Reached")
                            break
            embed=discord.Embed(title=title, description=body1, color=color)
            embed.set_author(name=author)
            embed.set_thumbnail(url=image)
            if addImage:
                embed.set_image(url=addedImage)
            embed.set_footer(text=time)
        elif btn.label == "Footer":
            await ctx.send("Please enter new footer:")
            msg = await client.wait_for("message", check=a.author_check(ctx.author), timeout=180)
            time = msg.content
            embed.set_footer(text=time)
        elif btn.label == "Author":
            await ctx.send("Please enter new author:")
            msg = await client.wait_for("message", check=a.author_check(ctx.author), timeout=180)
            author = msg.content
            embed.set_author(name=author)
    await ctx.send("Complete.")

@ui.slash.command(name='contract', description='Submits a contract request to the CP. Max 2 open contracts per RPO.', options=[
    SlashOption(str, name='Kerbals', description="Does your mission require kerbals? If so, yours, Charlie's, or a 3rd party?", choices=[
        create_choice("No", "No Kerbals"), create_choice("Yes, Mine", "Own Kerbals"), create_choice("Yes, CP's", "CP's Kerbals"), create_choice("Yes, Other", "Other RPO's Kerbals")], required=True),
    SlashOption(str, name="Comms", description="Do you need comms for this mission? If so do you need Charlie's, or do you have an arrangement?", choices=[create_choice('No', 'No comms needed'), create_choice("Yes, Charlie's", "Need Charlie's Network"), create_choice("Yes, Other", "Has Comms arrangement")], required=True),
    SlashOption(str, name="Goal", description="What is the end goal of your mission?", required=True),
    SlashOption(str, name='Wants', description="What are you hoping to learn and/or gain from this mission?", required=True),
    SlashOption(str, name="RP", description="Is there anything that you want done purely in RP?", required=True),
    SlashOption(str, name="Patent", description="Are you hoping to get a patent from this? If yes, you will get a prompt on what you want to patent.", choices=[
        create_choice("No", "No"), create_choice("Yes", 'Yes')], required=True),
    SlashOption(str, name="Craft", description="Are you submitting a craft? If yes, you will be prompted to upload one, and it will not be edited.", choices=[
        create_choice("No", "No"), create_choice("Yes", "Yes")], required=True),
    SlashOption(str, name="Payment", description="Where to charge from first after YT, discord coins (Coins) or RPO wallet (Funds)?", choices=[
        create_choice("Coins", "Coins"), create_choice("Funds", "Funds")], required=True),
    SlashOption(str, name="Participants", description="Other RPOs or Joint Ventures Involved", required=True),
    SlashOption(str, name="Location", description="What Celestial body is the mission aimed at? (If both surface and space, choose surface)", choices=[
        create_choice("Kerbin Surface", "Kerbin Surface"),create_choice("Mun Surface", 'Mun Surface'),create_choice("Minmus Surface", "Minmus Surface"), create_choice("Kerbin Space", "Kerbin Space"),create_choice("Mun Space", 'Mun Space'),create_choice("Minmus Space", "Minmus Space"), create_choice("Kerbol", "Kerbol")], required=True)],
    guild_ids=[225345178955808768], guild_permissions={225345178955808768: SlashPermission(allowed={"225345178955808768": SlashPermission.ROLE},forbidden={"684936661745795088":SlashPermission.ROLE,"676250179929636886":SlashPermission.ROLE})})
async def command(ctx, kerbals, comms, goal, wants, rp, patent, craft, payment,  participants, location):
    try:
        RPO = pd.read_csv(UserListURL, index_col=0).loc[ctx.author.id,'RPO']
    except:
        await ctx.author.send("Error: You are not registered in an RPO.")
        return
    contractDF = pd.read_csv('https://docs.google.com/spreadsheets/d/1MyTqsdG3uzOYt_sNzc1aKiLXMfATl4pBJg5lf-4hSQw/gviz/tq?tqx=out:csv&gid=918856176',)
    contractTotal = 0
    for i in contractDF["RPO"]:
        if i == RPO:
            contractTotal+=1
    if contractTotal>1:
        await ctx.author.send("Error: Your RPO already has the maximum number of open contracts.")
        return
    if patent == "Yes":
        await ctx.author.send("What do you want to patent?")
        patent = "Wants Patent"
        msg = await client.wait_for("message", check=a.message_check(channel=ctx.author.dm_channel), timeout=180)
        try:
            patentWant = msg.content
        except:
            patentWant = ""
    else:
        patent = "No Patent"
        patentWant = "None"
    if craft == "Yes":
        await ctx.author.send("Upload your craft file.")
        craft = "Submitted Craft"
        msg = await client.wait_for("message", check=a.message_check(channel=ctx.author.dm_channel), timeout=180)
        try:
            submittedCraft = msg.attachments[0].url
        except:
            submittedCraft = ""
    else:
        craft = "No craft submitted"
        submittedCraft = ""
    spreadsheet_id = '1MyTqsdG3uzOYt_sNzc1aKiLXMfATl4pBJg5lf-4hSQw'
    range_ = 'BotContracts!A2:O'
    value_input_option = 'USER_ENTERED'
    insert_data_option = 'INSERT_ROWS'

    await ctx.author.send("Contract Submission by: "+str(ctx.author)+" for RPO: "+str(RPO)+", "+str(patent)+" : "+str(patentWant)+", "+str(comms)+", Location: "+str(location)+", Payment: "+str(payment)+", Participants: "+str(participants))
    await ctx.author.send("Goals: "+str(goal)+", Wants: "+str(wants))
    if craft == "Submitted Craft":
         await ctx.author.send("Submitted Craft: "+str(submittedCraft))
    else:
        await ctx.author.send("Needs a craft designed")
    btn = await (
        await ctx.author.send("Is that Correct?", components=[
            Button("Yes", "Yes", color=ButtonStyles.green), Button("No", "No", color=ButtonStyles.red)
        ])
    ).wait_for("button", client)
    if btn.label == "Yes":
        btn = await (
            await ctx.author.send("Is this a multi-part mission?", components=[
                Button("Yes", "Yes", color=ButtonStyles.green), Button("No", "No", color=ButtonStyles.red)
            ])
        ).wait_for("button", client)
        if btn.label == "Yes":
            multipart = "Is Multipart"
        else:
            multipart = "Not Multipart"
    else:
        await ctx.author.send("Cancelling contract submission, please restart with correct parameters.")
        return
    value_range_body = {
        "range":range_,
        "majorDimension":"ROWS",
        "values": [[RPO, str(ctx.author), kerbals, comms, goal, wants, rp, patent, patentWant, craft, submittedCraft, payment, participants, location, multipart]]}
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
    response = request.execute()
    await ctx.author.send("Contract Submitted. Please wait for a representative of the Celestial Project to reach out. Have a nice day!")
    logChannel = client.get_channel(906190976320679996)
    await logChannel.send("Contract Submission by: "+str(ctx.author)+", (ID: "+str(ctx.author.id)+") for RPO: "+str(RPO)+", "+str(patent)+" : "+str(patentWant)+", "+str(comms)+", Location: "+str(location)+", Payment: "+str(payment)+", Participants: "+str(participants)+", "+str(multipart))
    await logChannel.send("Goals: "+str(goal)+", Wants: "+str(wants))
    if craft == "Submitted Craft":
         await logChannel.send("Submitted Craft: "+str(submittedCraft))
    else:
        await logChannel.send("Needs a craft designed")

@ui.slash.subcommand(base_names = 'ticket',name='reply', description='Replies to an open modmail ticket', options=[
    SlashOption(str, name="Ticket", description="Ticket to reply to. Should be an int, which will be given in a message header.", required=True),
    SlashOption(str, name='Message', description="Initial message to send", required=True)
    ], guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE},forbidden={
            "225345178955808768": SlashPermission.ROLE})})
async def command(ctx, ticket, message):
    modnames={
        363095569515806722:"[Moderator] Bluesy",247950431630655488:"[Moderator] Doffey",82495450153750528:"[Moderator] Kaitlin",146285543146127361:"[Admin] Jazmine",138380316095021056:"[Moderator] Krios",
        162833689196101632:"[Moderator] Mike Takumi", 137240557280952321:"[Admin] Pet",137240557280952321:"[Moderator] Melethya",225344348903047168:"[Owner] Charlie"
    }
    """menu = await (
    await ctx.send("Attachments?", components=[
        SelectMenu('attachments',options=[
            SelectOption(value='0',label='None',description='No Attachments'),
            SelectOption(value='1',label='One',description='One Attachment'),
            SelectOption(value='2',label='Two',description='Two Attachments'),
            SelectOption(value='3',label='Three',description='Three Attachments'),
            SelectOption(value='4',label='Four',description='Four Attachments'),
            SelectOption(value='5',label='Five',description='Five Attachments'),
            SelectOption(value='6',label='Six',description='Six Attachments'),
            SelectOption(value='7',label='Seven',description='Seven Attachments'),
            SelectOption(value='8',label='Eight',description='Eight Attachments'),
            SelectOption(value='9',label='Nine',description='Nine Attachments'),
            SelectOption(value='10',label='Ten',description='Ten Attachments'),
        ],min_values=1,max_values=1)
    ])
    ).wait_for("select", client)
    n = (int("".join(menu.data['values'])))
    i = 0
    attchmentUrls = list()
    if n >0:
        await menu.respond("Please upload first attachment")
        while i<n:
            msg = await client.wait_for("message", check=a.message_check(channel=ctx.author.dm_channel), timeout=180)
            try:
                attchmentUrls.append(msg.attachments[0].url)
            except: None
            await ctx.send("Upload next attachment.")
            i+=1
    else:attchmentUrls=None"""
    user = a.add_message(ctx,message,str(ticket),None)
    sendTo = await ctx.guild.fetch_member(int(user))
    await sendTo.send("Message from "+str(modnames[ctx.author.id])+": "+message)
    #if n >0: await sendTo.send(", ".join(attchmentUrls))
    await ctx.send("Sent.")

@ui.slash.subcommand(base_names = 'ticket',name='list',description='Displays all open tickets in modmail.', guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE},forbidden={
            "225345178955808768": SlashPermission.ROLE})})
async def command(ctx):
    if ctx.channel.id==906578081496584242:
        with open('tickets.json',"rb") as t:
            temp = fernet.decrypt(t.read())
        tickets = json.loads(temp)
        openTickets = list()
        for ticket in list(tickets.keys()):
            if tickets[ticket]["open"] == "True":
                author = "<@!"+str(tickets[ticket]['starter'])+">"
                appender = str(ticket)+" (Profile: " +author+")"
                openTickets.append(appender)
    tempStr = ", "
    tempOut = tempStr.join(openTickets)
    outString = "Open tickets are tickets numbered: " + tempOut
    await ctx.respond(outString,hidden=True)

@ui.slash.subcommand(base_names = 'ticket',name='history',description='Displays history of a modmail ticket.',options=[
    SlashOption(str,name="Ticket",description="Ticket to recall history of, or all is none is specified",required=False)
    ] , guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE},forbidden={
            "225345178955808768": SlashPermission.ROLE})})
async def command(ctx, ticket=None):
    if ticket is not None:
        pdf = fpdf.FPDF(format='letter')
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        with open('tickets.json',"rb") as t:
            temp = fernet.decrypt(t.read())
        tickets = json.loads(temp)
        for message in list(tickets[ticket]["messages"].keys()):
            pdf.write(5,a.strip_non_ascii(str(tickets[ticket]["messages"][message])))
            pdf.ln()
        pdfName = "ticket "+ticket+".pdf"
        pdf.output(pdfName)
        await ctx.respond(file=discord.File(pdfName),hidden=True)
        os.remove(pdfName)
    elif ticket is None:
        pdf = fpdf.FPDF(format='letter')
        pdf.set_font("Arial", size=12)
        with open('tickets.json',"rb") as t:
            temp = fernet.decrypt(t.read())
        tickets = json.loads(temp)
        for ticket in list(tickets.keys()):
            pdf.add_page()
            pdf.set_font("Arial", size=24)
            pdf.write(10,a.strip_non_ascii(str(ticket)))
            pdf.set_font("Arial", size=12)
            pdf.ln()
            for message in list(tickets[ticket]["messages"].keys()):
                pdf.write(5,a.strip_non_ascii(str(tickets[ticket]["messages"][message])))
                pdf.ln()
        pdf.output("all tickets.pdf")
        await ctx.respond(file=discord.File("all tickets.pdf"),hidden=True)
        os.remove("all tickets.pdf")

@ui.slash.subcommand(base_names = 'ticket',name='close',description='Closes an open modmail ticket.',options=[
    SlashOption(str,name="Ticket",description="Ticket to recall history of",required=True), SlashOption(str, name="Name",description="Name to give ticket for easier referral to later.",required=True)
    ] , guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE},forbidden={
            "225345178955808768": SlashPermission.ROLE})})
async def command(ctx, ticket, name):
    pdf = fpdf.FPDF(format='letter')
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    with open('tickets.json',"rb") as t:
        temp = fernet.decrypt(t.read())
    tickets = json.loads(temp)
    for message in list(tickets[ticket]["messages"].keys()):
        pdf.write(5,a.strip_non_ascii(str(tickets[ticket]["messages"][message])))
        pdf.ln()
    pdfName = "ticket "+re.sub(r':',"",a.strip_non_ascii(ticket))+".pdf"
    pdf.output(pdfName)
    tickets[ticket]["open"]="False"
    tickets[name] = tickets.pop(ticket)
    with open('tickets.json','wb') as t:
        t.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))
    await ctx.respond(content="Ticket Closed.",file=discord.File(pdfName))
    os.remove(pdfName) 

@ui.slash.subcommand(base_names = 'ticket',name='open',description="open a ticket forcefully with a user", options=[
    SlashOption(str, name="ID",description="User ID to open ticket with",required=True),SlashOption(str, name="message",description="message to send",required=True),
    SlashOption(str, name="title", description="Optional. use to set the ticket name to be non default.", required=False)], guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE},forbidden={
            "225345178955808768": SlashPermission.ROLE})})
async def command(ctx, id, message, title=None):
    with open('tickets.json',"rb") as t:
        temp = fernet.decrypt(t.read())
    tickets = json.loads(temp)
    newTicketNum = len(list(tickets.keys()))
    newTicket = {
            "open":"True","time":0,"starter":int(id), "messages":{
                "0":str(ctx.author)+": "+str(message)
            }
        }
    sendTo = await ctx.guild.fetch_member(int(id))
    if title is None:
        tickets.update({str(newTicketNum):newTicket})
    else:
        tickets.update({str(title):newTicket})
    with open('tickets.json','wb') as t:
        t.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))
    modnames={
        363095569515806722:"[Moderator] Bluesy",247950431630655488:"[Moderator] Doffey",82495450153750528:"[Moderator] Kaitlin",146285543146127361:"[Admin] Jazmine",162833689196101632:"[Moderator] Krios",
        162833689196101632:"[Moderator] Mike Takumi", 137240557280952321:"[Admin] Pet",137240557280952321:"[Moderator] Melethya",225344348903047168:"[Owner] Charlie"
    }
    await sendTo.send("Message from "+str(modnames[ctx.author.id])+": "+message)
    await ctx.respond("Sent.")

@ui.slash.command(name = 'comments',description="updates comment points totals from specified video", options=[
    SlashOption(str, name="ID",description="video ID to grab comments of",required=True)], guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE},forbidden={
            "225345178955808768": SlashPermission.ROLE})})
async def command(ctx, id):
    spreadsheet_id = '1MyTqsdG3uzOYt_sNzc1aKiLXMfATl4pBJg5lf-4hSQw'
    range_ = 'YT Comment Records!A2:B'
    value_render_option = 'FORMATTED_VALUE'
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_,majorDimension="COLUMNS", valueRenderOption=value_render_option)
    response = request.execute()
    df = pd.DataFrame()
    df['Name']=response['values'][0]
    df['Points']=response['values'][1]
    df['Points'] = df['Points'].astype(float)
    df['new'] = df['Name']
    df = df.set_index('new')
    commenters = grabber.comments(id)
    for commenter in commenters:
        if commenter in df['Name'].tolist():
            df.loc[commenter, 'Points']+=1
        else:
            df.loc[-1] = [commenter, 1]
    os.environ['TZ'] = 'US/Eastern'
    time.tzset()
    batch_update_values_request_body = {
        'value_input_option':'USER_ENTERED',
        'data':[
            {"range":range_,
            "majorDimension":"COLUMNS",
            "values": [df['Name'].tolist(),df['Points'].tolist()]},
            {"range":'YT Comment Records!E1',
            "majorDimension":"COLUMNS",
            "values": [[time.strftime('%X %x %Z')]]}]}
    request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body=batch_update_values_request_body)
    response = request.execute()
    await ctx.respond("Done")

@ui.slash.command(name="WODroll", description="Rolls a special set of d10s for determining bellcurve rolls.", options=[
    SlashOption(str, name="name", description="name for roll", required=True),
    SlashOption(int, name="Amount", description="How many dice to roll, min 3", required=True),
    SlashOption(str, name="Success", description="Minimum value to get a success", choices=[
        create_choice('5','5'), create_choice('6','6'), create_choice('7','7'), create_choice('8','8'), create_choice('9','9'),create_choice('10','10')
    ],required=True),
    SlashOption(str, name="Failure", description="Maximum value to count as a failure", choices=[
        create_choice('1','1'), create_choice('2','2'), create_choice('3','3'), create_choice('4','4')
    ],required=True),
    SlashOption(str, name="tag", description="Tag of RPO roll is for", required=True)], guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(
        allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE
        },
        forbidden={
            "225345178955808768": SlashPermission.ROLE}
    )})
async def command(ctx, name, amount, success, failure, tag):
    if amount <= 3:
        ctx.send("<:KSplodes:896043440872235028>: Minimum amount of dice to roll is 3.")
    i=0
    successes=0
    failures=0
    rolls = list()
    while i<amount:
        roll = random.randint(1,10)
        if roll <= int(failure):
            failures+=1
        elif roll >= int(success):
            successes+=1
        rolls.append(roll)
        i+=1
    numTens = 0
    for i in rolls:
        if i==10:
            numTens+=1
    CritSuccesses = (numTens-(numTens%2))
    netSuccesses = successes-failures+CritSuccesses
    output = '`'
    for x in rolls:
        output += str(x) + ', '
    output = output[:-2]
    output+='`'
    embed = None
    if netSuccesses>0:
        embed=discord.Embed(title=name+" Roll", description="**"+str(tag).upper()+"** rolled "+str(amount)+"d10s, getting "+output+", totaling `"+str(successes)+"` successes, `"+str(CritSuccesses)+"` crit successes and `"+ str(failures) +"` failures, for a net of **`"+str(netSuccesses)+"`** successes.", color=0x00ff00)
    elif netSuccesses<0:
        embed=discord.Embed(title=name+" Roll", description="**"+str(tag).upper()+"** rolled "+str(amount)+"d10s, getting "+output+", totaling `"+str(successes)+"` successes, `"+str(CritSuccesses)+"` crit successes and `"+ str(failures) +"` failures, for a net of **`"+str(netSuccesses)+"`** successes.", color=0xff0000)
    elif netSuccesses==0:
        embed=discord.Embed(title=name+" Roll", description="**"+str(tag).upper()+"** rolled "+str(amount)+"d10s, getting "+output+", totaling `"+str(successes)+"` successes, `"+str(CritSuccesses)+"` crit successes and `"+ str(failures) +"` failures, for a net of **`"+str(netSuccesses)+"`** successes.", color=0x0000ff)
    else:
        return
    await ctx.send(embed=embed)

@ui.slash.subcommand(base_names="recurring",name="add",description="updates the time and checks for any recurring payments",options=[
        SlashOption(str,name="RPO",description='RPO to check',required=True),
        SlashOption(str,name="Name",description="Name for the recourring event.",required=True),
        SlashOption(int,name='Next',description="First day for event to trigger",required=True),
        SlashOption(int,name="Interval",description="How long between triggers of event",required=True),
        SlashOption(int,name="Amount",description="Amount to add/remove on event (can be 0 for a tracker event)",required=True)]
    , guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(allowed={"225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,"338173415527677954": SlashPermission.ROLE},
        forbidden={"225345178955808768": SlashPermission.ROLE})})
async def command(ctx, rpo, name, next, interval, amount):
    reccuring = json.load(open("recurring.json"))
    if rpo.upper() in list(reccuring.keys()):
        reccuring[rpo.upper()].append({"name":str(name),"nextPayment":int(next),"interval":int(interval),"amount":int(amount)})
    else:
        reccuring.update({rpo.upper():[{"name":str(name),"nextPayment":int(next),"interval":int(interval),"amount":int(amount)}]})
    with open("recurring.json","w") as r:
        json.dump(reccuring,r)
    await ctx.send("Added new reccuring event to RPO "+str(rpo.upper())+": "+str(name)+" every "+str(interval)+" days, starting on day "+str(next)+" for a change in balance of "+str(amount)+".")

@ui.slash.subcommand(base_names="recurring",name="other",description="quereys/removes reccuring event",
    options=[
        SlashOption(str,name="RPO",description='RPO to check',required=True),
        SlashOption(str,name="Name",description="OPTIONAL. recurring event to look at, if none given, will show all for the RPO.")
    ]
    , guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(allowed={"225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,"338173415527677954": SlashPermission.ROLE},
        forbidden={"225345178955808768": SlashPermission.ROLE})})
async def command(ctx, rpo, name=None):
    reccuring = json.load(open("recurring.json"))
    if name is None:
        if len(reccuring[rpo.upper()]) == 0:
            await ctx.send("No reccuring events have been recorded for this RPO")
        else:
            try:await ctx.send("This RPO has the following recorded events: "+str([x['name'] for x in reccuring[rpo.upper()]]))
            except:await ctx.send("No reccuring events have been recorded for this RPO")
    else:
        btn = await (
                await ctx.send("Query or Remove?", components=[
                    Button("Query", "Query", color=ButtonStyles.blurple), Button("Remove", "Remove", color=ButtonStyles.red)
                ])
            ).wait_for("button", client)
        i = 0
        length = len(reccuring[rpo.upper()])
        if btn.label == "Remove":
            while i<length:
                if name==reccuring[rpo.upper()][i]['name']:
                    reccuring[rpo.upper()].pop(i)
                i+=1
            with open("recurring.json","w") as r:
                json.dump(reccuring,r)
            await ctx.send("Specified Event has been removed.")
        elif btn.label == "Query":
            for event in reccuring[rpo.upper()]:
                await ctx.send(str(event))
                await asyncio.sleep(1)

@ui.slash.subcommand(base_names="update",name="time",description="updates the time and checks for any recurring payments", 
    guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(
        allowed={"363095569515806722": SlashPermission.USER,"225344348903047168": SlashPermission.USER},
        forbidden={"225345178955808768": SlashPermission.ROLE})})
async def command(ctx):
    data = sfs.parse_savefile('persistent.sfs')
    ksptime = a.ksptime(data)
    reccuring = json.load(open("recurring.json"))
    accountBalanceSheet = pd.read_csv(RPOInfoURL)
    accountBalanceSheet['new'] = accountBalanceSheet['TAG']
    accountBalanceSheet = accountBalanceSheet.set_index('new')
    accountBalanceSheet['Account Balance'] = accountBalanceSheet['Account Balance'].astype(str).apply(lambda x: x.replace('$', '').replace(',', '')).astype(float)
    df = pd.DataFrame()
    df["RPO"] = []
    df["name"] = []
    df["amount"] = []
    df["nextPayment"] = []
    for rpo in list(reccuring.keys()):
        length = len(reccuring[rpo])
        i=0
        while i<length:
            if reccuring[rpo][i]["nextPayment"]<ksptime[0]:
                accountBalanceSheet.loc[str(rpo).upper(), 'Account Balance'] += reccuring[rpo][i]["amount"]
                reccuring[rpo][i]["nextPayment"] += reccuring[rpo][i]["interval"]
                df.loc[-1] = [rpo.upper(),reccuring[rpo][i]["name"],reccuring[rpo][i]["amount"],reccuring[rpo][i]["nextPayment"]]
            i+=1    
    try:
        a.render_mpl_table(df,header_columns=0,col_width=10)
        await ctx.send(file=discord.File(r'table.png'))
    except:await ctx.send("No recurring events have happened")
    with open("recurring.json","w") as r:
        json.dump(reccuring,r)
    gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
    sh = gc.open_by_key('1W_IAmn7t7-79WC4MHl1RzGj6q2Bq1-CJ5kDjR2KoXGw')
    worksheet = sh.get_worksheet(0)
    set_with_dataframe(worksheet, accountBalanceSheet)



@client.event
async def on_message(message):
    await client.process_commands(message)
    channel = client.get_channel(906578081496584242)
    if message.guild is None and message.author != client.user:
        if message.content is not None:
            if message.content is not None:
                ticket = a.add_onmessage(message)
                if ticket == None:
                    return
                else:
                    await channel.send("Message from "+str(message.author)+" "+str(message.author.id)+", Ticket: `"+str(ticket[0])+"`):")
                    if ticket[1] == "new":
                        await message.author.send("Remember to check our FAQ to see if your question/issue is addressed there: https://cpry.net/discordfaq")
                    if message.attachments:
                        for attachment in message.attachments:
                            attachedFile = await attachment.to_file()
                            await channel.send(file=attachedFile)
                    if message.content is not None:
                        await channel.send(message.content)

    elif message.guild is client.get_guild(225345178955808768) and message.author != client.user:
        if a.channel_check(message,[244979839147311104,897255188602179614,906190976320679996,906578081496584242,837859633502748672,426016300439961601,682559641930170379,686028730572865545,687817008355737606,839690221083820032,430197357100138497]):
            return
        elif re.search(r"bruh", message.content, re.MULTILINE|re.IGNORECASE):
            await message.delete()
        elif re.search(r"~~:.|:;~~", message.content, re.MULTILINE|re.IGNORECASE) or re.search(r"tilde tilde colon dot vertical bar colon semicolon tilde tilde", message.content, re.MULTILINE|re.IGNORECASE):
            await message.delete()
            role = message.guild.get_role(676250179929636886)
            await message.author.add_roles([676250179929636886])
            levelrole = 0
            for role in message.author.roles:
                if str(role.id) in ['837812373451702303','837812586997219372','837812662116417566','837812728801525781','837812793914425455','400445639210827786','685331877057658888','337743478190637077','837813262417788988']:
                    levelrole = role.id
            await message.author.remove_roles([levelrole])
            await asyncio.sleep(600)
            await message.author.remove_roles([676250179929636886])
            await message.author.add_roles([levelrole])

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("This command is on cooldown, you can use it in "+ str(round(error.retry_after, 2))+" seconds.")

async def on_connect():
    print("Logged In!")
client.on_connect = on_connect
client.run(token)