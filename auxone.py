from __future__ import print_function
import os.path
from discord import client
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
import six
from logging.handlers import RotatingFileHandler
from matplotlib.backends.backend_pdf import PdfPages
from collections.abc import Sequence
from cryptography.fernet import Fernet
import math
with open('details.json') as f:
    data = json.load(f) 

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
    data['RPOKnowledgegid'])

with open('filekey.key','rb') as file:
    key = file.read()
fernet = Fernet(key)

def author_check(author):
    return lambda message: message.author == author

def make_sequence(seq):
    if seq is None:
        return ()
    if isinstance(seq, Sequence) and not isinstance(seq, str):
        return seq
    else:
        return (seq,)

def message_check(channel=None, author=None, content=None, ignore_bot=True, lower=True):
    channel = make_sequence(channel)
    author = make_sequence(author)
    content = make_sequence(content)
    if lower:
        content = tuple(c.lower() for c in content)
    def check(message):
        if ignore_bot and message.author.bot:
            return False
        if channel and message.channel not in channel:
            return False
        if author and message.author not in author:
            return False
        actual_content = message.content.lower() if lower else message.content
        if content and actual_content not in content:
            return False
        return True
    return check


def render_mpl_table(data, col_width=5, row_height=0.625, font_size=20,
                     header_color='#40466e', row_colors=['xkcd:sky blue', 'xkcd:blue grey'], edge_color='k',
                     bbox=[0, 0, 1.3, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    plt.savefig('table.png',dpi=250,bbox_inches='tight')
    return ax

def render_mpl_table_colors(data, Colors, col_width=5, row_height=0.625, font_size=20,
                     header_color='#40466e', edge_color='k',
                     bbox=[0, 0, 1.3, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox,cellColours=Colors, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
    plt.savefig('table.png',dpi=250,bbox_inches='tight')
    return ax

def render_mpl_table_colors_pdf(export_pdf, data, Colors, col_width=5, row_height=0.625, font_size=20,
                     header_color='#40466e', edge_color='k',
                     bbox=[0, 0, 1.3, 1], header_columns=0,
                     ax=None, **kwargs):
    plt.rcParams['text.usetex'] = False
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox,cellColours=Colors, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
    export_pdf.savefig(dpi=250,bbox_inches='tight')
    plt.close()
    return export_pdf

def Portfolio(rpo, service):
    Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
    Investmentsdf = pd.read_csv(InvestorsURL, index_col=0) #Creates the data frame for investors
    spreadoutsdf = pd.read_csv(SSaccessURL, index_col=0) #creates the data frame that we reference to get the info needed to push stuff to spreadsheets
    df = pd.DataFrame(Investmentsdf.loc[rpo]) #creates the data frame with the specific investments with just one rpo
    df = df.reset_index() #fixes the data frame so it can be concatenated with with the market value data frame
    Marketdf = Marketdf.reset_index() #fixes the data frame so it can be concatenated with the specific investments data frame
    df = pd.concat([df, Marketdf], axis = 1).dropna(axis=0).rename(columns={rpo:'Shares'}) #concatenates the two dataframes, removes private companies, and fixes a column title
    df['Market Value'] = df['Shares'] * df['Market Price']  #does the math to make the market value column
    df['new'] = df['Symbol']
    df = df.set_index('new')
    sum = df['Market Value'].sum() #Gets the sum of the stock prices
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
    df['Profit / Loss '] = df['Market Value'].astype(float) - df['Total Invested (includes fees) '].astype(float)
    request = service.spreadsheets().values().get(spreadsheetId=spreadoutsdf.loc[rpo, 'sheetID'], range='Visuals!C32:C40', majorDimension = 'COLUMNS', valueRenderOption = 'UNFORMATTED_VALUE')
    response = request.execute()
    history = response['values']
    history = [ item for elem in history for item in elem]
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
                df['Shares'].tolist(),
                df['Symbol'].tolist(),
                df['Market Price'].tolist(),
                df['Day change'].tolist(),
                df['Market Value'].tolist(),
                df['Total Invested (includes fees) '].tolist(),
                df['Cost Basis '].tolist(),
                df['Profit / Loss '].tolist()]},#Converts dataframe into the form needed to send to google sheets
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

def undeclared(message):
        author = message.author
        userid = author.id
        RPO  = 'A'
        newUser = {'userID':[str(userid)], 'RPO':RPO, 'Author':[author], 'Coin Amount': [0], 'lastWorkAmount': [0], 'lastWork': [0], 'lastDaily': [0]}
        df = pd.DataFrame(newUser).set_index('userID')
        df2 = pd.DataFrame(newUser)
        userList = pd.read_csv(UserListURL, index_col=0).append(pd.DataFrame(newUser))
        userListOutput = pd.read_csv(UserListURL).append(df2)
        userListOutput['userID'] = userListOutput['userID'].astype(str)
        gc = gspread.service_account(filename='service_account.json') #gets credentials
        sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
        worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
        # APPEND DATA TO SHEET
        #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
        set_with_dataframe(worksheet, userListOutput) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
        print("<@!"+str(message.author.id) + "> you are now in RPO " + str(newUser['RPO'][0]))

def channel_check(message, channels):
    return message.channel.id in channels

def role_check(message, roles):
    for role in roles:
        if discord.utils.get(message.guild.roles, id=int(role)) in message.author.roles:
            return True
    return False

def author_check2(message, authors):
    return message.author.id in authors

def open_channel(message, json):
    if str(message.author.id) in list(json.keys()):
        return (json[str(message.author.id)])
    else:
        return False

def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = [c for c in string if 0 < ord(c) < 255]
    return ''.join(stripped)

def part_check(tech,part):
    length = len(tech)
    i = 0
    partlist = list()
    while i < length:
        if tech[i]['id'] not in ['tremendousEfficiencyPropulsion', 'veryHighEfficiencyPropulsion', 'advColonization', 'exoticRadiators', 'microwavePowerTransmission', 'exoticElectricalSystems', 'experimentalElectricalSystems', 'highPowerElectricalSystems', 'exoticPlasmaPropulsion', 'appliedHighEnergyPhysics', 'highEnergyScience', 'scientificOutposts', 'resourceExploitation', 'advOffworldMining', 'advAerospaceEngineering', 'expAircraftEngines', 'offworldManufacturing', 'extremeFuelStorage', 'colossalRocketry', 'giganticRocketry', 'fusionRockets', 'ultraHighEnergyPhysics', 'unifiedFieldTheory', 'antimatterPower', 'quantumReactions', 'exoticReactions', 'advFusionReactions', 'fusionPower', 'experimentalMotors']:
            for item in tech[i]['part']:
                partlist.append(item)
        i += 1
    return part not in partlist

def add_onmessage(message):
    with open('tickets.json',"rb") as t:
        temp = fernet.decrypt(t.read())
    tickets = json.loads(temp)
    for ticket in list(tickets.keys()):
        if tickets[ticket]["open"] == "True":
            if tickets[ticket]['starter'] == message.author.id:
                if (int(time.mktime(message.created_at.timetuple()))-int(tickets[ticket]['time'])) < 5:
                    return None
                messages = tickets[ticket]['messages']
                numMessages = len(list(messages.keys()))
                messages.update({str(numMessages):str(message.author)+": "+str(message.content)})
                tickets[ticket]['messages'] = messages
                tickets[ticket]['time'] = time.mktime(message.created_at.timetuple())
                with open('tickets.json','wb') as t:
                    t.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))
                return [ticket,"old"]
    newTicketNum = len(list(tickets.keys()))
    newTicket = {
            "open":"True","time":time.mktime(message.created_at.timetuple()),"starter":message.author.id, "messages":{
                "0":str(message.author)+": "+str(message.content)
            }
        }
    tickets.update({str(newTicketNum)+": "+str(message.author):newTicket})
    with open('tickets.json','wb') as t:
        t.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))
    return [str(newTicketNum)+": "+str(message.author),"new"]


def add_message(ctx,message, ticket):
    with open('tickets.json',"rb") as t:
        temp = fernet.decrypt(t.read())
    tickets = json.loads(temp)
    messages = tickets[ticket]['messages']
    numMessages = len(list(messages.keys()))
    messages.update({str(numMessages):str(ctx.author)+": "+str(message)})
    tickets[ticket]['messages'] = messages
    with open('tickets.json','wb') as t:
        t.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))
    return int(tickets[ticket]['starter'])

def ksptime(save):
    Sectime = float(save['GAME']['FLIGHTSTATE']['UT'])
    hours = math.floor(Sectime/3600)
    minutes = math.floor((Sectime%3600)/60)
    seconds = (Sectime%3600)%60
    return [math.floor(hours/6),hours%6,minutes,seconds]