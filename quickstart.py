from __future__ import print_function
import pickle
import os.path
import random
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next runon
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    folders = get_all_folders(service)

    print("%d folders found" % len(folders))

    colors = get_colors(service)

    for folder in folders:
        set_random_color(service, folder, colors)

def get_all_folders(service):
    page_token = None
    folders = []
    # Call the Drive v3 API
    while True:
        results = service.files().list(q="mimeType='application/vnd.google-apps.folder'",
                                   fields="nextPageToken, files(id, name)",
                                   pageToken=page_token).execute()
        items = results.get('files', [])
        folders += items
        page_token = results.get('nextPageToken', None)
        if page_token is None:
            break

    return folders

def get_metadata(service, id):
    Get metadata
    metadata = service.files().get(fileId=id, fields='*').execute()
    return metadata


def get_colors(service):
    results = service.about().get(fields='folderColorPalette').execute()

    return results.get('folderColorPalette', None)

def set_random_color(service, folder, colors):
    id = folder['id']
    color = random.choice(colors)
    update = {'folderColorRgb':color}

    print("Changing the color of folder %s to %s" % (folder['name'], color))

    result = service.files().update(fileId=id, body=update).execute()

    return result


if __name__ == '__main__':
    main()
