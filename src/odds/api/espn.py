from datetime import datetime, timezone
import json
import logging
import os
import requests


EVENT_DATE_FORMAT = "%Y-%m-%dT%H:%MZ"
NFL_SCOREBOARD_URL = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'


def get_datetime(event_date) -> datetime:
    """Convert event date string from ESPN API data to a datetime

    Parameters
    ----------
    event_date : str
        Date field of an ESPN API response event object

    Returns
    -------
    datetime
        The given event date converted to a datetime object in UTC
    """
    return datetime.strptime(event_date, EVENT_DATE_FORMAT).replace(tzinfo=timezone.utc)

def get_espn_data(week=None, espn_json_filename=None, force=False):
    """Get scores for the games of an NFL schedule week

    Parameters
    ----------
    week : int, optional
        NFL schedule week for which to get scores (default is the next week for which all games have not been played)
    espn_json_filename : str, optional
        Filename of a JSON file containing ESPN API data. If provided, data will be taken from this file instead of querying the ESPN API (default: "./scoreboard_weekX.json")
    force : boolean, optional
        If True, always gets data from API, instead of from local cache file.

    Returns
    -------
    dict
        ESPN API NFL scoreboard data
    """
    # Set default filename
    if espn_json_filename is None:
        espn_json_filename = './output/scoreboard_week{}.json'.format(week if week else '')

    # Read data from file if provided
    if os.path.isfile(espn_json_filename) and not force:
        logging.debug('Getting ESPN data from {}'.format(espn_json_filename))
        with open(espn_json_filename, 'r') as f:
            return json.load(f)

    logging.debug('Querying ESPN for data')
    response = requests.get('{}{}'.format(NFL_SCOREBOARD_URL, '?week={}'.format(week) if week is not None else ''))
    data = response.json()

    # Create directories
    os.makedirs(os.path.dirname(espn_json_filename), exist_ok=True)

    # Write to file
    logging.debug('Writing ESPN data to file '.format(espn_json_filename))
    with open(espn_json_filename, 'w') as f:
        json.dump(data, f)

    return data


def get_week(date=None, espn_json_filename=None):
    """Get NFL schedule week for the given date

    Parameters
    ----------
    date : datetime, optional
        Date for which to get the NFL schedule week (default: datetime.now())
    espn_json_filename : str, optional
        Filename of a JSON file containing ESPN API data. If provided, data will be taken from this file instead of querying the ESPN API

    Returns
    -------
    int
        The NFL schedule week under which the date falls
    """
    if not date:
        date = datetime.now(timezone.utc)
    logging.debug('Getting the NFL schedule week for date {}'.format(date))
    data = get_espn_data(None, espn_json_filename)

    regular_season_calendar = [calendar for calendar in data["leagues"]
                               [0]["calendar"] if calendar["label"] == "Regular Season"][0]

    def date_filter(entry):
        start_date = get_datetime(entry["startDate"])
        end_date = get_datetime(entry["endDate"])
        return date >= start_date and date < end_date
    return [int(entry["value"]) for entry in regular_season_calendar["entries"] if date_filter(entry)][0]


def get_week_dates(week=None, espn_json_filename=None):
    """Get start and end date of an NFL schedule week

    Parameters
    ----------
    week : int, optional
        NFL schedule week for which to get the start and end dates (default is the next week for which all games have not been played)
    espn_json_filename : str, optional
        Filename of a JSON file containing ESPN API data. If provided, data will be taken from this file instead of querying the ESPN API

    Returns
    -------
    datetime
        The start date of the NFL schedule week
    datetime
        The end date of the NFL schedule week
    """
    if week is None:
        week = get_week()
    logging.debug('Getting start and ends dates of NFL schedule week {}'.format(week))
    data = get_espn_data(week, espn_json_filename)

    regular_season_calendar = [calendar for calendar in data["leagues"]
                               [0]["calendar"] if calendar["label"] == "Regular Season"][0]
    week_entry = [entry for entry in regular_season_calendar["entries"]
                  if entry["value"] == str(week)][0]
    start_date = datetime.strptime(
        week_entry["startDate"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
    end_date = datetime.strptime(
        week_entry["endDate"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
    return start_date, end_date
