from __future__ import print_function
import lightbulb
from lightbulb.commands import user
import pandas as pd
import numpy as np
import json
import time
import matplotlib.pyplot as plt
import six
from matplotlib.backends.backend_pdf import PdfPages
from collections.abc import Sequence
from cryptography.fernet import Fernet
import math
import seaborn as sns
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Shadow
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

def undeclared(ctx):
        author = ctx.author
        userid = author.id
        RPO  = 'A'
        newUser = {'userID':[str(userid)], 'RPO':RPO, 'Author':[str(author.username)], 'Coin Amount': [0], 'lastWorkAmount': [0], 'lastWork': [0], 'lastDaily': [0]}
        df = pd.DataFrame(newUser).set_index('userID')
        userList = pd.DataFrame(json.loads(fernet.decrypt(open('UserInfo.json',"rb").read())))
        userListOutput = userList.append(df)
        with open('UserInfo.json','wb') as t:
            t.write(fernet.encrypt(json.dumps(userListOutput.to_dict()).encode('utf-8')))

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
                if (int(round(time.time(),0))-int(tickets[ticket]['time'])) < 5:
                    return None
                messages = tickets[ticket]['messages']
                numMessages = len(list(messages.keys()))
                messages.update({str(numMessages):str(message.author.username)+": "+str(message.content)})
                for attachment in message.attachments:
                    numMessages = len(list(messages.keys()))
                    messages.update({str(numMessages):str(message.author)+": "+str(attachment.url)})
                tickets[ticket]['messages'] = messages
                tickets[ticket]['time'] = round(time.time(),0)
                with open('tickets.json','wb') as t:
                    t.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))
                return [ticket,"old"]
    newTicketNum = len(list(tickets.keys()))
    newTicket = {
            "open":"True","time":round(time.time(),0),"starter":message.author.id, "messages":{
                "0":str(message.author)+": "+str(message.content)
            }
        }
    tickets.update({str(newTicketNum):newTicket})
    with open('tickets.json','wb') as t:
        t.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))
    return [str(newTicketNum)+": "+str(message.author.username),"new"]

def add_message(ctx,message, userID):
    with open('tickets.json',"rb") as t:
        temp = fernet.decrypt(t.read())
    tickets = json.loads(temp)
    for ticket in list(tickets.keys()):
        if tickets[str(ticket)]['starter']==userID:break
    messages = tickets[ticket]['messages']
    numMessages = len(list(messages.keys()))
    messages.update({str(numMessages):str(ctx.author.username)+": "+str(message)})
    tickets[ticket]['messages'] = messages
    open('tickets.json','wb').write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))

