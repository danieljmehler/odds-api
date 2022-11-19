import json
import src.odds.nfl.util as util

def test_aggregate_data():
    with open('test/resources/odds.json', 'r') as f:
        odds_data = json.load(f)
    with open('test/resources/scores.json', 'r') as f:
        score_data = json.load(f)
    games = util.aggregate_data(odds_data, score_data)
    assert len(games) == 14
    expected_fields = [
        "date",
        "time",
        "location",
        "away_team",
        "home_team"
    ]
    for game in games:
        for field in expected_fields:
            assert field in game