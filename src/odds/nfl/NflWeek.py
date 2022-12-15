from datetime import datetime, timezone
import logging
import requests
from src.odds.api.TheOddsApi import TheOddsApi
from src.odds.api.EspnApi import EspnApi
from src.odds.nfl.NflGame import HomeAway, NflGame


class NflWeek:
    """Interact with the ESPN API to get NFL schedule and score info"""

    DATE_FORMAT = "%Y-%m-%dT%H:%MZ"

    def __init__(self, week=None, espn_data=None, odds_data=None):
        if espn_data is None:
            espn = EspnApi()
            espn_data = espn.get_week_data(week)
        self.week = week or espn_data["week"]["number"]
        regular_season_calendar = [calendar for calendar in espn_data["leagues"]
                                   [0]["calendar"] if calendar["label"] == "Regular Season"][0]
        this_week_entry = [entry for entry in regular_season_calendar["entries"]
                           if entry["value"] == str(self.week)][0]
        self.start_date = self.__get_datetime(this_week_entry["startDate"])
        self.end_date = self.__get_datetime(this_week_entry["endDate"])
        self.games = self.__initialize_games(espn_data["events"], odds_data)

    def __str__(self):
        return "\n".join(map(str, sorted(self.games, key=lambda x: x.date)))

    def __get_datetime(self, event_date) -> datetime:
        """Convert date string from ESPN API data to a datetime

        Parameters
        ----------
        event_date : str
            Date field of an ESPN API response object

        Returns
        -------
        datetime
            The given date converted to a datetime object in UTC
        """
        return datetime.strptime(event_date, self.DATE_FORMAT).replace(tzinfo=timezone.utc)

    def __initialize_games(self, events, odds=None) -> list:
        if odds is None:
            theoddsapi = TheOddsApi()
            odds = theoddsapi.get_odds_data(self)
        games = []
        for event in events:
            address = event["competitions"][0]["venue"]["address"]
            g = NflGame(
                event["week"]["number"],
                self.__get_datetime(event["date"]),
                address["city"] if "state" not in address else '{}, {}'.format(
                    address["city"], address["state"]),  # TODO: expand to include indoor/outdoor
                HomeAway(
                    [competitor["team"]["displayName"] for competitor in event["competitions"]
                        [0]["competitors"] if competitor["homeAway"] == "away"][0],
                    [competitor["team"]["displayName"] for competitor in event["competitions"]
                        [0]["competitors"] if competitor["homeAway"] == "home"][0]
                )
            )
            g.set_score(event["competitions"][0])
            odds_events = [odds_event for odds_event in odds if odds_event["home_team"]
                           == g.teams.home and odds_event["away_team"] == g.teams.away]
            if len(odds_events) > 0:
                g.set_odds(odds_events[0])
            games.append(g)
        return games

    def to_csv(self):
        return [game.to_csv() for game in self.games]

    def set_bets(self, bet_data):
        for game in self.games:
            game_bet_data = next(iter([event for event in bet_data if event["away_team"]
                                 == game.teams.away and event["home_team"] == game.teams.home]), None)
            game.set_bets(game_bet_data)

    def set_bet_results(self, events):
        for game in self.games:
            game_event_data = next(iter([event for event in events if event["name"][:event["name"].index(
                ' at ')] == game.teams.away and event["name"][event["name"].index(' at ') + 4:] == game.teams.home]), None)
            game.set_bet_results(game_event_data)
            
