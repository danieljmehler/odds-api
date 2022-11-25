from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import logging
import os


CLIENT_SECRET_JSON_FILENAME = "client_secret.json"
SCOPES = [
    'https://www.googleapis.com/auth/drive'
]
TOKEN_JSON_FILENAME = "token.json"


def get_google_api_creds():
    """Get a Google API OAuth2 Credentials object

    Returns
    -------
    Credentials
        Google API OAuth2 Credentials object
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_JSON_FILENAME):
        creds = Credentials.from_authorized_user_file(
            TOKEN_JSON_FILENAME,
            SCOPES
        )
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_JSON_FILENAME,
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_JSON_FILENAME, 'w') as token:
            token.write(creds.to_json())
    return creds


def get_files(creds):
    """Get a list of Google Sheets file objects

    Parameters
    ----------
    creds : Credentials
        Google API OAUth2 Credentials object

    Returns
    -------
    list
        List of Google Sheets file objects
    """
    service = discovery.build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10,
        fields="nextPageToken, files(id, name)").execute()
    return results.get('files', [])


def get_file(creds, filename):
    files = get_files(creds)
    matching = [file for file in files if file["name"] == filename]
    if len(matching) == 1:
        return matching[0]
    elif len(matching) == 0:
        logging.warn('No Google Sheets files named {} found.'.format(filename))
        return None
    else:
        msg = 'Multiple Google Sheets files found with the name {}. Please manually delete unneccessary files and try again.'.format(filename)
        logging.error(msg)
        raise Exception(msg)

def delete_files(creds, files=[]):
    """Delete Google Sheets files

    Parameters
    ----------
    creds : Credentials
        Google API OAUth2 Credentials object
    files : list
        List of Google Sheets file objects
    """
    service = discovery.build('drive', 'v3', credentials=creds)
    for file in files:
        try:
            service.files().delete(fileId=file["id"]).execute()
        except HttpError as error:
            logging.error('Error while deleting Google Sheets file {} ({})'.format(
                file["name"], file["id"]))
            logging.error(error)


def upload_csv(creds, sheets_filename, csv_filename):
    """Upload local CSV file to Google Sheets

    Parameters
    ----------
    creds : Credentials
        Google API OAUth2 Credentials object
    sheets_filename : string
        Filename of the Google Sheets file to be created
    csv_filename : string
        Filename of the local CSV file to upload
    
    Returns
    -------
    file
        Google Sheets file object of the file that was created
    """
    files = get_files(creds)
    files_with_same_name = [
        file for file in file if file["name"] == sheets_filename]
    if len(files_with_same_name) > 0:
        logging.warn('Found existing file(s) named {}. Files will be deleted to create new file with that name.'.format(
            sheets_filename))
        delete_files(creds, files_with_same_name)

    service = discovery.build('drive', 'v3', credentials=creds)
    file_metadata = {
        "name": sheets_filename,
        "mimeType": 'application/vnd.google-apps.spreadsheet'
    }
    media = MediaFileUpload(
        csv_filename,
        mimetype="text/csv",
        resumable=True)
    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id').execute()
    except HttpError as error:
        logging.error('Error while uploading CSV file {} to Google Sheets file {}'.format(
            csv_filename, sheets_filename))
        logging.error(error)
        file = None
    return file


def get_file_data(creds, sheets_filename):
    """Get data of a Google Sheets file as a dict

    Parameters
    ----------
    creds : Credentials
        Google API OAUth2 Credentials object
    sheets_filename : string
        Filename of the Google Sheets file
    
    Returns
    -------
    dict
        Google Sheets file data
    """
    file = get_file(creds, sheets_filename)
    service = discovery.build('sheets', 'v4', credentials=creds)
    try:
        response = service.spreadsheets().get(
            spreadsheetId=file["id"], includeGridData=True).execute()
        # data = response["sheets"][0]["data"][0]
    except HttpError as error:
        logging.error('Error while Google Sheets data from file {}'.format(sheets_filename))

    def get_formatted_value(userEnteredValue):
        if "boolValue" in userEnteredValue:
            return bool(userEnteredValue["boolValue"])
        elif "numberValue" in userEnteredValue:
            return float(userEnteredValue["numberValue"])
        else:
            return userEnteredValue["stringValue"]

    # listOfRows = []
    # for row in data["rowData"]:
    #     listOfRows.append([get_formatted_value(
    #         value["userEnteredValue"]) for value in row["values"]])

    # ret = [dict(zip(listOfRows[0], row))
    #        for row in listOfRows if row[0] != "week"]
    # with open("test/output/sheet-reduced.json", 'w') as f:
    #     json.dump(ret, f)

    return response
