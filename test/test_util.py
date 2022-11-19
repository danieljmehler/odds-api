import json
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
    odds_info = util.create_odds_info(8, odds_game)
    assert odds_info["week"] == 8
    assert odds_info["away_team"] == "Arizona Cardinals"
    assert odds_info["away_team_h2h_price"] == 154
    assert odds_info["home_team"] == "Minnesota Vikings"
    assert odds_info["home_team_h2h_price"] == -184
    assert odds_info["away_team_spread"] == 3.5
    assert odds_info["away_team_spread_price"] == -110
    assert odds_info["home_team_spread"] == -3.5
    assert odds_info["home_team_spread_price"] == -110
    assert odds_info["over_under"] == 48.5
    assert odds_info["over_price"] == -115
    assert odds_info["under_price"] == -105


def test_aggregate_data():
    with open('test/resources/odds.json', 'r') as f:
        odds_data = json.load(f)
    with open('test/resources/scores.json', 'r') as f:
        score_data = json.load(f)
    games, odds = util.aggregate_data(8, odds_data, score_data)
    assert len(games) == 14