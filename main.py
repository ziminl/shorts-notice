import os
import pickle
import time
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def authenticate_youtube():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    youtube = build(API_NAME, API_VERSION, credentials=credentials)
    return youtube

def get_subscriptions(youtube):
    request = youtube.subscriptions().list(
        part='snippet',
        mine=True,
        maxResults=50
    )
    response = request.execute()

    subscriptions = []
    for item in response.get('items', []):
        channel_id = item['snippet']['resourceId']['channelId']
        subscriptions.append(channel_id)
    return subscriptions

def check_new_uploads(youtube, channel_id):
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        order='date',
        maxResults=5
    )
    response = request.execute()

    for item in response['items']:
        video_id = item['id']['videoId']
        video_title = item['snippet']['title']
        video_url = f'https://www.youtube.com/watch?v={video_id}'

        video_details_request = youtube.videos().list(
            part='contentDetails',
            id=video_id
        )
        video_details_response = video_details_request.execute()
        
        duration = video_details_response['items'][0]['contentDetails']['duration']
        
        if 'M' in duration:
            continue
        else:
            print(f"New Shorts uploaded! {video_title} : {video_url}")

def main():
    youtube = authenticate_youtube()
    subscriptions = get_subscriptions(youtube)

    while True:
        for channel_id in subscriptions:
            check_new_uploads(youtube, channel_id)
        
        time.sleep(60)

if __name__ == '__main__':
    main()
