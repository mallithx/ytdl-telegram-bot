#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging

""" Local modules """
import config
from core.core import WavesSpreadBot
import telegram_frontend.commands as commands

""" 3th party modules """
from telegram import *

log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)

def handle(bot, update):
    query = update.callback_query

    log.info('Pressed Menubutton: {}'.format(query.data))

    if query.data == 'Status' :
        commands.handle_status(None, update)
