#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging
import datetime

""" Local modules """
import config

""" 3th party modules """


log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)

class WavesSpreadBot:
    """TODO: Add description"""

    """ Singleton instance """
    __instance = None

    """ State attribute - False => Bot is off | True => Bot is running """
    running = False
    running_since = None
    last_up_time = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if WavesSpreadBot.__instance == None:
            WavesSpreadBot()
        return WavesSpreadBot.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if WavesSpreadBot.__instance != None:
            raise Exception("This class is a singleton! Call getInstance() instead.")
        else:
            WavesSpreadBot.__instance = self

            if config.AUTO_START_WAVES_BOT:
                WavesSpreadBot.__instance.start()

    def start(self):
        """ Start up """
        log.info('Starting WavesSpreadBot...')
        self.running = True
        self.running_since = datetime.datetime.now()
        log.info('WavesSpreadBot is now running.')

    def stop(self):
        """ Shut down """
        log.info('Shutdown WavesSpreadBot...')
        self.last_up_time = self.getTotalUpTime()
        self.running = False
        log.info('WavesSpreadBot successfully shut down.')

    def getStatus(self):
        """ Returns current state of running attribute """
        return self.running;

    def getTotalUpTime(self):
        """ Returns time passed since bot is running """
        if self.running:
            return datetime.datetime.now() - self.running_since
        else:
            return ' - '

    def getLastUpTime(self):
        """ Returns time passed since bot is running """
        return self.last_up_time if self.last_up_time else ' - '
