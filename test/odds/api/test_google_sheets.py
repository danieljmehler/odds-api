import csv
from datetime import datetime, timezone
import os
import random
import shutil
import src.odds.api.google_sheets as gsheets
import string

class TestTheOddsApi:

    output_directory = None

    def setup_method(self):
        date = datetime.now(timezone.utc)
        rstr = ''.join(random.choices(string.ascii_lowercase, k=8))
        self.output_directory = './test/output/{}_{}'.format(date.strftime("%Y-%m-%d"), rstr)
        os.makedirs(self.output_directory)
    
    def teardown_method(self):
        shutil.rmtree(self.output_directory)
        self.output_directory = None
    
    def test_get_google_api_creds(self):
        creds = gsheets.get_google_api_creds()
        assert creds is not None
    
    def test_get_files(self):
        creds = gsheets.get_google_api_creds()
        files = gsheets.get_files(creds)
        assert len(files) > 0
        for file in files:
            assert "name" in file
            assert "id" in file
    
    def test_get_file(self):
        creds = gsheets.get_google_api_creds()
        file = gsheets.get_file(creds, "Job Applications")
        assert file is not None
        assert "id" in file
        assert "name" in file
    
    def test_upload_csv(self):
        filename = "test-filename"
        data = [
            {
                "id": "abc123",
                "author": "Stephen King",
                "title": "The Stand",
                "publisher": "Penguin",
                "pages": 1012,
                "read": True
            },
            {
                "id": "fde456",
                "author": "Stephen King",
                "title": "Carrie",
                "publisher": "Penguin",
                "pages": 899,
                "read": False
            }
        ]
        with open('{}/{}.csv'.format(self.output_directory, filename), 'w', newline='') as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        creds = gsheets.get_google_api_creds()
        uploaded_file = gsheets.upload_csv(creds, filename, '{}/{}.csv'.format(self.output_directory, filename))
        gsheets_data_raw = gsheets.get_file_data(creds, filename)
        gsheets_data = [dict(zip(gsheets_data_raw["sheets"][0]["rows"][0], row)) for row in gsheets_data_raw["sheets"][0]["rows"] if row[0] != "id"]
        assert data == gsheets_data
        gsheets.delete_files(creds, [uploaded_file])
        assert gsheets.get_file(creds, filename) == None
    