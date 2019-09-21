#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
from argparse import ArgumentParser
import subprocess
import logging
import datetime
import os

""" 3th party modules """
from telegram import *
from telegram.ext import *
import youtube_dl

""" Local modules """
import src.utils as utils

log = logging.getLogger(__name__)


# Conversation stages
MENU_FORMAT, MENU_LENGTH = range(2)



def handle_cancel(update, context):
    return ConversationHandler.END



def handle_incoming_url(bot, update, chat_data):
    """ Handle incoming url """
    url = utils.parse_url(update.message.text)
    log.info('Incoming url "%s"' % url)

    bot.send_chat_action(update.message.chat_id, action=ChatAction.TYPING)

    opts = {
        'logger': logging.getLogger('youtube-dl'),
        'verbose': True,
        'format': 'bestvideo+bestaudio/best'
    }

    # load audio information
    with youtube_dl.YoutubeDL(opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
        except youtube_dl.utils.DownloadError as e:
            update.message.reply_text( 
                '<strong>Error:</strong> <i>Given url is invalid or from an unsupported source.</i>', parse_mode=ParseMode.HTML)
            return ConversationHandler.END

    meta = chat_data['metadata'] = {
        'url': url,
        'title': info_dict['title'] if 'title' in info_dict else '',
        'performer': info_dict['creater'] if 'creater' in info_dict else info_dict['uploader'],
        'duration': str(datetime.timedelta(seconds=int(info_dict['duration']))) if 'duration' in info_dict else 'unknown',
        'thumb': info_dict['thumbnail'] if 'thumbnail' in info_dict else '',
    }

    # create format keyboard
    keyboard = [
        [InlineKeyboardButton("mp3", callback_data='mp3'), InlineKeyboardButton("wav", callback_data='wav')],
        [InlineKeyboardButton("abort", callback_data='abort')]
    ]

    update.message.reply_text('<strong>%-70s</strong>\n<i>by %s</i>\n<i>%s</i>' % 
            (meta['title'], meta['performer'], meta['url']), 
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard))

    # remove initial message
    bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

    chat_data['info_dict'] = info_dict
    return MENU_FORMAT



def handle_menu_format(bot, update, chat_data):
    """ Handle format """
    msg = update.callback_query.message
    _format = query = update.callback_query.data

    # remove keyboard
    bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id)

    if _format == 'abort':
        msg.reply_text('<i>aborted</i>', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    # create mode keyboard
    keyboard = [
        [InlineKeyboardButton("cut", callback_data='cut'), InlineKeyboardButton("full length", callback_data='full')]
    ]

    bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

    chat_data['format'] = _format
    return MENU_LENGTH



def handle_menu_length(bot, update, chat_data):
    """ Handle download """
    msg = update.callback_query.message
    download_mode = query = update.callback_query.data

    # remove keyboard
    bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id)

    if download_mode == 'full':
        return handle_full_length_download(bot, msg, chat_data)
    if download_mode == 'cut':
        return handle_cut_download(bot, msg, chat_data)
    else:
        return ConversationHandler.END



def handle_full_length_download(bot, msg, chat_data):
    chat_id = msg.chat_id
    info_dict = chat_data['info_dict']

    if not 'format' in chat_data:
        chat_data['format'] = 'webm' # fallback format

    opts = {
        'logger': logging.getLogger('youtube-dl'),
        'outtmpl': 'tmp_audio',
        'verbose': True,
        'format': 'bestvideo+bestaudio/best',
        'forceid': True,
        'progress_hooks': [progress_hook]
    }

    opts.update({
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': chat_data['format'],
            'preferredquality': '192',
        }]
    })

    # load audio information
    with youtube_dl.YoutubeDL(opts) as ydl:
        try:
            log.debug('Downloading with opts:\n%r' % opts)
            ydl.download([info_dict['webpage_url']])
            filename = 'tmp_audio.%s' % chat_data['format']
            log.info('Downloaded file %s' % filename)
        except youtube_dl.utils.DownloadError as e:
            msg.reply_text( 
                '<strong>Error:</strong> <i>Failed to download audio as %s.</i>' % chat_data['format'], parse_mode=ParseMode.HTML)
            return ConversationHandler.END


    # check audio file size
    size = os.path.getsize(filename)
    log.info('File %s has a size of %d' % (filename, size))
    if size >= 52428800: # 50MB
         msg.reply_text(
                '<strong>Error:</strong> <i>The audio file is too large (max. 50MB).</i>', parse_mode=ParseMode.HTML)
    else:
        # open audio file for transfer    
        try:
            with open(filename, 'rb') as audio:
                log.info('Start transferring file %s to client' % filename)
                bot.send_audio(chat_id=chat_id, audio=audio, timeout=180, **chat_data['metadata'])
                log.info('Finished transferring file %s' % filename)
        except FileNotFoundError as e:
                msg.reply_text(
                    '<strong>Error:</strong> <i>Failed to download audio as %s.</i>' % chat_data['format'], parse_mode=ParseMode.HTML)
                return ConversationHandler.END

    # remove audio file from disc
    try:
        os.remove(filename)
        log.info('Removed file %s' % filename)
    except:
        log.error('Failed to remove file %s' % filename)

    return ConversationHandler.END



def handle_cut_download(bot, msg, chat_data):
    msg.reply_text('Cut download not implemented yet.')
    return ConversationHandler.END



def progress_hook(d):
    log.info('PROGRESS HOOK CALLED\n%r' % d)




# Conversation handler definition
handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.all, handle_incoming_url, pass_chat_data=True)],

    states={
        MENU_FORMAT: [CallbackQueryHandler(handle_menu_format, pass_chat_data=True)],
        MENU_LENGTH: [CallbackQueryHandler(handle_menu_length, pass_chat_data=True)]
    },

    fallbacks=[CommandHandler('cancel', handle_cancel)],
    run_async_timeout=999
)