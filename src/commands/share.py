#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging
import subprocess
import signal
import json
import re

""" Local modules """
import config

""" 3th party modules """
from telegram import *
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)

def handle_shared_url(bot, update, chat_data):
    url = update.message.text
    chat_id = update.message.chat.id
    log.info('info "%s"' % url)

    # display prepare message
    msg_prepare = bot.send_message(chat_id=chat_id, text='<i>... please wait ...</i>', parse_mode=ParseMode.HTML)

    try:
        process = subprocess.check_output(['youtube-dl', '-s', url, '--print-json', '--id'])
        data = json.loads(process.decode('utf8'))

        # remove prepare message
        bot.delete_message(chat_id=chat_id, message_id=msg_prepare.message_id)

        _id = data['id']
        title = data['title']
        uploader = data['uploader']

        # set chat data
        chat_data.update({'url': url})

        # reply keyboard
        keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton('Download .mp3', callback_data='mp3')],
                [InlineKeyboardButton('Download .wav', callback_data='wav')]])

        update.message.reply_text(
            text='<strong>%s</strong>\n<i>uploaded by %s</i>' % (title, uploader), 
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard)

        return

    except subprocess.CalledProcessError as e:  
        reply_error(update.message, e)
        return


def handle_provide_download(bot, update, chat_data):
    query = update.callback_query
    chat_id = query.message.chat.id

    ext = query.data
    url = chat_data['url']
    log.info('download "%s"' % url)

    # remove download btn after click
    bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id)

    # display prepare message
    msg_prepare = bot.send_message(chat_id=chat_id, text='<i>... please wait ...</i>', parse_mode=ParseMode.HTML)

    # download file
    process = subprocess.check_output(['youtube-dl', url, '--print-json', '-f bestaudio', '-x', '--audio-format', ext, '--id'])
    data = json.loads(process.decode('utf8'))

    _id = data['id']
    filename = '%s.%s' % (_id, ext) # button data is limited to 64 bytes

    # send file
    bot.send_audio(chat_id=chat_id, audio=open(filename, 'rb'), timeout=1000)
    log.info('send "%s" done' % filename)

    # remove prepare message
    bot.delete_message(chat_id=chat_id, message_id=msg_prepare.message_id)

    # remove file
    process = subprocess.check_output(['rm', '-f', filename])
    log.info('delete "%s" done' % filename)

    

def reply_error(msg, e):
    log.error('%s: %s' % (type(3).__name__, e))

    if hasattr(e, 'returncode') and e.returncode:
        e = 'Maybe due to invalid url?'

    msg.reply_text('<strong>Oops! Something went wrong</strong>\n<i>%s</i>' % e, parse_mode=ParseMode.HTML)
