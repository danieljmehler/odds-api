import json
import os
import shutil
import src.odds.nfl.util as util


def test_create_game_info_london():
    odds_game = {
        "id": "0c056485fc7897af7947e667069e420b",
        "sport_key": "americanfootball_nfl",
        "sport_title": "NFL",
        "commence_time": "2022-10-30T13:30:00Z",
        "home_team": "Jacksonville Jaguars",
        "away_team": "Denver Broncos"
    }
    event = {
        "id": "401435641",
        "uid": "s:20~l:28~e:401435641",
        "date": "2022-10-30T13:30Z",
        "name": "Denver Broncos at Jacksonville Jaguars",
        "shortName": "DEN @ JAX",
        "season": {
            "year": 2022,
            "type": 2,
            "slug": "regular-season"
        },
        "week": {
            "number": 8
        },
        "competitions": [
            {
                "id": "401435641",
                "uid": "s:20~l:28~e:401435641~c:401435641",
                "date": "2022-10-30T13:30Z",
                "attendance": 86215,
                "type": {
                    "id": "1",
                    "abbreviation": "STD"
                },
                "timeValid": True,
                "neutralSite": True,
                "conferenceCompetition": False,
                "recent": False,
                "venue": {
                    "id": "2455",
                    "fullName": "Wembley Stadium",
                    "address": {
                        "city": "London"
                    },
                    "capacity": 86000,
                    "indoor": False
                }
            }
        ]
    }
    game_info = util.create_game_info(8, odds_game, event)
    assert game_info["week"] == 8
    assert game_info["date"] == "2022-10-30"
    assert game_info["time"] == "01:30 PM"
    assert game_info["location"] == "London"
    assert game_info["away_team"] == "Denver Broncos"
    assert game_info["home_team"] == "Jacksonville Jaguars"


def test_create_game_info_us():
    odds_game = {
        "id": "fbef1db7e3116a12749166bf3f1e0d64",
        "sport_key": "americanfootball_nfl",
        "sport_title": "NFL",
        "commence_time": "2022-10-30T17:00:00Z",
        "home_team": "Minnesota Vikings",
        "away_team": "Arizona Cardinals"
    }
    event = {
        "id": "401437809",
        "uid": "s:20~l:28~e:401437809",
        "date": "2022-10-30T17:00Z",
        "name": "Arizona Cardinals at Minnesota Vikings",
        "shortName": "ARI @ MIN",
        "season": {
            "year": 2022,
            "type": 2,
            "slug": "regular-season"
        },
        "week": {
            "number": 8
        },
        "competitions": [
            {
                "id": "401437809",
                "uid": "s:20~l:28~e:401437809~c:401437809",
                "date": "2022-10-30T17:00Z",
                "attendance": 66742,
                "type": {
                    "id": "1",
                    "abbreviation": "STD"
                },
                "timeValid": True,
                "neutralSite": False,
                "conferenceCompetition": False,
                "recent": True,
                "venue": {
                    "id": "5239",
                    "fullName": "U.S. Bank Stadium",
                    "address": {
                        "city": "Minneapolis",
                        "state": "MN"
                    },
                    "capacity": 66468,
                    "indoor": True
                }
            }
        ]
    }
    game_info = util.create_game_info(8, odds_game, event)
    assert game_info["week"] == 8
    assert game_info["date"] == "2022-10-30"
    assert game_info["time"] == "05:00 PM"
    assert game_info["location"] == "Minneapolis, MN"
    assert game_info["away_team"] == "Arizona Cardinals"
    assert game_info["home_team"] == "Minnesota Vikings"

