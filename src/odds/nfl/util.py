import csv
from datetime import datetime, timezone
import logging


def aggregate_data(week, odds_data, score_data):
    games = []
    odds_infos = []
    for odds_game in odds_data:
        logging.debug('Getting event data for game {} at {}'.format(odds_game["away_team"], odds_game["home_team"]))
        events = [event for event in score_data["events"] if event["name"] == (odds_game["away_team"] + " at " + odds_game["home_team"])]
        if len(events) < 1:
            logging.debug('Did not find match for {} at {}'.format(odds_game["away_team"], odds_game["home_team"]))
            continue
        game_info = create_game_info(week, odds_game, events[0])
        odds_info = create_odds_info(week, odds_game)
        games.append(game_info)
        odds_infos.append(odds_info)
    return games, odds_infos


def create_game_info(week, odds_game, score_game):
    date = datetime.strptime(odds_game["commence_time"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    address = score_game["competitions"][0]["venue"]["address"]
    game = {
        "week": week,
        "date": date.strftime("%Y-%m-%d"),
        "time": date.strftime("%I:%M %p"),
        "location": address["city"] if "state" not in address else '{}, {}'.format(address["city"], address["state"]),
        "away_team": odds_game["away_team"],
        "home_team": odds_game["home_team"]
    }
    return game


def create_odds_info(week, odds_game):
    h2h_market = get_market(odds_game, "h2h")
    spreads_market = get_market(odds_game, "spreads")
    totals_market = get_market(odds_game, "totals")
    odds_info = {
        "week": week,
        "away_team": odds_game["away_team"],
        "away_team_h2h_price": get_outcome(h2h_market, odds_game["away_team"])["price"],
        "away_team_h2h_bet": False,
        "home_team": odds_game["home_team"],
        "home_team_h2h_price": get_outcome(h2h_market, odds_game["home_team"])["price"],
        "home_team_h2h_bet": False,
        "away_team_spread": get_outcome(spreads_market, odds_game["away_team"])["point"],
        "away_team_spread_price": get_outcome(spreads_market, odds_game["away_team"])["price"],
        "away_team_spread_bet": False,
        "home_team_spread": get_outcome(spreads_market, odds_game["home_team"])["point"],
        "home_team_spread_price": get_outcome(spreads_market, odds_game["home_team"])["price"],
        "home_team_spread_bet": False,
        "over_under": get_outcome(totals_market, "Over")["point"],
        "over_price": get_outcome(totals_market, "Over")["price"],
        "over_bet": False,
        "under_price": get_outcome(totals_market, "Under")["price"],
        "under_bet": False
    }
    return odds_info


def get_market(odds_game, key):
    return [market for market in odds_game["bookmakers"][0]["markets"] if market["key"] == key][0]


def get_outcome(market, name):
    return [outcome for outcome in market["outcomes"] if outcome["name"] == name][0]


def write_csvs(game_data, odds_data, game_filepath, odds_filepath):
    with open(game_filepath, 'w', newline='') as csvfile:
        game_fieldnames = game_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=game_fieldnames)
        writer.writeheader()
        writer.writerows(game_data)
    with open(odds_filepath, 'w', newline='') as csvfile:
        odds_fieldnames = odds_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=odds_fieldnames)
        writer.writeheader()
        writer.writerows(odds_data)