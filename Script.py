from __future__ import print_function
import enum
import os.path
from googleapiclient.discovery import build
import gspread
from gspread_dataframe import set_with_dataframe
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pandas as pd
import numpy as np
import json
#imports all needed packages

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
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
    data['InvestersID'],
    data['SSaccessgid']
) #these make the URLS needed for pandas to read the needed CSVs, in combination with the details.json file
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
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
Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
Investmentsdf = pd.read_csv(InvestorsURL, index_col=0).dropna(axis=1, how='all') #Creates the data fram for investors
RPOlist = list() #initializes empty list for list of RPOs with investments
spreadoutsdf = pd.read_csv(SSaccessURL, index_col=0)

def updateInvestors():
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=data['Master_SPREADSHEET_ID'],
                            range=data['Master_RANGE_NAME']).execute()
    values = result.get('values', [])
    Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
    Investmentsdf = pd.read_csv(InvestorsURL, index_col=0).dropna(axis=1, how='all') #Creates the data fram for investors
    RPOlist = list() #initializes empty list for list of RPOs with investments
    spreadoutsdf = pd.read_csv(SSaccessURL, index_col=0)
    spreadoutsdf2 = pd.read_csv(SSaccessURL)
    for row in values:
        RPOlist.append(row[0]) #Adds all RPOs with investments to a list
    #print(RPOlist)
    for i in RPOlist:
        Investmentsdf.loc[i].dropna()#removes all placeholder/non investment rows
        print(Investmentsdf.loc[i])
    for i in RPOlist:
        try:
            #print(i)
            spreadoutsdf.loc[i]
        except:
            newRPO = i
            newsheetID = input('Input sheet ID for new RPO ' + newRPO + " ") #gets sheetID from user for new RPO
            newgid1 = input('Input GID1 for new RPO ' + newRPO + " ") #gets gid for tab1 from user for new RPO
            newgid2 = input('Input GID2 for new RPO ' + newRPO + " ") #gets gid for tab2 from user for new RPO
            newrpoDict = {'rpo': [newRPO],'sheetID': [newsheetID], 'gid1': [newgid1], 'gid2': [newgid2]} #creates a dictionary to transform into a dataframe to add to the list of sheets and use to add to the persistent list of them
            spreadoutsdf = spreadoutsdf.append(pd.DataFrame(data=newrpoDict).set_index('rpo')) #adds new RPO info to the list of sheets
            spreadoutsdf2 = spreadoutsdf2.append(pd.DataFrame(data=newrpoDict)) #adds new RPO info to the list of sheets for sending to permanent storage
            # ACCES GOOGLE SHEET
            gc = gspread.service_account(filename='service_account.json') #gets credentials
            sh = gc.open_by_key(data['SSaccessID']) #gets sheetinfo
            worksheet = sh.get_worksheet(7) #-> 0 - first sheet, 1 - second sheet etc. 
            # APPEND DATA TO SHEET
            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
            set_with_dataframe(worksheet, spreadoutsdf2) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
    return RPOlist

def portfolio(rpo):
    Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
    Investmentsdf = pd.read_csv(InvestorsURL, index_col=0) #Creates the data frame for investors
    spreadoutsdf = pd.read_csv(SSaccessURL, index_col=0) #creates the data frame that we reference to get the info needed to push stuff to spreadsheets
    df = pd.DataFrame(Investmentsdf.loc[rpo]) #creates the data frame with the specific investments with just one rpo
    df = df.reset_index() #fixes the data frame so it can be concatenated with with the market value data frame
    Marketdf = Marketdf.reset_index() #fixes the data frame so it can be concatenated with the specific investments data frame
    df = pd.concat([df, Marketdf], axis = 1).dropna(axis=0).rename(columns={rpo:'Shares'}) #concatenates the two dataframes, removes private companies, and fixes a column title
    df['Market Value'] = df['Shares'] * df['Market Price']  #does the math to make the market value column
    sum = df['Market Value'].sum() #Gets the sum of the stock prices



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
    print(history)
    batch_update_values_request_body = {
        "value_input_option" : 'USER_ENTERED',  # How the input data should be interpreted.
        "data": [
            {"range": 'A11:E44',
            "majorDimension":'COLUMNS',
            "values": [
                df['Shares'].tolist(),
                df['Symbol'].tolist(),
                df['Market Price'].tolist(),
                df['Day change'].tolist(),
                df['Market Value'].tolist()]},#Converts dataframe into the form needed to send to google sheets
            {"range": 'E4',
            "majorDimension":'COLUMNS',
            "values":[[sum]]
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
    

if __name__ == '__main__':
    RPOlist = updateInvestors()



if __name__ == '__main__':
    for i in RPOlist:
       portfolio(i)