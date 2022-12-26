from src.odds.BetResults import BetResults


class BetCalculator:
    def calculate(self, nflgame):
        """Calculate bet results of the given NflGame.

        Parameters
        ----------
        nflgame : NflGame
            The NflGame, with score, odds, and bet data

        Returns
        -------
        BetResult
            Results of the bets for the given NflGame
        """
        if nflgame.score is None:
            return
        if nflgame.odds is None:
            return

        nflgame.bet_results = BetResults()
        if nflgame.odds.h2h is not None:
            nflgame.odds.h2h.bet_results = self.__calculate_h2h(nflgame)
            nflgame.bet_results += nflgame.odds.h2h.bet_results
        if nflgame.odds.spread is not None:
            nflgame.odds.spread.bet_results = self.__calculate_spread(nflgame)
            nflgame.bet_results += nflgame.odds.spread.bet_results
        if nflgame.odds.total is not None:
            nflgame.odds.total.bet_results = self.__calculate_total(nflgame)
            nflgame.bet_results += nflgame.odds.total.bet_results


    def __calculate_h2h(self, nflgame):
        """Calculate results of H2H bets made.

        Parameters
        ----------
        nflgame : NflGame
            The NflGame, with score, odds, and bet data

        Returns
        -------
        BetResults
        """
        # No odds, no h2h bet
        if nflgame.odds is None or nflgame.odds.h2h is None or nflgame.odds.h2h.bet is None:
            return BetResults(0, 0, 0, 0)

        # Push
        if (nflgame.odds.h2h.bet.away > 0 or nflgame.odds.h2h.bet.home > 0) and nflgame.score.away == nflgame.score.home:
            return BetResults(0, 0, 1, 0)

        wins = 0
        losses = 0
        net = 0
        # Bet on away team to win h2h
        if nflgame.odds.h2h.bet.away > 0:
            won_away_bet = nflgame.score.away > nflgame.score.home
            if won_away_bet:
                wins += 1
            else:
                losses += 1
            net += self.__calculate_bet_winnings(
                won_away_bet,
                nflgame.odds.h2h.price.away,
                nflgame.odds.h2h.bet.away
            )

        # Bet on home team to win h2h
        if nflgame.odds.h2h.bet.home > 0:
            won_home_bet = nflgame.odds.h2h.bet.home and nflgame.score.home > nflgame.score.away
            if won_home_bet:
                wins += 1
            else:
                losses += 1
            net += self.__calculate_bet_winnings(
                won_home_bet,
                nflgame.odds.h2h.price.home,
                nflgame.odds.h2h.bet.home
            )
        return BetResults(
            wins,
            losses,
            0,
            net
        )

    def __calculate_spread(self, nflgame):
        # No odds, no spread bet
        if nflgame.odds is None or nflgame.odds.spread is None or nflgame.odds.spread.bet is None:
            return BetResults(0, 0, 0, 0)

        # Push
        if (nflgame.odds.spread.bet.away > 0 or nflgame.odds.spread.bet.home > 0) and nflgame.score.away + nflgame.odds.spread.points.away == nflgame.score.home:
            return BetResults(0, 0, 1, 0)

        wins = 0
        losses = 0
        net = 0

        # Bet on away team to win ats
        if nflgame.odds.spread.bet.away > 0:
            won_away_bet = nflgame.score.away + \
                nflgame.odds.spread.points.away > nflgame.score.home
            if won_away_bet:
                wins += 1
            else:
                losses += 1
            net += self.__calculate_bet_winnings(
                won_away_bet,
                nflgame.odds.spread.price.away,
                nflgame.odds.spread.bet.away
            )

        # Bet on home team to win ats
        if nflgame.odds.spread.bet.home > 0:
            won_home_bet = nflgame.score.home + \
                nflgame.odds.spread.points.home > nflgame.score.away
            if won_home_bet:
                wins += 1
            else:
                losses += 1
            net += self.__calculate_bet_winnings(
                won_home_bet,
                nflgame.odds.spread.price.home,
                nflgame.odds.spread.bet.home
            )
        return BetResults(
            wins,
            losses,
            0,
            net
        )

    def __calculate_total(self, nflgame):
        # No odds, no total bet
        if nflgame.odds is None or nflgame.odds.total is None or nflgame.odds.total.bet is None:
            return BetResults(0, 0, 0, 0)

        # Push
        if (nflgame.odds.total.bet.away > 0 or nflgame.odds.total.bet.home > 0) and nflgame.score.away + nflgame.score.home == nflgame.odds.total.points:
            return BetResults(0, 0, 1, 0)

        wins = 0
        losses = 0
        net = 0

        # Bet on under
        if nflgame.odds.total.bet.away > 0:
            won_under_bet = nflgame.score.away + \
                nflgame.score.home < nflgame.odds.total.points
            if won_under_bet:
                wins += 1
            else:
                losses += 1
            net += self.__calculate_bet_winnings(
                won_under_bet,
                nflgame.odds.total.price.away,
                nflgame.odds.total.bet.away
            )

        # Bet on over
        if nflgame.odds.total.bet.home > 0:
            won_over_bet = nflgame.score.home + nflgame.score.away > nflgame.odds.total.points
            if won_over_bet:
                wins += 1
            else:
                losses += 1
            net += self.__calculate_bet_winnings(
                won_over_bet,
                nflgame.odds.total.price.home,
                nflgame.odds.total.bet.home
            )
        return BetResults(
            wins,
            losses,
            0,
            net
        )

    def __calculate_bet_winnings(self, won_bet, price, bet):
        if price == 0:
            return 0
        if not won_bet:
            return -1 * bet
        multiplier = (1 + price/100) if price > 0 else (1 - 100/price)
        return round(multiplier * bet - bet, 2)
