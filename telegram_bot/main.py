from __future__ import print_function
from google_drive import upload
from google_drive import connect_google_cloud
from google_drive import get_file_metadata
from google_drive import create_folder

from telegram_commands import initialize


"""
    This function is bridge between telegram bot and google drive (independent to each other)
"""


def upload_google(file_name, folder_id):
    with open(f'files/{file_name}', 'rb') as file:
        return upload(get_file_metadata(file_name, folder_id), file)


def create_folder_google(name, root_id, callback, context, update):
    create_folder(name, root_id, callback, context, update)


def get_sub_folders(root_id):
    from google_drive import get_folders_from_root
    return get_folders_from_root(root_id)


def get_folders():
    from google_drive import get_folders
    return get_folders()


"""
    Connect to google cloud and initialize telegram bot
"""


if __name__ == '__main__':
    connect_google_cloud()
    initialize()
