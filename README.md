[logo]: https://udacity.com/favicon.ico "Udacity"
![udacity][logo] Project 5: Design a Game
====================================

##Game Description
Description here...

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
   - Path: ''
   - Method: 
   - Parameters: 
   - Returns: 
   - Description: 
 - **create_user**
   - Path: 'user'
   - Method: POST
   - Parameters: user_name, email (optional)
   - Returns: Message confirming creation of the User.
   - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
 - **get_scores**
   - Path: ''
   - Method: 
   - Parameters: 
   - Returns: 
   - Description: 
 - **get_user_games**
   - Path: ''
   - Method: 
   - Parameters: 
   - Returns: 
   - Description: 
 - **get_user_scores**
   - Path: ''
   - Method: 
   - Parameters: 
   - Returns: 
   - Description: 
 - **guess_letter**
   - Path: ''
   - Method: 
   - Parameters: 
   - Returns: 
   - Description: 
 - **guess_word**
   - Path: ''
   - Method: 
   - Parameters: 
   - Returns: 
   - Description: 
 - **new_game**
   - Path: ''
   - Method: 
   - Parameters: 
   - Returns: 
   - Description: 


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