def test_create_odds_info():
    odds_game = {
        "id": "fbef1db7e3116a12749166bf3f1e0d64",
        "sport_key": "americanfootball_nfl",
        "sport_title": "NFL",
        "commence_time": "2022-10-30T17:00:00Z",
        "home_team": "Minnesota Vikings",
        "away_team": "Arizona Cardinals",
        "bookmakers": [
            {
                "key": "fanduel",
                "title": "FanDuel",
                "last_update": "2022-10-29T15:05:30Z",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {
                                "name": "Arizona Cardinals",
                                "price": 154
                            },
                            {
                                "name": "Minnesota Vikings",
                                "price": -184
                            }
                        ]
                    },
                    {
                        "key": "spreads",
                        "outcomes": [
                            {
                                "name": "Arizona Cardinals",
                                "price": -110,
                                "point": 3.5
                            },
                            {
                                "name": "Minnesota Vikings",
                                "price": -110,
                                "point": -3.5
                            }
                        ]
                    },
                    {
                        "key": "totals",
                        "outcomes": [
                            {
                                "name": "Over",
                                "price": -115,
                                "point": 48.5
                            },
                            {
                                "name": "Under",
                                "price": -105,
                                "point": 48.5
                            }
                        ]
                    }
                ]
            }
        ]
    }
    event = {
        "id": "401437809",
        "uid": "s:20~l:28~e:401437809",
        "date": "2022-10-30T17:00Z",
        "name": "Arizona Cardinals at Minnesota Vikings",
        "shortName": "ARI @ MIN",
        "season": {
            "year": 2022,
            "type": 2,
            "slug": "regular-season"
        },
        "week": {
            "number": 8
        },
        "competitions": [
            {
                "id": "401437809",
                "uid": "s:20~l:28~e:401437809~c:401437809",
                "date": "2022-10-30T17:00Z",
                "attendance": 66742,
                "type": {
                    "id": "1",
                    "abbreviation": "STD"
                },
                "timeValid": True,
                "neutralSite": False,
                "conferenceCompetition": False,
                "recent": True,
                "venue": {
                    "id": "5239",
                    "fullName": "U.S. Bank Stadium",
                    "address": {
                        "city": "Minneapolis",
                        "state": "MN"
                    },
                    "capacity": 66468,
                    "indoor": True
                },
                "competitors": [
                    {
                        "winner": True,
                        "team": {
                            "displayName": "Minnesota Vikings",
                        },
                        "score": "34"
                    },
                    {
                        "winner": False,
                        "team": {
                            "displayName": "Arizona Cardinals",
                        },
                        "score": "26"
                    }
                ]
            }
        ]
    }
    odds_info = util.create_odds_info(8, odds_game, event)
    assert odds_info["week"] == 8
    assert odds_info["away_team"] == "Arizona Cardinals"
    assert odds_info["away_team_score"] == 26
    assert odds_info["away_team_h2h_price"] == 154
    assert not odds_info["away_team_h2h_bet"]
    assert odds_info["home_team"] == "Minnesota Vikings"
    assert odds_info["home_team_score"] == 34
    assert odds_info["home_team_h2h_price"] == -184
    assert not odds_info["home_team_h2h_bet"]
    assert odds_info["away_team_spread"] == 3.5
    assert odds_info["away_team_spread_price"] == -110
    assert not odds_info["away_team_spread_bet"]
    assert odds_info["home_team_spread"] == -3.5
    assert odds_info["home_team_spread_price"] == -110
    assert not odds_info["home_team_spread_bet"]
    assert odds_info["over_under"] == 48.5
    assert odds_info["over_price"] == -115
    assert not odds_info["over_bet"]
    assert odds_info["under_price"] == -105
    assert not odds_info["under_bet"]


def test_aggregate_data():
    with open('test/resources/odds.json', 'r') as f:
        odds_data = json.load(f)
    with open('test/resources/scores.json', 'r') as f:
        score_data = json.load(f)
    games, odds = util.aggregate_data(8, odds_data, score_data)
    assert len(games) == 15


