import logging

from src.odds.BetCalculator import BetCalculator
from src.odds.BetResults import BetResults


class NflGame:

    def __init__(
        self,
        week,
        date,
        location,  # TODO: expand to include indoor/outdoor
        teams
    ):
        self.week = week
        self.date = date
        self.location = location
        self.teams = teams
        self.score = None
        self.odds = None
        self.bet_results = None

    def __str__(self):
        game_info = "Week {} ({})\n{}{} at {}{}".format(
            self.week,
            self.date.strftime("%Y-%m-%d %I:%M %p"),
            self.teams.away,
            ' {}'.format(self.score.away) if self.score else '',
            self.teams.home,
            ' {}'.format(self.score.home) if self.score else ''
        )
        return "{}\n{}\nResults: {}".format(game_info, self.odds, self.bet_results)

    def set_score(self, competition):
        if int(competition["status"]["type"]["id"]) == 3:
            self.score = HomeAway(
                int([competitor["score"] for competitor in competition["competitors"]
                    if competitor["homeAway"] == "away"][0]),
                int([competitor["score"] for competitor in competition["competitors"]
                    if competitor["homeAway"] == "home"][0])
            )

    def set_odds(self, odds_event):
        logging.debug('Setting odds for event: '.format(odds_event))
        # H2H
        h2h_market = next(iter([market for market in odds_event["bookmakers"]
                          [0]["markets"] if market["key"] == "h2h"]), None)
        h2h = None
        if h2h_market:
            h2h = H2HOdds(
                HomeAway(
                    next(iter([outcome["price"] for outcome in h2h_market["outcomes"]
                               if outcome["name"] == self.teams.away]), None),
                    next(iter([outcome["price"] for outcome in h2h_market["outcomes"]
                               if outcome["name"] == self.teams.home]), None)
                )
            )

        # Spreads
        spread_market = next(iter([market for market in odds_event["bookmakers"]
                                   [0]["markets"] if market["key"] == "spreads"]), None)
        spread = None
        if spread_market:
            # Get spread outcomes
            away_spread_outcome = next(iter([
                outcome for outcome in spread_market["outcomes"] if outcome["name"] == self.teams.away]), None)
            home_spread_outcome = next(iter([
                outcome for outcome in spread_market["outcomes"] if outcome["name"] == self.teams.home]), None)
            spread = SpreadOdds(
                HomeAway(
                    away_spread_outcome["point"],
                    home_spread_outcome["point"]
                ),
                HomeAway(
                    away_spread_outcome["price"],
                    home_spread_outcome["price"]
                )
            )

        # Totals
        total_market = next(iter([market for market in odds_event["bookmakers"]
                                  [0]["markets"] if market["key"] == "totals"]), None)
        total = None
        if total_market:
            over_outcome = next(iter([
                outcome for outcome in total_market["outcomes"] if outcome["name"] == "Over"]), None)
            under_outcome = next(iter([
                outcome for outcome in total_market["outcomes"] if outcome["name"] == "Under"]), None)
            # Create TotalOdds
            total = TotalOdds(
                under_outcome["point"],
                HomeAway(
                    under_outcome["price"],
                    over_outcome["price"]
                )
            )

        self.odds = NflGameOdds(h2h, spread, total)

    def __set_odds(self, bet_data):
        h2h = H2HOdds(
            HomeAway(
                bet_data["away_team_h2h_price"],
                bet_data["home_team_h2h_price"]
            )
        )
        spread = SpreadOdds(
            HomeAway(
                bet_data["away_team_spread"],
                bet_data["home_team_spread"]
            ),
            HomeAway(
                bet_data["away_team_spread_price"],
                bet_data["home_team_spread_price"]
            )
        )
        total = TotalOdds(
            bet_data["over_under"],
            HomeAway(
                bet_data["under_price"],
                bet_data["over_price"]
            )
        )
        self.odds = NflGameOdds(h2h, spread, total)

    def set_bets(self, bet_data):
        if not bet_data:
            logging.debug("Cannot set bets. No bet data.")
            return
        if not self.odds:
            logging.debug("Setting odds data from bet data.")
            self.__set_odds(bet_data)
        if self.odds.h2h:
            logging.debug("Setting H2H bets.")
            self.odds.h2h.bet = HomeAway(
                bet_data.get("away_team_h2h_bet", 0),
                bet_data.get("home_team_h2h_bet", 0)
            )
            logging.debug("Set H2H bets: {}".format(self.odds.h2h.bet))
        else:
            logging.debug("Cannot set H2H bets. No H2H odds.")
        if self.odds.spread:
            logging.debug("Setting ATS bets.")
            self.odds.spread.bet = HomeAway(
                bet_data.get("away_team_spread_bet", 0),
                bet_data.get("home_team_spread_bet", 0)
            )
            logging.debug("Set ATS bets: {}".format(self.odds.spread.bet))
        if self.odds.total:
            self.odds.total.bet = HomeAway(
                bet_data.get("under_bet", 0),
                bet_data.get("over_bet", 0)
            )

    def set_bet_results(self, event):
        self.set_score(event["competitions"][0])
        bc = BetCalculator()
        bc.calculate(self)

    def to_csv(self) -> dict:
        return {
            "week": self.week,
            "away_team": self.teams.away,
            "away_team_h2h_price": self.odds.h2h.price.away if self.odds and self.odds.h2h and self.odds.h2h.price and self.odds.h2h.price.away else 0,
            "away_team_h2h_bet": self.odds.h2h.bet.away if self.odds and self.odds.h2h and self.odds.h2h.bet and self.odds.h2h.bet.away else 0,
            "home_team": self.teams.home,
            "home_team_h2h_price": self.odds.h2h.price.home if self.odds and self.odds.h2h and self.odds.h2h.price and self.odds.h2h.price.home else 0,
            "home_team_h2h_bet": self.odds.h2h.bet.home if self.odds and self.odds.h2h and self.odds.h2h.bet and self.odds.h2h.bet.home else 0,
            "away_team_spread": self.odds.spread.points.away if self.odds and self.odds.spread and self.odds.spread.points and self.odds.spread.points.away else None,
            "away_team_spread_price": self.odds.spread.price.away if self.odds and self.odds.spread and self.odds.spread.price and self.odds.spread.price.away else 0,
            "away_team_spread_bet": self.odds.spread.bet.away if self.odds and self.odds.spread and self.odds.spread.bet and self.odds.spread.bet.away else 0,
            "home_team_spread": self.odds.spread.points.home if self.odds and self.odds.spread and self.odds.spread.points and self.odds.spread.points.home else None,
            "home_team_spread_price": self.odds.spread.price.home if self.odds and self.odds.spread and self.odds.spread.price and self.odds.spread.price.home else 0,
            "home_team_spread_bet": self.odds.spread.bet.home if self.odds and self.odds.spread and self.odds.spread.bet and self.odds.spread.bet.home else 0,
            "over_under": self.odds.total.points if self.odds and self.odds.total and self.odds.total.points and self.odds.total.points else None,
            "over_price": self.odds.total.price.home if self.odds and self.odds.total and self.odds.total.price and self.odds.total.price.home else 0,
            "over_bet": self.odds.total.bet.home if self.odds and self.odds.total and self.odds.total.bet and self.odds.total.bet.home else 0,
            "under_price": self.odds.total.price.away if self.odds and self.odds.total and self.odds.total.price and self.odds.total.price.away else 0,
            "under_bet": self.odds.total.bet.away if self.odds and self.odds.total and self.odds.total.bet and self.odds.total.bet.away else 0
        }


