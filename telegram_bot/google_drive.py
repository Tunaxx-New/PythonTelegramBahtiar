import os.path
from googleapiclient.http import MediaFileUpload

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from telegram_bot.thread_with_return import ThreadWithReturn

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

service = None


"""
    Connecting to google cloud using OAuth2 module
"""


def connect_google_cloud():
    global service
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
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

    try:
        service = build('drive', 'v3', credentials=creds)
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


"""
    Getting subfolders from folder bu executing query google drive api (recursive DFS)
    @param1 folders - all folders inside google drive, it's for remove duplicates
    @param2 folder - current folder {id, name}
    
    Changing folders array of dictionaries
"""


def get_sub_folders(folders, folder):
    sub_query = f"mimeType='application/vnd.google-apps.folder' and trashed=false and parents='{folder['id']}'"
    sub_results = service.files().list(q=sub_query, fields="nextPageToken, files(id, name)").execute()
    sub_folders = []
    for f in sub_results['files']:
        f_ = {'id': f['id'], 'name': f['name']}
        sub_folders.append(f_)
        get_sub_folders(sub_folders, f_)

        if f_ in folders:
            folders.remove(f_)

    if folder in folders:
        folders[folders.index(folder)].update({'sub_folders': sub_folders})


"""
    Getting all frolders from disk and by DFS it's sub folders
    @return folders - array of folder {id, name, sub_folders:[]}
"""


def get_folders():
    query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()

    folders = [{'id': folder['id'], 'name': folder['name']} for folder in results['files']]

    for folder in folders:
        get_sub_folders(folders, folder)

    return folders


"""
    Getting array of only argument root id folder
    @return folders - array of folders {id, name}
"""


def get_folders_from_root(root_id):
    print(root_id)
    query = f"mimeType='application/vnd.google-apps.folder' and trashed=false and parents='{root_id}'"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    folders = []
    for f in results['files']:
        f_ = {'id': f['id'], 'name': f['name']}
        folders.append(f_)
    return folders


"""
    Creates folder inside google drive root id folder
    And executing callback function after creating folders
    @param1 - name - name of create folder
    @param2 - root_id - id of folder, for create inside this folder
    @param3 - callback - callback function with response and context as arguments
    @param4-5 context, update - telegram context and update
"""


def create_folder(name, root_id, callback, context, update):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [root_id]
    }

    request = service.files().create(body=file_metadata)

    thread = ThreadWithReturn(target=request.execute)
    thread.start()
    result = thread.join()
    callback(None, result, None, context, update)


"""
    @return file_metadata - metadata for sending file into google drive
"""


def get_file_metadata(file_name, id):
    if id == '':
        print('Empty folder id!')

    file_metadata = {
        'name': file_name,
        'mimeType': '*/*',
        'parents': [id]
    }

    return file_metadata


"""
    Uploading file into google drive
    @param1 file_metadata - metadata for google drive {name, mimeType, parents:[]}
    @param2 file - file for upload
    @return string of status
"""


def upload(file_metadata, file):
    media = MediaFileUpload(file.name, mimetype='*/*', resumable=True)

    f = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return f'Successfully uploaded file {file.name} (id: {f.get("id")}) into '