def test_write_csvs():
    with open('test/resources/odds.json', 'r') as f:
        odds_data = json.load(f)
    with open('test/resources/scores.json', 'r') as f:
        score_data = json.load(f)
    games, odds = util.aggregate_data(8, odds_data, score_data)
    assert len(games) == 15
    assert len(odds) == 15
    path = os.path.join('test', 'output')
    try:
        shutil.rmtree(path)
    except Exception as e:
        raise e
    finally:
        os.mkdir(path)
    util.write_csvs(games, odds, 'test/output/test_game_info.csv', 'test/output/test_odds_info.csv')


# def test_list_google_drive_files():
#     creds = util.get_google_api_creds()
#     util.list_google_drive_files(creds)


# def test_upload_csv_to_google_sheets():
#     creds = util.get_google_api_creds()
#     util.upload_csv_to_google_sheets(creds, "odds-api", "test/output/test_game_info.csv")


def test_get_dates_for_week_1():
    start_date, end_date = util.get_dates_for_week(1)
    assert start_date.strftime("%Y-%m-%dT%H:%MZ") == "2022-09-08T07:00Z"
    assert end_date.strftime("%Y-%m-%dT%H:%MZ") == "2022-09-14T06:59Z"


def test_get_dates_for_week_11():
    start_date, end_date = util.get_dates_for_week(11)
    assert start_date.strftime("%Y-%m-%dT%H:%MZ") == "2022-11-16T08:00Z"
    assert end_date.strftime("%Y-%m-%dT%H:%MZ") == "2022-11-23T07:59Z"


# def test_get_odds_for_week():
#     odds_json = util.get_odds_for_week(11)
#     assert len(odds_json) == 13


# def test_delete_google_sheets_file():
#     creds = util.get_google_api_creds()
#     files = util.get_google_sheets_files(creds, "odds-api")
#     util.delete_google_sheets_files(creds, files)


# def test_get_google_sheet_data():
#     creds = util.get_google_api_creds()
#     util.get_google_sheet_data(creds, 'odds-api-week11-bets')

def test_calculate_bet_winnings():
    assert util.calculate_bet_winnings(False, -110, 100) == -100
    assert util.calculate_bet_winnings(False, 0, 100) == 0
    assert util.calculate_bet_winnings(False, 115, 100) == -100
    assert util.calculate_bet_winnings(True, -110, 100) == 90.91
    assert util.calculate_bet_winnings(True, 0, 100) == 0
    assert util.calculate_bet_winnings(True, 115, 100) == 115


def test_calculate_h2h_bet_winnings_home_win():
    game = {
        "away_team_score": 10,
        "home_team_score": 13,
        "away_team_h2h_price": -110,
        "home_team_h2h_price": 115,
        "away_team_h2h_bet": 0,
        "home_team_h2h_bet": 100
    }
    assert util.calculate_h2h_bet_winnings(game) == 115

def test_calculate_h2h_bet_winnings_home_lose():
    game = {
        "away_team_score": 13,
        "home_team_score": 10,
        "away_team_h2h_price": -110,
        "home_team_h2h_price": 115,
        "away_team_h2h_bet": 0,
        "home_team_h2h_bet": 100
    }
    assert util.calculate_h2h_bet_winnings(game) == -100

def test_calculate_h2h_bet_winnings_away_win():
    game = {
        "away_team_score": 13,
        "home_team_score": 10,
        "away_team_h2h_price": -110,
        "home_team_h2h_price": 115,
        "away_team_h2h_bet": 100,
        "home_team_h2h_bet": 0
    }
    assert util.calculate_h2h_bet_winnings(game) == 90.91

def test_calculate_h2h_bet_winnings_away_lose():
    game = {
        "away_team_score": 10,
        "home_team_score": 13,
        "away_team_h2h_price": -110,
        "home_team_h2h_price": 115,
        "away_team_h2h_bet": 100,
        "home_team_h2h_bet": 0
    }
    assert util.calculate_h2h_bet_winnings(game) == -100

def test_calculate_h2h_bet_winnings_push():
    game = {
        "away_team_score": 13,
        "home_team_score": 13,
        "away_team_h2h_price": -110,
        "home_team_h2h_price": 115,
        "away_team_h2h_bet": 100,
        "home_team_h2h_bet": 0
    }
    assert util.calculate_h2h_bet_winnings(game) == 0