class HomeAway:
    def __init__(self, away=None, home=None):
        self.away = away
        self.home = home

    def __str__(self):
        return "away {} | home {}".format(self.away, self.home)


class H2HOdds:
    def __init__(self, price=HomeAway(), bet=HomeAway(), bet_results=BetResults()):
        self.price = price
        self.bet = bet
        self.bet_results = bet_results

    def __str__(self):
        return "{}{} | {}{}{}".format(
            self.price.away,
            " ${:,.2f}".format(self.bet.away) if self.bet.away > 0 else "",
            self.price.home,
            " ${:,.2f}".format(self.bet.home) if self.bet.home > 0 else "",
            " | Results: {}".format(
                self.bet_results) if self.bet.home > 0 or self.bet.away > 0 else ""
        )


class SpreadOdds:
    def __init__(self, points=None, price=HomeAway(), bet=HomeAway(), bet_results=BetResults()):
        self.price = price
        self.points = points
        self.bet = bet
        self.bet_results = bet_results

    def __str__(self):
        return "{} ({}){} | {} ({}){}{}".format(
            self.points.away,
            self.price.away,
            " ${:,.2f}".format(self.bet.away) if self.bet.away > 0 else "",
            self.points.home,
            self.price.home,
            " ${:,.2f}".format(self.bet.home) if self.bet.home > 0 else "",
            " | Results: {}".format(
                self.bet_results) if self.bet.home > 0 or self.bet.away > 0 else ""
        )


class TotalOdds:
    def __init__(self, points=None, price=HomeAway(), bet=HomeAway(), bet_results=BetResults()):
        # price.away = under
        # price.home = over
        self.price = price
        self.points = points
        # bet.away = under bet
        # bet.home = over bet
        self.bet = bet
        self.bet_results = bet_results

    def __str__(self):
        return "{} | U {}{} | O {}{}{}".format(
            self.points,
            self.price.away,
            " ${:,.2f}".format(self.bet.away) if self.bet.away > 0 else "",
            self.price.home,
            " ${:,.2f}".format(self.bet.home) if self.bet.home > 0 else "",
            " | Results: {}".format(
                self.bet_results) if self.bet.home > 0 or self.bet.away > 0 else ""
        )


class NflGameOdds:
    def __init__(self, h2h, spread, total):
        self.h2h = h2h
        self.spread = spread
        self.total = total

    def __str__(self):
        return "H2H: {}\nATS: {}\nO/U: {}".format(
            self.h2h,
            self.spread,
            self.total
        )
