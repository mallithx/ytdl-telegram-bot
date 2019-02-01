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
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)

def create_keyboard_markup(filename):
    keyboard = []
    """
    col_counter = 0
    row = []
    for f in formats:
        
        if f['ext'] == 'webm':
            continue

        row.append(InlineKeyboardButton(f['ext'], callback_data=f['ext']))
        col_counter += 1

        if col_counter == 3:
            keyboard.append(row)
            row = []
            col_counter = 0"""
    
    keyboard.append([InlineKeyboardButton('Download Audio', callback_data=filename)])

    return InlineKeyboardMarkup(keyboard)

def handle_shared_url(bot, update, chat_data):
    url = update.message.text
    log.info('Start handling url: %s' % url)

    chat_data = dict()

    try:
        process = subprocess.check_output(['youtube-dl', url, '--print-json', '-f bestaudio', '-o%(title)s.%(ext)s'])
        data = json.loads(process.decode('utf8'))

        title = data['title']
        filename = '%s.%s' % (data['title'], data['ext'])

        update.message.reply_text(
            text='<strong>%s</strong>\n<i>Select option:</i>' % (title), 
            parse_mode=ParseMode.HTML,
            reply_markup=create_keyboard_markup(filename))   

        return

    except Exception as e:  
        reply_error(update.message, e)
        return


def handle_provide_download(bot, update, chat_data):
    chat_id = update.callback_query.message.chat.id
    filename = update.callback_query.data

    bot.send_message(chat_id=chat_id, text='<i>preparing file download ...</i>', parse_mode=ParseMode.HTML)

    bot.send_audio(chat_id=chat_id, audio=open(filename, 'rb'), timeout=1000)
    log.debug('send done')
    
    process = subprocess.check_output(['rm', '-f', filename])
    log.debug('delete done')

    

def reply_error(msg, e):
    log.error('%s: %s' % (type(3).__name__, e))

    if hasattr(e, 'returncode') and e.returncode:
        e = 'Maybe due to invalid url?'

    msg.reply_text('<strong>Oops! Something went wrong</strong>\n<i>%s</i>' % e, parse_mode=ParseMode.HTML)