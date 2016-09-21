#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity, taskqueue
from api import HangmanApi

from models import *


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        games = Game.query(Game.game_over == False)
        users = (game.user.get() for game in games)
        #users = User.query(User.email != None)
        for user in users:
            if user.email != None:
                subject = 'This is a reminder!'
                body = 'Hello {}, you have an incomplete Hangman game waiting!'.format(user.name)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                try:
                    mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                                   user.email,
                                   subject,
                                   body)
                except:
                    taskqueue.add(url='/crons/send_reminder')


class UpdateAverageMovesRemaining(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        HangmanApi._cache_average_attempts()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_attempts', UpdateAverageMovesRemaining),
], debug=True)
