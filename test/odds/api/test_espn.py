from datetime import datetime, timezone
import os
import random
import shutil
import src.odds.api.espn as espn
import string

class TestEspn:

    output_directory = None

    def setup_method(self):
        date = datetime.now(timezone.utc)
        rstr = ''.join(random.choices(string.ascii_lowercase, k=8))
        self.output_directory = './test/output/{}_{}'.format(date.strftime("%Y-%m-%d"), rstr)
        os.makedirs(self.output_directory)
    
    def teardown_method(self):
        shutil.rmtree(self.output_directory)
        self.output_directory = None

    def test_get_espn_data(self):
        filename = '{}/scoreboard.json'.format(self.output_directory)
        data = espn.get_espn_data(None, filename)
        assert os.path.isfile(filename)
        assert "leagues" in data
        assert "events" in data
        data2 = espn.get_espn_data(None, filename)
        assert "leagues" in data2
        assert "events" in data2
        assert data == data2

    def test_get_week(self):
        date = datetime.strptime("2022-11-25", "%Y-%m-%d").replace(tzinfo=timezone.utc)
        filename = '{}/scoreboard.json'.format(self.output_directory)
        week = espn.get_week(date, filename)
        assert week == 12

    def test_get_week_dates(self):
        filename = '{}/scoreboard.json'.format(self.output_directory)
        start_date, end_date = espn.get_week_dates(1, filename)
        expected_start_date = datetime.strptime("2022-09-08T07:00Z", "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
        expected_end_date = datetime.strptime("2022-09-14T06:59Z", "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
        assert start_date == expected_start_date
        assert end_date == expected_end_date