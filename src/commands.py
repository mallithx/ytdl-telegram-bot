#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging
import subprocess
import json
import re

""" Local modules """
import config
from src.track import Track
from src.waitmsg import PleaseWaitMessage

""" 3th party modules """
from telegram import *
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)

def noop():
    pass

def handle_shared_link(bot, update, chat_data):
    """ Handle imcomming links """
    url = update.message.text
    chat_id = update.message.chat.id
    log.info('Incoming url "%s"' % url)

    # display wait message
    please_wait = PleaseWaitMessage(bot, chat_id)
    please_wait.send()

    # new track from url
    track = Track(url)

    def done(data):
        _id = data['id']
        title = data['title']
        uploader = data['uploader']

        # set chat data
        chat_data.update({'track': track})

        # reply keyboard
        keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton('Download .mp3', callback_data='mp3')],
                [InlineKeyboardButton('Download .wav', callback_data='wav')],
                [InlineKeyboardButton('Download .flac', callback_data='flac')]])

        please_wait.revoke()
        update.message.reply_text(
            text='<strong>%s</strong>\n<i>uploaded by %s</i>' % (title, uploader), 
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard)

    def error(e):        
        please_wait.revoke()
        __reply_error(update.message, e)

    # start getinfo
    track.getinfo(done, error)


def handle_provide_download(bot, update, chat_data):
    """ QueryCallbackHandler for download format choice """
    query = update.callback_query
    chat_id = query.message.chat.id

    ext = query.data
    track = chat_data['track']
    url = track.url

    # remove download btn after click
    bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id)

    # display prepare message
    please_wait = PleaseWaitMessage(bot, chat_id)
    please_wait.send()
    
    def done():
        # send file
        bot.send_audio(chat_id=chat_id, audio=open(track.filename, 'rb'), timeout=1000)
        log.info('Successfully send "%s" to chat_id=%s' % (track.filename, chat_id))

        please_wait.revoke()
        # remove file from disk
        track.delete(noop, noop)

    def error(e):
        please_wait.revoke()
        __reply_error(query.message, e)

    # start download
    track.download(done, error, ext=ext)
    

def __reply_error(msg, e):
    """ Reply generic error to client """
    log.error('%s: %s' % (type(3).__name__, e))

    if hasattr(e, 'returncode') and e.returncode:
        e = 'Maybe due to invalid url?'

    msg.reply_text('<strong>Oops! Something went wrong</strong>\n<i>%s</i>' % e, parse_mode=ParseMode.HTML)


def handle_start(bot, update):
    """ Handle /start command """
    update.message.reply_text(
        text='<strong>How to start?</strong>\nshare a link !', 
        parse_mode=ParseMode.HTML)
