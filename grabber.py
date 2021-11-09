import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
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
yt = build('youtube', 'v3', credentials=creds)
def comments(videoID):
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
    print(authorList)