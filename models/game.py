"""Game.py - This file contains the class definitions for the Datastore
entities used by the Game. Because this class is also a regular Python
classes it can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from fractions import Fraction
from protorpc import messages
from google.appengine.ext import ndb
from score import Score

WORDS = ['Python', 'HTML', 'CSS', 'JavaScript', 'PHP', 'MySQL']

class Game(ndb.Model):
    """Game object"""
    target_word = ndb.StringProperty(required=True)
    current_word = ndb.StringProperty(required=True)
    guess_history = ndb.StringProperty(required=True)
    attempts_allowed = ndb.IntegerProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True, default=6)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user, attempts):
    	"""Creates and returns a new game"""
    	word_to_guess = random.choice(WORDS)
        current_word = '-' * len(word_to_guess)
    	game = Game(user=user,
                    target_word=word_to_guess,
                    current_word=current_word,
                    guess_history='',
                    attempts_allowed=attempts,
                    attempts_remaining=attempts,
                    game_over=False)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.current_word = self.current_word
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.message = message
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        user = self.user.get()
        self.game_over = True
        if won == True:
            user.games_won += 1
            self.current_word = self.target_word
        else:
            user.games_lost += 1

        try:
            total_games = user.games_won + user.games_lost
            win_loss = Fraction(user.games_won, total_games)
        except ZeroDivisionError:
            win_loss = Fraction(user.games_won, 1)
        user.win_loss = float(win_loss)
        user.put()
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        score.put()

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    attempts = messages.IntegerField(2, default=6)

class MakeMoveForm(messages.Message):
    """Used to guess a letter or word in an existing game"""
    guess = messages.StringField(1, required=True)
    word_guess =  messages.BooleanField(2, required=True)

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    current_word = messages.StringField(2, required=True)
    attempts_remaining = messages.IntegerField(3, required=True)
    game_over = messages.BooleanField(4, required=True)
    message = messages.StringField(6, required=True)
    user_name = messages.StringField(7, required=True)

class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)

class HistoryForm(messages.Message):
    """HistoryForm-- outbound (single) string message"""
    Guess = messages.StringField(1, required=True)
    Result = messages.StringField(2, required=True)

class HistoryForms(messages.Message):
    """Returns multiple GuessMessage"""
    history = messages.MessageField(HistoryForm, 1, repeated=True)