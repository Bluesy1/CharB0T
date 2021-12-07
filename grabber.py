import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pandas as pd
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
creds = None
def comments(videoID):
    creds = None
    if os.path.exists('token1.json'):
        creds = Credentials.from_authorized_user_file('token1.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token1.json', 'w') as token:
            token.write(creds.to_json())
    yt = build('youtube', 'v3', credentials=creds)
    request = yt.commentThreads().list(
        part="snippet,replies",
        videoId=str(videoID)
    )
    response = request.execute()
    authorList = list()
    for item in response['items']:
        #print(item)
        authorList.append(item['snippet']['topLevelComment']['snippet']['authorDisplayName'])
    authorList = list(set(authorList))
    return authorList

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', scopes)
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
while True:
    id = input("Youtube video ID? ")
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
    commenters = comments(id)
    for commenter in commenters:
        if commenter in df['Name'].tolist():
            df.loc[commenter, 'Points']+=1
        else:
            df.loc[-1] = [commenter, 1]
    batch_update_values_request_body = {
        'value_input_option':'USER_ENTERED',
        'data':[
            {"range":range_,
            "majorDimension":"COLUMNS",
            "values": [df['Name'].tolist(),df['Points'].tolist()]},
            {"range":'YT Comment Records!E1',
            "majorDimension":"COLUMNS",
            "values": [["Last Video: "+id]]}]}
    request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body=batch_update_values_request_body)
    response = request.execute()
    print(response)