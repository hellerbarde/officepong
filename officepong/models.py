"""
Database schema.
"""
from datetime import datetime
from time import time
from quart import current_app
from tortoise import Model, fields


class Player(Model):
    """
    A player is a user with an ELO score.
    """
    name = fields.CharField(256, pk=True)
    elo = fields.FloatField()
    games = fields.IntField()

    def __init__(self, name=None, elo=None, games=None):
        super().__init__(
            name=name,
            elo=current_app.config["ELO_START_VALUE"],
            games=0
        )

    def __repr__(self):
        return "%s-%i-%i" % (self.name, self.elo, self.games)


class Match(Model):
    """
    A match is a game, it can have multiple winners and losers, and a
    a score for the winners and losers.
    """

    timestamp = fields.IntField(pk=True)
    winners = fields.CharField(1024)
    losers = fields.CharField(1024)
    win_score = fields.IntField()
    lose_score = fields.IntField()
    actual = fields.FloatField()
    expected = fields.FloatField()
    delta = fields.FloatField()

    def __init__(self, timestamp=None, winners=None, losers=None, win_score=None, lose_score=None , actual=None, expected=None, delta=None):
        super().__init__(
            timestamp = int(time()),
            winners = winners,
            losers = losers,
            win_score = win_score,
            lose_score = lose_score,
            actual = actual,
            expected = expected,
            delta = delta
        )

    def __repr__(self):
        return "%i %s:%s (%i:%i) %i" % (self.timestamp, self.winners, self.losers,
                                        self.win_score, self.lose_score, self.delta)

