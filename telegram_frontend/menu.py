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

def handle_button_press(bot, update):
    query = update.callback_query

    log.debug('Pressed Menubutton: {}'.format(query.data))

    update.message = query.message
    
    bot.edit_message_text(text="Running action: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


    if query.data == 'status':
        commands.handle_status(bot, update)
    elif query.data == 'start':
        commands.handle_start(bot, update)
    elif query.data == 'stop':
        commands.handle_stop(bot, update)
    else:
        commands.handle_help(bot, update)
