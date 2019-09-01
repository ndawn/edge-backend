import os.path
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_PATH = 'utils/google/'


def get_service():
    creds = None

    if os.path.exists(os.path.join(CREDENTIALS_PATH, 'token.pickle')):
        with open(os.path.join(CREDENTIALS_PATH, 'token.pickle'), 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(os.path.join(CREDENTIALS_PATH, 'credentials.json'), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.path.join(CREDENTIALS_PATH, 'token.pickle'), 'wb') as token:
            pickle.dump(creds, token)

    return build('sheets', 'v4', credentials=creds)
