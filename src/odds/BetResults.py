class BetResults:
    def __init__(self, wins=0, losses=0, pushes=0, net=0):
        self.wins = wins
        self.losses = losses
        self.pushes = pushes
        self.net = net

    def __str__(self):
        return "{}-{}-{} ${:,.2f}".format(
            self.wins,
            self.losses,
            self.pushes,
            self.net
        )