def test_calculate_spread_bet_winnings_away_win():
    game = {
        "away_team_score": 14,
        "away_team_spread": -3.5,
        "home_team_score": 10,
        "home_team_spread": 3.5,
        "away_team_spread_price": -110,
        "home_team_spread_price": 115,
        "away_team_spread_bet": 100,
        "home_team_spread_bet": 0
    }
    assert util.calculate_spread_bet_winnings(game) == 90.91

def test_calculate_spread_bet_winnings_away_lose():
    game = {
        "away_team_score": 13,
        "away_team_spread": -3.5,
        "home_team_score": 10,
        "home_team_spread": 3.5,
        "away_team_spread_price": -110,
        "home_team_spread_price": 115,
        "away_team_spread_bet": 100,
        "home_team_spread_bet": 0
    }
    assert util.calculate_spread_bet_winnings(game) == -100

def test_calculate_spread_bet_winnings_home_win():
    game = {
        "away_team_score": 13,
        "away_team_spread": -3.5,
        "home_team_score": 10,
        "home_team_spread": 3.5,
        "away_team_spread_price": -110,
        "home_team_spread_price": 115,
        "away_team_spread_bet": 0,
        "home_team_spread_bet": 100
    }
    assert util.calculate_spread_bet_winnings(game) == 115

def test_calculate_spread_bet_winnings_home_lost():
    game = {
        "away_team_score": 17,
        "away_team_spread": -3.5,
        "home_team_score": 10,
        "home_team_spread": 3.5,
        "away_team_spread_price": -110,
        "home_team_spread_price": 115,
        "away_team_spread_bet": 0,
        "home_team_spread_bet": 100
    }
    assert util.calculate_spread_bet_winnings(game) == -100

def test_calculate_spread_bet_winnings_push():
    game = {
        "away_team_score": 13,
        "away_team_spread": -3,
        "home_team_score": 10,
        "home_team_spread": 3,
        "away_team_spread_price": -110,
        "home_team_spread_price": 115,
        "away_team_spread_bet": 0,
        "home_team_spread_bet": 100
    }
    assert util.calculate_spread_bet_winnings(game) == 0


def test_calculate_totals_bet_winnings_over_win():
    game = {
        "away_team_score": 14,
        "home_team_score": 10,
        "over_under": 23.5,
        "over_price": -110,
        "under_price": 115,
        "over_bet": 100,
        "under_bet": 0
    }
    assert util.calculate_totals_bet_winnings(game) == 90.91

def test_calculate_totals_bet_winnings_over_lose():
    game = {
        "away_team_score": 13,
        "home_team_score": 10,
        "over_under": 23.5,
        "over_price": -110,
        "under_price": 115,
        "over_bet": 100,
        "under_bet": 0
    }
    assert util.calculate_totals_bet_winnings(game) == -100

def test_calculate_totals_bet_winnings_under_win():
    game = {
        "away_team_score": 13,
        "home_team_score": 10,
        "over_under": 23.5,
        "over_price": -110,
        "under_price": 115,
        "over_bet": 0,
        "under_bet": 100
    }
    assert util.calculate_totals_bet_winnings(game) == 115

def test_calculate_totals_bet_winnings_under_lose():
    game = {
        "away_team_score": 14,
        "home_team_score": 10,
        "over_under": 23.5,
        "over_price": -110,
        "under_price": 115,
        "over_bet": 0,
        "under_bet": 100
    }
    assert util.calculate_totals_bet_winnings(game) == -100

def test_calculate_totals_bet_winnings_push():
    game = {
        "away_team_score": 14,
        "home_team_score": 10,
        "over_under": 24,
        "over_price": -110,
        "under_price": 115,
        "over_bet": 100,
        "under_bet": 0
    }
    assert util.calculate_totals_bet_winnings(game) == 0