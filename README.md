[logo]: https://udacity.com/favicon.ico "Udacity"
![udacity][logo] Project 5: Design a Game
====================================

##Game Description
This is a classic game of Hangman. A word is randomly selected from a list of word for the player to guess. The player must guess the letters in the word or the word itself within the specified amount of guesses to win.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - settings.py: Global variables for the API
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **cancel_game**
   - Path: 'game/cancel/{urlsafe_game_key}'
   - Method: PUT
   - Parameters: urlsafe_game_key
   - Returns: Message confirming cancellation of the Game.
   - Description: Cancels a specified game, based on the key.
 - **create_user**
   - Path: 'user'
   - Method: POST
   - Parameters: user_name, email (optional)
   - Returns: Message confirming creation of the User.
   - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
 - **get_scores**
   - Path: 'scores'
   - Method: GET
   - Parameters: None
   - Returns: Form containing all Scores.
   - Description: Returns all Scores
 - **get_user_games**
   - Path: 'scores/user/{user_name}'
   - Method: GET
   - Parameters: user_name
   - Returns: Form containing all of a User's Scores.
   - Description: Returns all of an individual User's Scores.
 - **get_user_scores**
   - Path: 'games/user/{user_name}'
   - Method: GET
   - Parameters: user_name
   - Returns: Form containing all of a User's active Games.
   - Description: Returns all of an individual User's active games.
 - **guess_letter**
   - Path: 'game/letter/{urlsafe_game_key}'
   - Method: PUT
   - Parameters: urlsafe_game_key 
   - Returns: Message containing the result of the guess.
   - Description: Guesses a letter within the word. Returns the game state.
 - **guess_word**
   - Path: 'game/word/{urlsafe_game_key}'
   - Method: PUT
   - Parameters: urlsafe_game_key
   - Returns: Message containing the result of the guess.
   - Description: Guesses the word. Returns the game state.
 - **new_game**
   - Path: 'game'
   - Method: POST
   - Parameters: user_name
   - Returns: Message confirming creation of the Game.
   - Description: Creates a new Game for the User with the specified user name.


##Models Included:
  - **User**
    - Stores unique user_name and (optional) email address.
    
  - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
  - **Score**
    - Records completed games. Associated with Users model via KeyProperty.

##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).
 - **NewGameForm**
    - Used to create a new game (user_name, min, max, attempts)
 - **MakeMoveForm**
    - Inbound make move form (guess).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    guesses).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.
