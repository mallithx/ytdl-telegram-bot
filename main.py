#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging
import os,signal,sys
import urllib.request
import json
import base64

""" Local modules """
import config

""" 3th party modules """
from telegram import *
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler, ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)

URL, Format = (1, 2)

def initialize():
    log.info('Initialize Telegram Bot...')

    # Create the Updater and pass it your bot's token.
    updater = Updater(config.BOT_TOKEN)
    updater.dispatcher.add_error_handler(handle_error)

    updater.dispatcher.add_handler(RegexHandler('^.*$', handle_url, pass_chat_data=True))
    updater.dispatcher.add_handler(CallbackQueryHandler(handle_download, pass_chat_data=True))

    # Start the Bot
    log.info('Start polling...')
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    log.info('Initialize Telegram Bot...DONE. switching to idle mode.')
    updater.idle()

def handle_download(bot, update, chat_data):
    query = update.callback_query
    data = query.data

    format_ = chat_data['format_urls'][int(data)][0]
    size = chat_data['format_urls'][int(data)][1]
    url = chat_data['format_urls'][int(data)][2]

    bot.send_message(chat_id=query.message.chat.id, 
        text='<strong>Download: </strong><i>%s (%s)</i> -> <a href="%s">here</a>' % (format_, size, url), 
        parse_mode=ParseMode.HTML)


def handle_url(bot, update, chat_data):
    url = update.message.text 

    log.debug('handle_url chat_data: {}'.format(chat_data))

    try:
        resp = urllib.request.urlopen('http://localhost:3000/info?url=%s' % url).read()
        data = json.loads(resp)

        chat_data['format_urls'] = []

        button_list = []
        for i, f in enumerate(data['formats']):
            url = f['url']
            formatName = f['type']
            formatSize = f['size'] if 'size' in f else f['audioBitrate']
            chat_data['format_urls'].append((formatName, formatSize, url))
            button_list.append([InlineKeyboardButton('[%s] %s' % (formatSize, formatName), callback_data=i)])
   
        reply_markup = InlineKeyboardMarkup(button_list)

        update.message.reply_text(
            text='<strong>Title:</strong> %s\n<strong>Length:</strong> %s' % (data['title'], '00:00'),
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup)


    except urllib.request.HTTPError as e:
        log.error(e)
        update.message.reply_text(text='<strong>Not a valid url!</strong>\n%s' % str(e), parse_mode=ParseMode.HTML)


def handle_error(bot, update, error):
    log.warning('Update "%s" caused error "%s"', update, error)

def on_exit(sig, func=None):
    print("exit handler triggered")
    sys.exit(1)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, on_exit)
    initialize()
