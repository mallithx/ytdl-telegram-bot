#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging
import os,signal,sys

""" Local modules """
import config
from core.core import WavesSpreadBot
import telegram_frontend.commands as commands
import telegram_frontend.menu as menu
import telegram_frontend.error as error

""" 3th party modules """
from telegram import *
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)

def message(bot, update):
    log.warn('TRIGGER')

def initialize():
    log.info('Initialize Telegram Bot...')

    # Initialize Core
    WavesSpreadBot.getInstance()

    # Create the Updater and pass it your bot's token.
    updater = Updater(config.BOT_TOKEN)

    updater.dispatcher.add_error_handler(error.handle)

    updater.dispatcher.add_handler(CommandHandler('help', commands.handle_help))
    updater.dispatcher.add_handler(CommandHandler('status', commands.handle_status))
    updater.dispatcher.add_handler(CommandHandler('menu', commands.handle_menu))
    updater.dispatcher.add_handler(CommandHandler('start', commands.handle_start))
    updater.dispatcher.add_handler(CommandHandler('stop', commands.handle_stop))

    # Workaround to handle menu button callbacks
    updater.dispatcher.add_handler(RegexHandler('status', commands.handle_status))
    updater.dispatcher.add_handler(RegexHandler('start', commands.handle_start))
    updater.dispatcher.add_handler(RegexHandler('stop', commands.handle_stop))

    # Start the Bot
    log.info('Start polling...')
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    log.info('Initialize Telegram Bot...DONE. switching to idle mode.')
    updater.idle()

def on_exit(sig, func=None):
    print("exit handler triggered")
    sys.exit(1)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, on_exit)
    initialize()
