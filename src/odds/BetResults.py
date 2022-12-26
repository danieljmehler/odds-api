class BetResults:
    def __init__(self, wins=0, losses=0, pushes=0, net=0):
        self.wins = wins
        self.losses = losses
        self.pushes = pushes
        self.net = net

    def __str__(self):
        return "{}-{}-{} {}".format(
            self.wins,
            self.losses,
            self.pushes,
            self.__format_dollar(self.net)
        )
    
    def __add__(self, other):
        if self is None:
            return BetResults()
        if other is None:
            return self
        return BetResults(
            self.wins + other.wins,
            self.losses + other.losses,
            self.pushes + other.pushes,
            self.net + other.net
        )
    
    def __radd__(self, other):
        if self is None:
            return BetResults()
        if other is None:
            return self
        if other == 0:
            return self
        else:
            return self.__add__(other)
    
    def __format_dollar(self, number):
        return "{}${:,.2f}".format(
            '-' if number < 0 else '',
            abs(number)
        )
