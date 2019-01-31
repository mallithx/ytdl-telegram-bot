#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging
import subprocess
import signal
import json

""" Local modules """
import config

""" 3th party modules """
from telegram import *
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler, ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)


def initialize():
    log.info('Initialize Telegram Bot...')

    # Create the Updater and pass it your bot's token.
    updater = Updater(config.BOT_TOKEN)
    updater.dispatcher.add_error_handler(handle_error)

    updater.dispatcher.add_handler(RegexHandler('^mp4 .*$', handle_conversion_mp4))
    updater.dispatcher.add_handler(RegexHandler('^.*$', handle_link_only))

    # Start the Bot
    log.info('Start polling...')
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    log.info('Initialize Telegram Bot...DONE. switching to idle mode.')
    updater.idle()

def handle_conversion_mp4(bot, update):
    update.message.reply_text(text='mp4 conversion is not supported yet');

def handle_link_only(bot, update):
    url = update.message.text
    log.info('Start handling url: %s' % url)

    try:
        process = subprocess.check_output(['youtube-dl', url, '--id', '--print-json', '-s'])
        data = json.loads(process.decode('utf8'))

        title = data['title']
        filename = data['_filename']
        formats = data['formats']
        targetFormat = None

        # find audio format
        for f in formats:
            if 'audio only' in f['format']:
                targetFormat = f

        log.info('Downloaded %s' % filename)
        log.debug('Target format: \n{}'.format(targetFormat))

        update.message.reply_text(
            text='<strong>%s\n --> </strong><a href="%s">%s</a>' % (title, targetFormat['url'], targetFormat['format']), 
            parse_mode=ParseMode.HTML)   

        return

    except Exception as e:  
        reply_error(update.message, e)
        return


def reply_error(msg, e):
    log.error('%s: %s' % (type(3).__name__, e))
    msg.reply_text('<strong>Oops! Something went wrong</strong>\n<i>Maybe due to invalid url?</i>', parse_mode=ParseMode.HTML)

def handle_error(bot, update, error):
    log.warning('Update "%s" caused error "%s"', update, error)

def on_exit(sig, func=None):
    print("exit handler triggered")
    sys.exit(1)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, on_exit)
    initialize()
