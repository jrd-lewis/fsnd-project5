# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import json
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import *
from utils import get_by_urlsafe

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),)
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1))
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
HIGH_SCORES_REQUEST = endpoints.ResourceContainer(number_of_results=messages.IntegerField(1, default=10))

@endpoints.api(name='hangman', version='v1')
class HangmanApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:
        	game = Game.new_game(user.key, request.attempts)
       	except:
       		raise endpoints.BadRequestException('Could not start '
                                                'new game!')
        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_average_attempts')
       	return game.to_form('Good luck playing Hangman!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')     

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
      """Makes a move. Returns a game state with message"""
      game = get_by_urlsafe(request.urlsafe_game_key, Game)
      if game.game_over:
        return game.to_form('Game already over!')
      game.attempts_remaining -= 1
      # Checks if it the type of request is set to be a letter or word
      if request.word_guess:
        # Makes sure the current word wasn't guessed already
        if game.guess_history.find('"%s"' % request.guess.lower()) != -1:
          msg = 'Word already guessed!'
        else:
          # Compares the two words and sets the state and message accordingly
          if request.guess.lower() == game.target_word.lower():
            game.current_word = game.target_word
            game.end_game(True)
            msg = 'You win!'
          else:
            msg = 'Incorrect word!'
            # If it's not the right word and there are no more attempts, the game will end
            if game.attempts_remaining < 1:
              game.end_game(False)
              msg += ' Game over!'
      else:
        # Makes sure the current letter wasn't guessed already
        if game.guess_history.find(': "' + request.guess.lower()) != -1:
          msg = 'Letter already guessed!'
        else:
          temp_word = ''
          letters_found = 0
          i = 0
          try:
            assert (len(request.guess) == 1)
          except:
            raise endpoints.BadRequestException('Only a single letter is'
                                                ' allowed to be guessed!')
          # Go through letter by letter to see how many matches there are
          # and where the matches are in the word.
          while i < len(game.target_word):
            if game.current_word[i] == '-':
              if game.target_word[i].lower() == request.guess.lower():
                temp_word += game.target_word[i]
                letters_found += 1
              else:
                temp_word += '-'
            else:
              temp_word += game.current_word[i]
            i += 1

          msg = str(letters_found) + ' %s\'s Found.' % request.guess
          game.current_word = temp_word
          # Sets the message and state if the current word matches
          if game.current_word.lower() == game.target_word.lower():
            game.current_word = game.target_word
            game.end_game(True)
            msg = 'You win!'
          # Sets the message and state if the user couldn't guess the word within the attempt limit
          if game.attempts_remaining < 1:
            game.end_game(False)
            msg += ' Game over!'
      # For converting game history to a json, it will only add a comma it is not the only guess
      if len(game.guess_history) < 1:
        game.guess_history += '{"Guess": "%s", "Result": "%s"}' % (request.guess.lower(), msg)
      else:
        game.guess_history += ', {"Guess": "%s", "Result": "%s"}' % (request.guess.lower(), msg)
      game.put()
      return game.to_form(msg)

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=StringMessage,
                      path='games/active',
                      name='get_active_game_count',
                      http_method='GET')
    def get_active_game_count(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
      """Returns all of an individual User's active games"""
      user = User.query(User.name == request.user_name).get()
      if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
      games = Game.query(Game.user == user.key).filter(Game.game_over == False)
      return GameForms(items=[game.to_form('Ready to play!') for game in games])

    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancels a game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')
        game.end_game(False)
        game.put()
        return game.to_form('Game Canceled!')

    @endpoints.method(request_message=HIGH_SCORES_REQUEST,
                      response_message=ScoreForms,
                      path='scores/high_scores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
      """Returns high scores in descending order"""
      scores = Score.query(Score.won == True).order(-Score.guesses).fetch(limit=request.number_of_results)
      return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=RankForms,
                      path='score/user/rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
      """Returns all players ranked by performance"""
      return RankForms(items=[user.to_rank_form() for user in User.query().order(-User.win_loss)])

    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=HistoryForms,
                      path='game/history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Returns a game's history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        template = '{"history": [%s]}'
        game_history = json.loads(template % (game.guess_history))
        return HistoryForms(**game_history)   

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining
                                        for game in games])
            average = float(total_attempts_remaining)/count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))

api = endpoints.api_server([HangmanApi])