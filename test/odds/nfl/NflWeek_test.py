from datetime import datetime, timezone
from src.odds.nfl.NflWeek import NflWeek


class TestNflWeek:

    espn_data = {
        "leagues": [
            {
                "calendar": [
                    {
                        "label": "Regular Season",
                        "entries": [
                            {
                                "label": "Week 12",
                                "value": "12",
                                "startDate": "2022-11-23T08:00Z",
                                "endDate": "2022-11-30T07:59Z"
                            }
                        ]
                    }
                ]
            }
        ],
        "events": [
            {
                "date": "2022-11-24T17:30Z",
                "name": "Team A at Team H",
                "shortName": "A @ H",
                "week": {
                    "number": 12
                },
                "competitions": [
                    {
                        "status": {
                            "type": {
                                "id": 3
                            }
                        },
                        "venue": {
                            "address": {
                                "city": "City",
                                "state": "ST"
                            }
                        },
                        "competitors": [
                            {
                                "homeAway": "away",
                                "score": 31,
                                "team": {
                                    "displayName": "Team A"
                                }
                            },
                            {
                                "homeAway": "home",
                                "score": 30,
                                "team": {
                                    "displayName": "Team H"
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }

    odds_data = [
        {
            "home_team": "Team H",
            "away_team": "Team A",
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
    ]

    def test_init(self):
        nflweek = NflWeek(12, self.espn_data, self.odds_data)
        assert nflweek.week == 12
        assert nflweek.start_date == datetime.strptime("2022-11-23T08:00Z", nflweek.DATE_FORMAT).replace(tzinfo=timezone.utc)
        assert nflweek.end_date == datetime.strptime("2022-11-30T07:59Z", nflweek.DATE_FORMAT).replace(tzinfo=timezone.utc)
        assert len(nflweek.games) == 1
        assert nflweek.games[0].week == 12
        assert nflweek.games[0].date == datetime.strptime("2022-11-24T17:30Z", nflweek.DATE_FORMAT).replace(tzinfo=timezone.utc)
        assert nflweek.games[0].location == "City, ST"
        assert nflweek.games[0].teams.away == "Team A"
        assert nflweek.games[0].teams.home == "Team H"
        assert nflweek.games[0].score.home == 30
        assert nflweek.games[0].score.away == 31
        assert nflweek.games[0].odds.h2h.price.away == 160
        assert nflweek.games[0].odds.h2h.price.home == -190
        assert nflweek.games[0].odds.spread.price.away == -110
        assert nflweek.games[0].odds.spread.price.home == -110
        assert nflweek.games[0].odds.spread.points.away == 3.5
        assert nflweek.games[0].odds.spread.points.home == -3.5
        assert nflweek.games[0].odds.total.price.away == -108
        assert nflweek.games[0].odds.total.price.home == -112
        assert nflweek.games[0].odds.total.points == 40.5
