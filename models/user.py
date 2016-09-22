"""User.py - This file contains the class definitions for the Datastore
entities used by the User. Because this class is also a regular Python
classes it can include methods (such as 'to_form' and 'new_game')."""

from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    games_won = ndb.IntegerProperty(required=True, default=0)
    games_lost = ndb.IntegerProperty(required=True, default=0)
    win_loss = ndb.FloatProperty(required=True, default=0.0)

    def to_rank_form(self):
        form = RankForm()
        form.user_name = self.name
        form.games_won = self.games_won
        form.games_lost = self.games_lost
        form.win_loss = self.win_loss
        return form


class RankForm(messages.Message):
    """RankForm for outbound User information"""
    user_name = messages.StringField(1, required=True)
    games_won = messages.IntegerField(2, required=True)
    games_lost = messages.IntegerField(3, required=True)
    win_loss = messages.FloatField(4, required=True)


class RankForms(messages.Message):
    """Return multiple RankForms"""
    items = messages.MessageField(RankForm, 1, repeated=True)
