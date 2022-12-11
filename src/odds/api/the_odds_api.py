
"""Methods for interacting with The Odds API and working with the data."""

from datetime import datetime, timezone
import src.odds.api.espn as espn
import json
import logging
import os
import requests


COMMENCE_TIME_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def get_odds_api_token(api_token_filename='./odds-api-token.txt') -> str:
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


def get_datetime(commence_time) -> datetime:
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


def get_odds_data(week=None, odds_json_filename=None, espn_json_filename=None) -> dict:
    """Get The Odds API odds data for the given week. Return the data as a dict, and also write the JSON to a local file.

    Parameters
    ----------
    week : int, optional
        The week for which to get odds data (default is the next week for which all games have not been played)
    odds_json_filename : str, optional
        Filename to which odds JSON data will be saved. If this file already exists, data will be retrieved from this file instead of from the API (default: "./output/odds_weekX.json").

    Returns
    -------
    dict
        JSON odds data from The Odds API for the given week
    """
    if not week:
        week = espn.get_week(None, espn_json_filename)

    # Set default filename
    if not odds_json_filename:
        odds_json_filename = './output/odds_week{}.json'.format(week)

    # If odds JSON file already exists, return its data
    if os.path.isfile(odds_json_filename):
        logging.debug('Getting odds data from {}'.format(odds_json_filename))
        with open(odds_json_filename, 'r') as f:
            return json.load(f)

    logging.debug('Querying The Odds API for odds data')
    API_KEY = get_odds_api_token()
    # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports
    SPORT = 'americanfootball_nfl'
    REGIONS = 'us'  # uk | us | eu | au. Multiple can be specified if comma delimited
    # h2h | spreads | totals. Multiple can be specified if comma delimited
    MARKETS = 'h2h,spreads,totals'
    ODDS_FORMAT = 'american'  # decimal | american
    DATE_FORMAT = 'iso'  # iso | unix
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

    # Filter odds data by the week we want
    start_date, end_date = espn.get_week_dates(week, espn_json_filename)
    logging.debug('Filter odds data for dates {}-{}'.format(start_date, end_date))

    def date_filter(game):
        commence_date = get_datetime(game["commence_time"])
        return commence_date > start_date and commence_date < end_date
    week_data = [game for game in odds_json if date_filter(game)]

    # Write to file
    logging.debug('Writing odds data to file '.format(odds_json_filename))
    with open(odds_json_filename, 'w') as f:
        json.dump(week_data, f)

    # Return JSON object
    return week_data
