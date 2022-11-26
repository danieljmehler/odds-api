from datetime import datetime, timezone
import os
import random
import shutil
import src.odds.api.espn as espn
import src.odds.api.the_odds_api as odds
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
    
    def test_get_odds_api_token(self):
        assert len(odds.get_odds_api_token()) == 32
    
    def test_get_odds_data(self):
        espn_filename = '{}/scoreboard.json'.format(self.output_directory)
        odds_filename = '{}/odds.json'.format(self.output_directory)
        data = odds.get_odds_data(None, odds_filename, espn_filename)
        assert len(data) > 0
        data2 = odds.get_odds_data(None, odds_filename, espn_filename)
        assert data == data2