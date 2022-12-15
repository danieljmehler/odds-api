
from datetime import datetime, timezone
import json
import logging
import os
import requests


COMMENCE_TIME_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

class TheOddsApi:
    """Methods for interacting with The Odds API and working with the data."""

    def get_odds_api_token(self, api_token_filename='./odds-api-token.txt') -> str:
        """Gets the contents of the given file, which is assumed to be an API token for The Odds API

        Parameters
        ----------
        api_token_filename : str, optional
            Path to a file which contains an API token for The Odds API (default: "./odds-api-token.txt")

        Returns
        -------
        str
            Contents of the given file, which is assumed to be an API token for The Odds API
        """

        with open(api_token_filename, 'r') as f:
            contents = f.read()
        return contents


    def get_datetime(self, commence_time) -> datetime:
        """Convert commence_time string from The Odds API data to a datetime

        Parameters
        ----------
        commence_time : str
            commence_time field of a The Odds API response object

        Returns
        -------
        datetime
            The given commence_time converted to a datetime object in UTC
        """
        return datetime.strptime(commence_time, COMMENCE_TIME_DATE_FORMAT).replace(tzinfo=timezone.utc)


    def get_odds_data(self, nflweek=None) -> dict:
        """Get The Odds API odds data for the given week. Return the data as a dict, and also write the JSON to a local file.

        Parameters
        ----------
        nflweek : NflWeek, optional
            The week for which to get odds data (default is to return all odds data)

        Returns
        -------
        dict
            JSON odds data from The Odds API for the given week
        """
        logging.debug('Querying The Odds API for odds data')
        API_KEY = self.get_odds_api_token()
        # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports
        SPORT = 'americanfootball_nfl'
        # uk | us | eu | au. Multiple can be specified if comma delimited
        REGIONS = 'us'
        # h2h | spreads | totals. Multiple can be specified if comma delimited
        MARKETS = 'h2h,spreads,totals'
        # decimal | american
        ODDS_FORMAT = 'american'
        # iso | unix
        DATE_FORMAT = 'iso'
        # Comma-separated list of bookmakers to be returned. If both bookmakers and regions are specified, bookmakers takes priority.
        BOOKMAKERS = "fanduel"
        response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds', params={
            'api_key': API_KEY,
            'regions': REGIONS,
            'markets': MARKETS,
            'oddsFormat': ODDS_FORMAT,
            'dateFormat': DATE_FORMAT,
            'bookmakers': BOOKMAKERS
        })
        odds_json = response.json()

        if nflweek is None:
            return odds_json

        logging.debug('Filter odds data for dates {}-{}'.format(nflweek.start_date, nflweek.end_date))
        def date_filter(game):
            commence_date = self.get_datetime(game["commence_time"])
            return commence_date > nflweek.start_date and commence_date < nflweek.end_date
        return [game for game in odds_json if date_filter(game)]
