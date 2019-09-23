#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
from argparse import ArgumentParser
import subprocess
import datetime
import logging
import os

""" 3th party modules """
from telegram import *
from telegram.ext import *
import youtube_dl

""" Local modules """
import src.utils as utils

log = logging.getLogger(__name__)


# Conversation stages
CHOOSE_FORMAT, CHOOSE_LENGTH, CHECKOUT = range(3)



def handle_cancel(update, context):
    return ConversationHandler.END


def handle_incoming_url(bot, update, chat_data):
    """ Handle incoming url """
    url = utils.parse_url(update.message.text)
    log.info('Incoming url "%s"' % url)

    bot.send_chat_action(update.message.chat_id, action=ChatAction.TYPING)

    try:
        info_dict = utils.get_info(url)
        chat_data['metadata'] = {
            'url': url,
            'title': info_dict['title'] if 'title' in info_dict else '',
            'performer': info_dict['creater'] if 'creater' in info_dict else info_dict['uploader'],
            'duration': str(datetime.timedelta(seconds=int(info_dict['duration']))) if 'duration' in info_dict else 'unknown',
            'thumb': info_dict['thumbnail'] if 'thumbnail' in info_dict else '',
        }
    except youtube_dl.utils.DownloadError as e:
        update.message.reply_text( 
            '<strong>Error:</strong> <i>Given url is invalid or from an unsupported source.</i>', parse_mode=ParseMode.HTML)
        return ConversationHandler.END


    # create format keyboard
    keyboard = [['wav', 'mp3'], ['abort']]

    bot.send_message(
        chat_id=update.message.chat_id, 
        text='<strong>%(title)-70s</strong>\n<i>by %(performer)s</i>' % chat_data['metadata'],
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

    reply = update.message.reply_text(
        text='<i>** choose format **</i>', 
        parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

    chat_data['url'] = url
    chat_data['info_dict'] = info_dict
    chat_data['last_message_id'] = reply.message_id

    return CHOOSE_FORMAT



def handle_format_selection(bot, update, chat_data):

    ext = update.message.text
    msg = update.message
    chat_id = msg.chat_id


    if ext == 'abort': return ConversationHandler.END

    bot.send_chat_action(update.message.chat_id, action=ChatAction.TYPING)
    # remove previous messages
    bot.delete_message(chat_id=chat_id, message_id=chat_data['last_message_id'])
    bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    # send new message
    bot.send_message(chat_id=chat_id, 
        text='<strong>Format:</strong> <i>%s</i>' % ext, 
        parse_mode=ParseMode.HTML)

    reply = update.message.reply_text(
        '<i>** select start/end ** { HH:MM:SS-HH:MM:SS }\n or /skip</i>', 
        parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())

    chat_data['ext'] = ext
    chat_data['last_message_id'] = reply.message_id

    return CHOOSE_LENGTH



def handle_length_selection(bot, update, chat_data):
    
    length = update.message.text
    msg = update.message
    chat_id = msg.chat_id

    if length == 'abort': return ConversationHandler.END

    bot.send_chat_action(update.message.chat_id, action=ChatAction.TYPING)
    # remove previous messages
    bot.delete_message(chat_id=chat_id, message_id=chat_data['last_message_id'])
    bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    # send new message
    bot.send_message(chat_id=chat_id, 
        text='<strong>Length:</strong> <i>%s</i>' % length, 
        parse_mode=ParseMode.HTML)

    # create checkout keyboard
    keyboard = [['abort', 'download']]

    reply = update.message.reply_text(
        '<i>** please confirm **</i>', 
        parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

    chat_data['length'] = length
    chat_data['last_message_id'] = reply.message_id

    return CHECKOUT



def handle_checkout(bot, update, chat_data):

    confirmed = update.message.text
    msg = update.message
    chat_id = msg.chat_id

    if confirmed == 'abort': return ConversationHandler.END

    # remove previous messages
    bot.delete_message(chat_id=chat_id, message_id=chat_data['last_message_id'])
    bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    # send new message
    status_msg = bot.send_message(chat_id=chat_id, text='<i>.. processing (1/2) ..</i>', parse_mode=ParseMode.HTML)
    bot.send_chat_action(update.message.chat_id, action=ChatAction.RECORD_AUDIO)

    # download audio
    try:
        filename = utils.get_download(chat_data['url'], chat_data['ext'])
    except youtube_dl.utils.DownloadError as e:
        update.message.reply_text( 
            '<strong>Error:</strong> <i>Failed to download audio as %s.</i>' % chat_data['ext'], parse_mode=ParseMode.HTML)
        return ConversationHandler.END


    # update status message
    bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
    status_msg = bot.send_message(chat_id=chat_id, text='<i>.. sending audio (2/2) ..</i>', parse_mode=ParseMode.HTML)
    bot.send_chat_action(update.message.chat_id, action=ChatAction.UPLOAD_AUDIO)


    if not utils.size_ok(filename):
        update.message.reply_text('<strong>Error:</strong> <i>The audio file is too large (max. 50MB).</i>', parse_mode=ParseMode.HTML)
    else:
        # open audio file for transfer    
        try:
            with open(filename, 'rb') as audio:
                log.info('Start transferring file %s to client' % filename)
                bot.send_audio(chat_id=chat_id, audio=audio, timeout=180, **chat_data['metadata'])
                log.info('Finished transferring file %s' % filename)
        except FileNotFoundError as e:
                update.message.reply_text(
                    '<strong>Error:</strong> <i>Failed to download audio as %s.</i>' % chat_data['ext'], parse_mode=ParseMode.HTML)
                return ConversationHandler.END

    # remove please wait message
    bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
    # remove tmp file from disk
    utils.remove_file(filename)

    return ConversationHandler.END



# Conversation handler definition
handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.all, handle_incoming_url, pass_chat_data=True)],

    states={
        CHOOSE_FORMAT: [MessageHandler(Filters.all, handle_format_selection, pass_chat_data=True)],
        CHOOSE_LENGTH: [MessageHandler(Filters.all, handle_length_selection, pass_chat_data=True)],

        CHECKOUT: [MessageHandler(Filters.all, handle_checkout, pass_chat_data=True)]
    },

    fallbacks=[CommandHandler('cancel', handle_cancel)],
    run_async_timeout=999
)