def ksptime(save):
    Sectime = float(save['GAME']['FLIGHTSTATE']['UT'])
    hours = math.floor(Sectime/3600)
    minutes = math.floor((Sectime%3600)/60)
    seconds = (Sectime%3600)%60
    return [(hours//6)+1,hours%6,minutes,seconds]

def transferRPO(RPO,ssaccess):
    investments = json.load(open('investments.json'))
    try:
        portfolio = pd.read_csv('https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid=1205501929'.format(ssaccess),usecols=[0,1,2,3,4,5,6,7])
        investmentsList= list()
        for i,j in portfolio.iterrows():
            investmentsList.append([j.loc[x] for x in list(portfolio.columns)])
        history = pd.read_csv('https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid=1195787828'.format(ssaccess),usecols=[2],skiprows=12,names=['history'])
        investmentsList2 = list()
        for x in investmentsList[1:]:
            if (x[0] !=0):
                investmentsList2.append(x)
        investments.update({RPO:
            {"Market_Value":investmentsList[0][4],
            "Total_Invested":investmentsList[0][5],
            "Profit/Loss":investmentsList[0][7],
            "Investments":investmentsList2,
            "Market_History":history['history'].tolist()
            }})
        json.dump(investments,open('investments.json','w'))
    except: print(RPO, "has no investments")

def as_currency(amount):
    if amount >= 0:
        return '${:,.2f}'.format(amount)
    else:
        return '-${:,.2f}'.format(abs(amount))

def as_percent(amount):
    if amount >= 0:
        return '{:,.2f}%'.format(amount)
    else:
        return '-{:,.2f}%'.format(abs(amount))

def rpoPortfolio(RPO):
    investments = json.load(open('investments.json'))
    if RPO not in list(investments.keys()):
        return False
    investments[RPO]['Market_History']  = [item.replace('$', '').replace(',', '') if isinstance(item, str) else item for item in investments[RPO]['Market_History']]
    investments[RPO]['Market_History'] = [float(item) for item in investments[RPO]['Market_History']]
    i=0
    length = len(investments[RPO]['Investments'])
    while i<length:
        investments[RPO]['Investments'][i]= [item.replace('$', '').replace(',', '').replace('%', '') if isinstance(item, str) else item for item in investments[RPO]['Investments'][i]]
        tempList = list()
        for item in investments[RPO]['Investments'][i]:
            try: 
                if float(item).is_integer():
                    tempList.append(int(float(item)))
                else:
                    tempList.append(float(item))
            except: tempList.append(str(item))
        investments[RPO]['Investments'][i] = tempList
        i+=1
    #print(investments[RPO]['Investments'])
    pdf = PdfPages('multipage.pdf')
    table_data = [
        ['Market Value',as_currency(investments[RPO]['Market_Value'])],
        ['Total Invested',as_currency(investments[RPO]['Total_Invested'])],
        ['Profit/Loss',as_currency(investments[RPO]['Profit/Loss'])]]
    fig, ax = plt.subplots()
    cellColours = []
    if float(str(table_data[0][1]).replace('$', '').replace(',', ''))>0:
        cellColours.append(['#00ff0080','#00ff0080'])
    elif float(str(table_data[0][1]).replace('$', '').replace(',', ''))<0:
        cellColours.append(['#ff000080','#ff000080'])
    else: cellColours.append(['#0000ff80','#0000ff80'])
    cellColours.append(['#0000ff80','#0000ff80'])
    if float(str(table_data[2][1]).replace('$', '').replace(',', ''))>0:
        cellColours.append(['#00ff0080','#00ff0080'])
    elif float(str(table_data[2][1]).replace('$', '').replace(',', ''))<0:
        cellColours.append(['#ff000080','#ff000080'])
    else: cellColours.append(['#0000ff80','#0000ff80'])
    mpl_table = ax.table(cellText=table_data, cellColours=cellColours, loc='center')
    mpl_table.set_fontsize(14)
    mpl_table.scale(1,4)
    ax.axis('off')
    pdf.savefig()
    plt.close()
    fig, ax = plt.subplots()
    ax.axis('off')
    investmentsList = list()
    for item in investments[RPO]['Investments']:
        item.pop(5)
        item[2] = as_currency(float(item[2]))
        item[3] = as_percent(float(item[3]))
        item[4] = as_currency(float(item[4]))
        item[5] = as_currency(float(item[5]))
        item[6] = as_currency(float(item[6]))
        investmentsList.append(item)
    mpl_table = ax.table(cellText=investmentsList, colLabels=['Shares', 'Symbol', 'Price','Day Change', 'Market Value', 'Cost Basis', 'Profit / Loss'], loc='center',bbox=[0,0,1.5,1])
    labels = list()
    fracs = list()
    for (row, col), cell in mpl_table.get_celld().items():
        cell.set_facecolor('#000000')
        cell.set_text_props(color='#ffffff')
        cell.set_edgecolor(color='#808080')
        cell.set_text_props(fontproperties=FontProperties(weight='demibold'))
        if (row == 0):
            cell.set_text_props(fontproperties=FontProperties(weight='bold'))
            cell.set_facecolor(color='#808080')
            cell.set_fontsize(18)
        elif (col == 0):
            cell.set_text_props(color='#00FFFF')
        elif (row>0 and col==3):
            text = float(str(cell.get_text()).split(',')[2].replace('%','').replace(" ",'').replace("'",'').replace(")",''))
            if text>0:cell.set_text_props(color='#00ff00')
            elif text<0:cell.set_text_props(color='#ff0F0F')
            else: cell.set_text_props(color='#00FFFF')
        elif (row>0 and col==6):
            text = float(str(cell.get_text()).split(',')[2].replace('$','').replace(" ",'').replace("'",'').replace(")",''))
            if text>0:cell.set_text_props(color='#00ff00')
            elif text<0:cell.set_text_props(color='#ff0F0F')
            else: cell.set_text_props(color='#00FFFF')
        if (col == 4 and row>0):
            fracs.append(float(str(cell.get_text()).split(',')[2].replace('$','').replace(" ",'').replace("'",'').replace(")",'')))
        if (col == 1 and row>0):
            labels.append(str(cell.get_text()).split(',')[2].replace('$','').replace(" ",'').replace("'",'').replace(")",''))
    mpl_table.auto_set_column_width([0,1,2,3,4,5,6,7])
    mpl_table.auto_set_font_size(True)
    pdf.savefig(bbox_inches='tight',pad_inches=0.15)
    plt.close()
    fig, ax = plt.subplots()
    # make a square figure and axes
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    i=0
    length = len(fracs)-1
    while i<length:
        if fracs[length] == 0:
            fracs.pop(length)
            labels.pop(length)
        length-=1
    labels = tuple(labels)
    # We want to draw the shadow for each pie but we will not use "shadow"
    # option as it does'n save the references to the shadow patches.
    pies = plt.pie(fracs, labels=labels, autopct='%1.1f%%',)
    for w in pies[0]:
        # set the id with the label.
        w.set_gid(w.get_label())
        # we don't want to draw the edge of the pie
        w.set_edgecolor("none")
    for w in pies[0]:
        # create shadow patch
        s = Shadow(w, -0.01, -0.01)
        s.set_gid(w.get_gid() + "_shadow")
        s.set_zorder(w.get_zorder() - 0.1)
        ax.add_patch(s)
    pdf.savefig()
    df = pd.DataFrame()
    df['Value'] = investments[RPO]['Market_History']
    df['Days'] = range(len(investments[RPO]['Market_History']))
    plt.close()
    sns.set_theme(style="darkgrid")
    graph = sns.lineplot(data=df,x="Days",y='Value')
    pdf.savefig()
    pdf.close()
    return True

def strip_class(arg:str):
    if arg =="<class 'str'>":return "str"
    if arg =="<class 'int'>":return "int"
    if arg =="<class 'float'>":return "float"
    if arg =="<class 'bool'>":return "boolean"
    return arg

def list_to_string(arg: list):
    tempstr = ", "
    return tempstr.join(arg)

def option_help(option: lightbulb.commands.base.OptionLike) -> str:
    vartype = strip_class(option.arg_type)
    options = list_to_string(option.choices)
    default = option.default
    if option.required: required = " "
    else: required = " not "
    return f" Arg type: {vartype}, Choices: {options}, Default: {default}, is{required}required"


class userInfo:
    def readUserInfo():
        df = pd.DataFrame(json.loads(fernet.decrypt(open('UserInfo.json',"rb").read())))
        with open('UserInfo.json','wb') as t:
            t.write(fernet.encrypt(json.dumps(df.to_dict()).encode('utf-8')))
        return df

    def writeUserInfo(userinfodf):
        with open('UserInfo.json','wb') as t:
            t.write(fernet.encrypt(json.dumps(userinfodf.to_dict()).encode('utf-8')))
    
    def editCoins(userID, amount):
        userInfo = pd.DataFrame(json.loads(fernet.decrypt(open('UserInfo.json',"rb").read())))
        output = {'before':userInfo.loc[str(userID),"Coin Amount"]}
        if str(userID) not in list(userInfo.index):
            return False
        elif float(amount)>=0:
            output.update({'changed':amount})
            userInfo.loc[str(userID),"Coin Amount"]+=amount
            output.update({'final':userInfo.loc[str(userID),"Coin Amount"]})
            with open('UserInfo.json','wb') as t:
                t.write(fernet.encrypt(json.dumps(userInfo.to_dict()).encode('utf-8')))
            return output
        elif float(amount)<0:
            change = min(userInfo.loc[str(userID),"Coin Amount"],abs(amount))
            output.update({'changed':change})
            userInfo.loc[str(userID),"Coin Amount"]-=change
            output.update({'final':userInfo.loc[str(userID),"Coin Amount"]})
            with open('UserInfo.json','wb') as t:
                t.write(fernet.encrypt(json.dumps(userInfo.to_dict()).encode('utf-8')))
            return output

    def getCoins(userID):
        userInfo = pd.DataFrame(json.loads(fernet.decrypt(open('UserInfo.json',"rb").read())))
        with open('UserInfo.json','wb') as t:
            t.write(fernet.encrypt(json.dumps(userInfo.to_dict()).encode('utf-8')))
        try:
            return userInfo.loc[str(userID),"Coin Amount"]
        except:
            return 0

    def getWallet():
        df = pd.read_json('Account Balance.json')
        df.to_json('Account Balance.json')
        return df
    
    def writeWallet(walletDf):
        walletDf.to_json('Account Balance.json')

    def editWallet(RPO, amount):
        rpoInfo = pd.read_json('Account Balance.json')
        print(rpoInfo.head(10))
        output = {'before':rpoInfo.loc[str(RPO),"Account Balance"]}
        if str(RPO) not in list(rpoInfo.index):
            return False
        elif float(amount)>=0:
            output.update({'changed':amount})
            rpoInfo.loc[str(RPO),"Account Balance"] = round(float(str(rpoInfo.loc[str(RPO),"Account Balance"]).replace(',',''))+amount,2)
            output.update({'final':rpoInfo.loc[str(RPO),"Account Balance"]})
            rpoInfo.to_json('Account Balance.json')
            return output
        elif float(amount)<0:
            change = min(float(str(rpoInfo.loc[str(RPO),"Account Balance"]).replace(',','')),abs(float(amount)))
            output.update({'changed':change})
            rpoInfo.loc[str(RPO),"Account Balance"] = round(float(str(rpoInfo.loc[str(RPO),"Account Balance"]).replace(",",''))-change,2)
            output.update({'final':rpoInfo.loc[str(RPO),"Account Balance"]})
            rpoInfo.to_json('Account Balance.json')
            return output

    def roleCheck(author, aroles):
        roles = author.role_ids
        for role in roles:
            if role in aroles: return True
        return False

class checks:
    # Defining the custom check function
    def check_author_is_me(context)->bool:# Returns True if the author's ID is the same as the given one
        return context.author.id == 363095569515806722

    def check_econ_channel(context):
        return context.channel_id in [893867549589131314, 687817008355737606]

    def check_modmail_channel(context):
        return context.channel_id in [906578081496584242,687817008355737606]
    
    def Punished(context):
        roles = context.member.role_ids
        for role in roles:
            if role in [684936661745795088,676250179929636886]:
                return False
        #if context.author.id == 920994579342311465: return False
        return True 
    
    def check_invest_channel(context):return context.channel_id in [900523609603313704, 687817008355737606]

    def check_publisher(context): return context.author.id in [363095569515806722, 225344348903047168, 146285543146127361]