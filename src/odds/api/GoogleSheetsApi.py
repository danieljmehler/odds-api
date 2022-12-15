from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import json
import logging
import os


class GoogleSheetsApi:

    CLIENT_SECRET_JSON_FILENAME = "client_secret.json"
    SCOPES = [
        'https://www.googleapis.com/auth/drive'
    ]
    TOKEN_JSON_FILENAME = "token.json"

    def get_google_api_creds(self):
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
        if os.path.exists(self.TOKEN_JSON_FILENAME):
            creds = Credentials.from_authorized_user_file(
                self.TOKEN_JSON_FILENAME,
                self.SCOPES
            )
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRET_JSON_FILENAME,
                    self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.TOKEN_JSON_FILENAME, 'w') as token:
                token.write(creds.to_json())
        return creds

    def get_files(self, creds):
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
            pageSize=20,
            fields="nextPageToken, files(id, name)").execute()
        return results.get('files', [])

    def get_file(self, creds, filename):
        files = self.get_files(creds)
        logging.debug("Retrieved Google Sheets file: {}".format(files))
        matching = [file for file in files if file["name"] == filename]
        if len(matching) == 1:
            return matching[0]
        elif len(matching) == 0:
            logging.warning(
                'No Google Sheets files named {} found.'.format(filename))
            return None
        else:
            msg = 'Multiple Google Sheets files found with the name {}. Please manually delete unneccessary files and try again.'.format(
                filename)
            logging.error(msg)
            raise Exception(msg)

    def delete_files(self, creds, files=[]):
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

    def upload_csv(self, creds, sheets_filename, csv_filename):
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
        files = self.get_files(creds)
        files_with_same_name = [
            file for file in files if file["name"] == sheets_filename]
        if len(files_with_same_name) > 0:
            logging.warning('Found existing file(s) named {}. Files will be deleted to create new file with that name.'.format(
                sheets_filename))
            self.delete_files(creds, files_with_same_name)

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
                fields='id, name').execute()
        except HttpError as error:
            logging.error('Error while uploading CSV file {} to Google Sheets file {}'.format(
                csv_filename, sheets_filename))
            logging.error(error)
            file = None
        return file

    def get_file_data(self, creds, sheets_filename, transform=False):
        """Get data of a Google Sheets file as a dict

        Parameters
        ----------
        creds : Credentials
            Google API OAUth2 Credentials object
        sheets_filename : string
            Filename of the Google Sheets file
        transform : bool (default: False)
            Whether to try to transform the data into a dict, using the first row
            of each sheet as keys

        Returns
        -------
        dict
            Google Sheets file data
        """
        # Add localfilename
        # If it exists and not force, get data from local file
        # Else, get from API
        file = self.get_file(creds, sheets_filename)
        logging.debug("Retrieved Google Sheets file: {}".format(file))
        service = discovery.build('sheets', 'v4', credentials=creds)
        try:
            response = service.spreadsheets().get(
                spreadsheetId=file["id"], includeGridData=True).execute()
        except HttpError as error:
            logging.error(
                'Error while Google Sheets data from file {}'.format(sheets_filename))

        def get_formatted_value(userEnteredValue):
            if "boolValue" in userEnteredValue:
                return bool(userEnteredValue["boolValue"])
            elif "numberValue" in userEnteredValue:
                return float(userEnteredValue["numberValue"])
            else:
                return userEnteredValue["stringValue"]

        data = {"sheets": []}
        for sheet in response["sheets"]:
            data_sheet = {
                "title": sheet["properties"]["title"],
                "rows": []
            }
            for row in sheet["data"][0]["rowData"]:
                data_sheet["rows"].append([get_formatted_value(
                    value["userEnteredValue"]) for value in row["values"] if "userEnteredValue" in value])
            data["sheets"].append(data_sheet)

        if transform:
            for sheet in data["sheets"]:
                # for each in r in sheet.rows
                # r is a list, the values in the row
                # create a dict
                # The dict keys are sheet.rows[0] values
                # The dict values are r values
                sheet["rows"] = [{sheet["rows"][0][idx]: col for idx, col in enumerate(
                    row)} for row in sheet["rows"][1:]]

        return data
