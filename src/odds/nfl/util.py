import csv
from datetime import datetime, timezone
import logging


def aggregate_data(odds_data, score_data):
    games = []
    for odds_game in odds_data:
        logging.debug('Getting event data for game {} at {}'.format(odds_game["away_team"], odds_game["home_team"]))
        events = [event for event in score_data["events"] if event["name"] == (odds_game["away_team"] + " at " + odds_game["home_team"])]
        if len(events) < 1:
            logging.debug('Did not find match for {} at {}'.format(odds_game["away_team"], odds_game["home_team"]))
            continue
        score_game = events[0]
        date = datetime.strptime(odds_game["commence_time"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        address = score_game["competitions"][0]["venue"]["address"]
        game = {
            "date": date.strftime("%Y-%m-%d"),
            "time": date.strftime("%I:%M %p"),
            "location": address["city"] if "state" not in address else '{}, {}'.format(address["city"], address["state"]),
            "away_team": odds_game["away_team"],
            "home_team": odds_game["home_team"]
        }
        games.append(game)
    return games

def write_csv(data, filepath):
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = [
            "week",
            "start_date",
            "end_date",
            "game_id",
            "game_date",
            "game_time",
            "location",
            "away_team",
            "home_team"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)