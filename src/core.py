#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging

""" 3th party modules """
from telegram import *
from telegram.ext import * 

""" Local modules """
import src.error
import src.handlers

log = logging.getLogger(__name__)


class TelegramAudioDownloadBot:

    def __init__(self, token):
        self.updater = Updater(token=token, workers=4)
        self.dispatcher = self.updater.dispatcher

        self.__register_handlers()
        log.info('Initialize Telegram Bot...DONE. switching to idle mode.')


    def start(self):
        # Start polling and go to idle
        log.info('Start polling...')
        self.updater.start_polling()
        self.updater.idle()

    def __register_handlers(self):
        # Error handler
        self.dispatcher.add_error_handler(src.error.handler)
        # Command handlers
        self.dispatcher.add_handler(src.handlers.StartCommandHandler())
        self.dispatcher.add_handler(src.handlers.VersionCommandHandler())
        self.dispatcher.add_handler(src.handlers.UpdateCommandHandler())
        self.dispatcher.add_handler(src.handlers.HistoryCommandHandler())
        # *main* conversation handler
        self.dispatcher.add_handler(src.handlers.MainConversationHandler())

        log.info('Handler registration done. (success)')
    
