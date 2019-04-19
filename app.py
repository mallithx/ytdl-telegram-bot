#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging
import signal
import sys
import json
import datetime
import os
from io import BytesIO

""" 3th party modules """
from telegram import *
from telegram.ext import * 
import youtube_dl


# verify that config.py exists
try:
    import config
except ImportError as e:
    print('Error: No config.py file present. See config_template.py for further instructions.')
    sys.exit()


# setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=config.LOG_LEVEL)
log = logging.getLogger(__name__)



def handle_cancel(update, context):
    return ConversationHandler.END



def handle_start(bot, update):
    """ Handle /start command """
    update.message.reply_text(
        text='<strong>How to start?</strong>\nshare a link !', 
        parse_mode=ParseMode.HTML)



def handle_incoming_url(bot, update, chat_data):
    """ Handle incoming url """
    url = update.message.text
    log.info('Incoming url "%s"' % url)

    # load audio information
    with youtube_dl.YoutubeDL() as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
        except youtube_dl.utils.DownloadError as e:
            update.message.reply_text( 
                '<strong>Error:</strong> <i>Given url is invalid or from an unsupported source.</i>', parse_mode=ParseMode.HTML)
            return ConversationHandler.END

    meta = chat_data['metadata'] = {
        'title': info_dict['title'] if 'title' in info_dict else '',
        'performer': info_dict['creater'] if 'creater' in info_dict else info_dict['uploader'],
        'duration': str(datetime.timedelta(seconds=int(info_dict['duration']))) if 'duration' in info_dict else 'unknown',
        'thumb': info_dict['thumbnail'] if 'thumbnail' in info_dict else '',
    }

    # create format keyboard
    keyboard = [
        [InlineKeyboardButton("bestaudio", callback_data='bestaudio')],
        [InlineKeyboardButton("mp4", callback_data='mp4'), InlineKeyboardButton("wav", callback_data='wav')],
        [InlineKeyboardButton("abort", callback_data='abort')]
    ]

    update.message.reply_text('<strong>%-70s</strong>\n<i>by %s</i>' % (meta['title'], meta['performer']), 
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard))

    chat_data['info_dict'] = info_dict
    return MENU_FORMAT



def handle_format(bot, update, chat_data):
    """ Handle format """
    msg = update.callback_query.message
    _format = query = update.callback_query.data

    # remove keyboard
    bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id)

    if _format == 'abort':
        msg.reply_text('<i>aborted</i>', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    if _format == 'mp4' or _format == 'wav':
        msg.reply_text('<i>format %s not implemented yet</i>' % _format, parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    # create mode keyboard
    keyboard = [
        [InlineKeyboardButton("advanced", callback_data='advanced'), InlineKeyboardButton("quick", callback_data='quick')]
    ]

    bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

    chat_data['format'] = _format
    return MENU_DOWNLOAD

def handle_download(bot, update, chat_data):
    """ Handle download """
    msg = update.callback_query.message
    download_mode = query = update.callback_query.data

    # remove keyboard
    bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id)

    if download_mode == 'quick':
        return handle_quick_download(bot, msg, chat_data)
    if download_mode == 'advanced':
        return handle_advanced_download(bot, msg, chat_data)


def handle_quick_download(bot, msg, chat_data):
    chat_id = msg.chat_id
    info_dict = chat_data['info_dict']

    if not 'format' in chat_data:
        chat_data['format'] = 'bestaudio' # fallback format

    opts = {
        'outtmpl': 'tmp/%(id)s',
        'format': chat_data['format'],
        'forceid': True
    }

    # load audio information
    with youtube_dl.YoutubeDL(opts) as ydl:
        try:
            ydl.download([info_dict['webpage_url']])
            filename = 'tmp/' + info_dict['id']
            log.info('Downloaded file %s' % filename)
        except youtube_dl.utils.DownloadError as e:
            msg.reply_text( 
                '<strong>Error:</strong> <i>Failed to download audio from url.</i>', parse_mode=ParseMode.HTML)
            return ConversationHandler.END
    

    with open(filename, 'rb') as audio:
        bot.send_audio(chat_id=chat_id, audio=audio, timeout=180, **chat_data['metadata'])

    # remove audio file from disc
    try:
        os.remove(filename)
        log.info('Removed file %s' % filename)
    except:
        log.error('Failed to remove file %s' % filename)

    return ConversationHandler.END



def handle_advanced_download(bot, update, chat_data):
    msg.reply_text('Advanced download not implemented yet.')
    return ConversationHandler.END



def handle_error(bot, update, error):
    log.warning('Update "%s" caused error "%s"', update, error)



MENU_FORMAT, MENU_DOWNLOAD = range(2)

def initialize():
    log.info('Initialize Telegram Bot...')

    updater = Updater(config.BOT_TOKEN)
    updater.dispatcher.add_error_handler(handle_error)

    updater.dispatcher.add_handler(CommandHandler('start', handle_start))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.all, handle_incoming_url, pass_chat_data=True)],

        states={
            MENU_FORMAT: [CallbackQueryHandler(handle_format, pass_chat_data=True)],
            MENU_DOWNLOAD: [CallbackQueryHandler(handle_download, pass_chat_data=True)]
        },

        fallbacks=[CommandHandler('cancel', handle_cancel)],
        run_async_timeout=999
    )

    updater.dispatcher.add_handler(conv_handler)


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
