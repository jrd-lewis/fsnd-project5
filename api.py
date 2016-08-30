# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
import settings
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakeGuessForm,\
    ScoreForms, GameForms
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeGuessForm,
    urlsafe_game_key=messages.StringField(1))
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

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

       	return game.to_form('Good luck playing Hangman!')

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

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/word/{urlsafe_game_key}',
                      name='guess_word',
                      http_method='PUT')
    def guess_word(self, request):
    	"""Guesses a word. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')

        game.attempts_remaining -= 1
        if request.guess.lower() == game.target_word.lower():
            game.end_game(True)
            return game.to_form('You win!')
        else:
        	msg = 'Incorrect word!'

        if game.attempts_remaining < 1:
            game.end_game(False)
            return game.to_form(msg + ' Game over!')
        else:
            game.put()
            return game.to_form(msg)

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/letter/{urlsafe_game_key}',
                      name='guess_letter',
                      http_method='PUT')
    def guess_letter(self, request):
    	"""Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')

        game.attempts_remaining -= 1

        if game.guess_history.find(request.guess.lower()) != -1:
          return game.to_form('Letter already guessed!')
        else:
          game.guess_history += request.guess.lower() + ','
        
        temp_word = ''
        letters_found = 0
        i = 0
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

        if game.current_word.lower() == game.target_word.lower():
            game.end_game(True)
            return game.to_form('You win!')

        if game.attempts_remaining < 1:
            game.end_game(False)
            return game.to_form(msg + ' Game over!')
        else:
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



api = endpoints.api_server([HangmanApi])