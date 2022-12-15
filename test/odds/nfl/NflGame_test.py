from datetime import date
import json

from src.odds.nfl.NflGame import HomeAway, NflGame


class TestNflGame:

    competition_final = {
        "status": {
            "type": {
                "id": 3
            }
        },
        "competitors": [
            {
                "homeAway": "away",
                "score": 31
            },
            {
                "homeAway": "home",
                "score": 30
            }
        ]
    }
    competition_inprogress = {
        "status": {
            "type": {
                "id": 1
            }
        },
        "competitors": [
            {
                "homeAway": "away",
                "score": 10
            },
            {
                "homeAway": "home",
                "score": 24
            }
        ]
    }
    odds_event = {
        "bookmakers": [
            {
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {
                                "name": "Team A",
                                "price": 160
                            },
                            {
                                "name": "Team H",
                                "price": -190
                            }
                        ]
                    },
                    {
                        "key": "spreads",
                        "outcomes": [
                            {
                                "name": "Team A",
                                "price": -110,
                                "point": 3.5
                            },
                            {
                                "name": "Team H",
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
                                "price": -112,
                                "point": 40.5
                            },
                            {
                                "name": "Under",
                                "price": -108,
                                "point": 40.5
                            }
                        ]
                    }
                ]
            }
        ]
    }
    bet_data = {
        "week": 12,
        "away_team": "Team A",
        "away_team_h2h_price": 160,
        "away_team_h2h_bet": 100,
        "home_team": "Team H",
        "home_team_h2h_price": -190,
        "home_team_h2h_bet": 50,
        "away_team_spread": 3.5,
        "away_team_spread_price": -110,
        "away_team_spread_bet": 150,
        "home_team_spread": -3.5,
        "home_team_spread_price": -110,
        "home_team_spread_bet": 200,
        "over_under": 40.5,
        "over_price": -112,
        "over_bet": 1000,
        "under_price": -108,
        "under_bet": 1500
    }

    def test_set_score_final(self):
        nflgame = NflGame(
            12,
            date.today(),
            "Location",
            HomeAway("Team A", "Team H")
        )
        
        nflgame.set_score(self.competition_final)
        assert nflgame.score.home == 30
        assert nflgame.score.away == 31
    
    def test_set_score_inprogress(self):
        nflgame = NflGame(
            12,
            date.today(),
            "Location",
            HomeAway("Team A", "Team H")
        )
        
        nflgame.set_score(self.competition_inprogress)
        assert nflgame.score is None

    def test_set_odds(self):
        nflgame = NflGame(
            12,
            date.today(),
            "Location",
            HomeAway("Team A", "Team H")
        )

        nflgame.set_odds(self.odds_event)
        assert nflgame.odds.h2h.price.away == 160
        assert nflgame.odds.h2h.price.home == -190
        assert nflgame.odds.spread.price.away == -110
        assert nflgame.odds.spread.price.home == -110
        assert nflgame.odds.spread.points.away == 3.5
        assert nflgame.odds.spread.points.home == -3.5
        assert nflgame.odds.total.price.away == -108
        assert nflgame.odds.total.price.home == -112
        assert nflgame.odds.total.points == 40.5


    def test_set_bets(self):
        nflgame = NflGame(
            12,
            date.today(),
            "Location",
            HomeAway("Team A", "Team H")
        )

        nflgame.set_odds(self.odds_event)
        nflgame.set_bets(self.bet_data)
        assert nflgame.odds.h2h.bet.away == self.bet_data["away_team_h2h_bet"]
        assert nflgame.odds.h2h.bet.home == self.bet_data["home_team_h2h_bet"]
        assert nflgame.odds.spread.bet.away == self.bet_data["away_team_spread_bet"]
        assert nflgame.odds.spread.bet.home == self.bet_data["home_team_spread_bet"]
        assert nflgame.odds.total.bet.away == self.bet_data["under_bet"]
        assert nflgame.odds.total.bet.home == self.bet_data["over_bet"]