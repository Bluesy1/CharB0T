from __future__ import print_function
import os.path
from googleapiclient.discovery import build
import gspread
from gspread_dataframe import set_with_dataframe
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pandas as pd
import numpy
import scipy
#imports all needed packages

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# The ID and range of a sample spreadsheet.
Master_SPREADSHEET_ID = '1MyTqsdG3uzOYt_sNzc1aKiLXMfATl4pBJg5lf-4hSQw'
Master_RANGE_NAME = 'InvestorsEx!A2:A'
googleSheetId = '1W_IAmn7t7-79WC4MHl1RzGj6q2Bq1-CJ5kDjR2KoXGw'
workSheetName = '57562462'
InvestersID = '1MyTqsdG3uzOYt_sNzc1aKiLXMfATl4pBJg5lf-4hSQw'
Investorssheetgid = '220412879'
SSaccessID = InvestersID
SSaccessgid = '720954414'
URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    googleSheetId,
    workSheetName
)
InvestorsURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    InvestersID,
    Investorssheetgid
)
SSaccessURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    InvestersID,
    SSaccessgid
)
def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
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

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=Master_SPREADSHEET_ID,
                                range=Master_RANGE_NAME).execute()
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
    for i in RPOlist:
        try:
            print(i)
            print(spreadoutsdf.loc[i])
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
            sh = gc.open_by_key(SSaccessID) #gets sheetinfo
            worksheet = sh.get_worksheet(7) #-> 0 - first sheet, 1 - second sheet etc. 
            # APPEND DATA TO SHEET
            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
            set_with_dataframe(worksheet, spreadoutsdf2) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET

if __name__ == '__main__':
    main()