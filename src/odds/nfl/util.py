import csv
from datetime import datetime, timezone
import json
import logging
import os
import requests
import src.odds.api.espn as espn
import TheOddsApi as odds


def aggregate_data(week, odds_data, score_data):
    games = []
    odds_infos = []
    for event in score_data["events"]:
        logging.debug('Getting event data for game {}'.format(event["name"]))
        odds_games = [odds_game for odds_game in odds_data if event["name"] == (odds_game["away_team"] + " at " + odds_game["home_team"])]
        if len(odds_games) < 1:
            logging.debug('Did not find match for {}'.format(event["name"]))
            odds_game = {
                "commence_time": datetime.strptime(event["date"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "home_team": event["name"][event["name"].index(' at ') + 4:],
                "away_team": event["name"][:event["name"].index(' at ')],
                "bookmakers": []
            }
        else:
            odds_game = odds_games[0]
        game_info = create_game_info(week, odds_game, event)
        odds_info = create_odds_info(week, odds_game, event)
        games.append(game_info)
        odds_infos.append(odds_info)
    return games, odds_infos


def create_game_info_data(espn_data):
    data = []
    for event in espn_data["events"]:
        address = event["competitions"][0]["venue"]["address"]
        event_date = espn.get_datetime(event["date"]).astimezone()
        game = {
            "week": espn_data["week"]["number"],
            "date": event_date.strftime("%Y-%m-%d"),
            "time": event_date.strftime("%I:%M %p"),
            "location": address["city"] if "state" not in address else '{}, {}'.format(address["city"], address["state"]),
            "home_team": event["name"][event["name"].index(' at ') + 4:],
            "away_team": event["name"][:event["name"].index(' at ')]
        }
        data.append(game)
    return data


def create_odds_info_data(week, odds_data):
    data = []
    for event in odds_data:
        h2h_market = get_market(event, "h2h")
        spreads_market = get_market(event, "spreads")
        totals_market = get_market(event, "totals")
        game = {
            "week": week,
            "away_team": event["away_team"],
            "away_team_h2h_price": 0 if h2h_market is None else get_outcome(h2h_market, event["away_team"])["price"],
            "away_team_h2h_bet": 0,
            "home_team": event["home_team"],
            "home_team_h2h_price": 0 if h2h_market is None else  get_outcome(h2h_market, event["home_team"])["price"],
            "home_team_h2h_bet": 0,
            "away_team_spread": 0 if spreads_market is None else get_outcome(spreads_market, event["away_team"])["point"],
            "away_team_spread_price": 0 if spreads_market is None else get_outcome(spreads_market, event["away_team"])["price"],
            "away_team_spread_bet": 0,
            "home_team_spread": 0 if spreads_market is None else get_outcome(spreads_market, event["home_team"])["point"],
            "home_team_spread_price": 0 if spreads_market is None else get_outcome(spreads_market, event["home_team"])["price"],
            "home_team_spread_bet": 0,
            "over_under": 0 if totals_market is None else get_outcome(totals_market, "Over")["point"],
            "over_price": 0 if totals_market is None else get_outcome(totals_market, "Over")["price"],
            "over_bet": 0,
            "under_price": 0 if totals_market is None else get_outcome(totals_market, "Under")["price"],
            "under_bet": 0
        }
        data.append(game)
    return data

def get_market(odds_game, key):
    if len(odds_game["bookmakers"]) > 0:
        return [market for market in odds_game["bookmakers"][0]["markets"] if market["key"] == key][0]
    return None


def get_outcome(market, name):
    if market is not None:
        return [outcome for outcome in market["outcomes"] if outcome["name"] == name][0]
    return None


def write_csv(data, filename):
    if os.path.dirname(filename) != '':
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)





def add_scores_to_bet_data(bet_data, score_data):
    updated_bet_data = []
    for game in bet_data:
        score_game = [event for event in score_data["events"] if event["name"] == '{} at {}'.format(game["away_team"], game["home_team"])][0]
        away_score = [competitor["score"] for competitor in score_game["competitions"][0]["competitors"] if competitor["team"]["displayName"] == game["away_team"]][0]
        home_score = [competitor["score"] for competitor in score_game["competitions"][0]["competitors"] if competitor["team"]["displayName"] == game["home_team"]][0]
        game["away_team_score"] = int(away_score)
        game["home_team_score"] = int(home_score)
        updated_bet_data.append(game)

    return updated_bet_data


def calculate_bet_winnings(won_bet, price, bet):
    if price == 0:
        return 0, [0, 0, 0]
    if not won_bet:
        return -1 * bet, [0, 1, 0]
    multiplier = (1 + price/100) if price > 0 else (1 - 100/price)
    return round(multiplier * bet - bet, 2), [1, 0, 0]

def calculate_h2h_bet_winnings(game):
    net_winnings = 0
    wlt = [0, 0, 0]

    # If a push
    if game["away_team_score"] == game["home_team_score"]:
        return 0, [0, 0, 1]

    away_bet_winnings, away_wlt = calculate_bet_winnings(
        game["away_team_score"] > game["home_team_score"],
        game["away_team_h2h_price"],
        game["away_team_h2h_bet"]
    )
    

    net_winnings += away_bet_winnings
    net_winnings += calculate_bet_winnings(
        game["home_team_score"] > game["away_team_score"],
        game["home_team_h2h_price"],
        game["home_team_h2h_bet"]
    )
    return net_winnings


def calculate_spread_bet_winnings(game):
    net_winnings = 0

    # If a push
    if game["away_team_score"] + game["away_team_spread"] == game["home_team_score"]:
        return 0

    net_winnings += calculate_bet_winnings(
        game["away_team_score"] + game["away_team_spread"] > game["home_team_score"],
        game["away_team_spread_price"],
        game["away_team_spread_bet"]
    )
    net_winnings += calculate_bet_winnings(
        game["home_team_score"] + game["home_team_spread"] > game["away_team_score"],
        game["home_team_spread_price"],
        game["home_team_spread_bet"]
    )
    return net_winnings


def calculate_totals_bet_winnings(game):
    net_winnings = 0

    # If a push
    if game["away_team_score"] + game["home_team_score"] == game["over_under"]:
        return 0

    net_winnings += calculate_bet_winnings(
        game["away_team_score"] + game["home_team_score"] > game["over_under"],
        game["over_price"],
        game["over_bet"]
    )
    net_winnings += calculate_bet_winnings(
        game["away_team_score"] + game["home_team_score"] < game["over_under"],
        game["under_price"],
        game["under_bet"]
    )
    return net_winnings


def calculate_bet_results(bet_data):
    for idx, game in enumerate(bet_data):
        net_winnings = 0
        net_winnings += calculate_h2h_bet_winnings(game)
        net_winnings += calculate_spread_bet_winnings(game)
        net_winnings += calculate_totals_bet_winnings(game)
        bet_data[idx]["net_winnings"] = net_winnings
    with open("test/output/bet_results.json", 'w') as f:
        json.dump(bet_data, f)