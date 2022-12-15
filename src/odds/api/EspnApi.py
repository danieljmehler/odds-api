import logging
import requests

class EspnApi:
    """Methods for interacting with the ESPN API and working with the data."""

    NFL_SCOREBOARD_URL = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'

    def get_week_data(self, week=None) -> dict:
        logging.debug('Querying ESPN for data')
        response = requests.get(
            '{}{}'.format(
                self.NFL_SCOREBOARD_URL,
                '?week={}'.format(week) if week is not None else ''
            )
        )
        return response.json()