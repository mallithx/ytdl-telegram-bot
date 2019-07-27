#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import subprocess
import logging
import signal
import sys
import json
import datetime
import os
import re
from io import BytesIO

""" 3th party modules """
from telegram import *
from telegram.ext import * 

# verify that youtube-dl and python bindings are installed
try:
    import youtube_dl
except ImportError as e:
    print('Error: youtube-dl and/or youtube_dl python bindings are not installed')

# verify that config.py exists
try:
    import config
except ImportError as e:
    print('Error: No config.py file present. See config_template.py for further instructions.')
    sys.exit()


# setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
log = logging.getLogger(__name__)


def parse_url(msg):
    """ Extract url from message """
    match = re.search('(?P<url>https?://[^\s]+)', msg)

    if match:
        return match.group('url')
    else:
        log.error('No URL found in "%s"' % msg)

    return msg


def handle_cancel(update, context):
    return ConversationHandler.END



def handle_start(bot, update):
    """ Handle /start command """
    update.message.reply_text(
        text='<strong>Audio Downloader</strong>\n<i>v2019.06.19</i>\n\n<strong>Share a link or enter a URL to download audio file.</strong>\n\nyoutube.com \u2714\nsoundcloud.com \u2714\n\nUse /update to fetch most recent youtube-dl /version.', 
        parse_mode=ParseMode.HTML)

def handle_version(bot, update):
    """ Handle /version command """ 
    try:
        resp = subprocess.check_output(['youtube-dl', '--version'])
        version = resp.decode('utf-8')
        update.message.reply_text(
            text='<strong>youtube-dl:</strong> %s' % version,
            parse_mode=ParseMode.HTML)
    except subprocess.CalledProcessError as e:
        update.message.reply_text(
            text='<i>Failed to determine version of youtube-dl</i>\n%r' % e,
            parse_mode=ParseMode.HTML)	 

def handle_update(bot, update):
    """ Handle /update command """
    try:
        resp = subprocess.check_output(['pip', 'install', 'youtube-dl', '--upgrade'])
        resp = resp.decode('utf-8')
        update.message.reply_text(
            text=resp,
            parse_mode=ParseMode.HTML)
    except subprocess.CalledProcessError as e:
        update.message.reply_text(
            text='<i>Failed to update youtube-dl</i>\n%r' % e,
            parse_mode=ParseMode.HTML)


def handle_incoming_url(bot, update, chat_data):
    """ Handle incoming url """
    url = parse_url(update.message.text)
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


def handle_full_length_download(bot, msg, chat_data):
    chat_id = msg.chat_id
    info_dict = chat_data['info_dict']

    if not 'format' in chat_data:
        chat_data['format'] = 'bestaudio' # fallback format

    opts = {
        'outtmpl': 'tmp/%(id)s',
        'format': 'bestvideo+bestaudio/best',
        'forceid': True
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
            filename = 'tmp/%s.%s' % (info_dict['id'], chat_data['format'])
            log.info('Downloaded file %s' % filename)
        except youtube_dl.utils.DownloadError as e:
            msg.reply_text( 
                '<strong>Error:</strong> <i>Failed to download audio as %s.</i>' % chat_data['format'], parse_mode=ParseMode.HTML)
            return ConversationHandler.END
    

    with open(filename, 'rb') as audio:
        log.info('Start transferring file %s to client' % filename)
        bot.send_audio(chat_id=chat_id, audio=audio, timeout=180, **chat_data['metadata'])
        log.info('Finished transferring file %s' % filename)

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



def handle_error(bot, update, error):
    log.warning('Update "%s" caused error "%s"', update, error)



MENU_FORMAT, MENU_LENGTH = range(2)

def initialize():
    log.info('Initialize Telegram Bot...')

    updater = Updater(config.BOT_TOKEN)
    updater.dispatcher.add_error_handler(handle_error)

    updater.dispatcher.add_handler(CommandHandler('start', handle_start))
    updater.dispatcher.add_handler(CommandHandler('version', handle_version))
    updater.dispatcher.add_handler(CommandHandler('update', handle_update))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.all, handle_incoming_url, pass_chat_data=True)],

        states={
            MENU_FORMAT: [CallbackQueryHandler(handle_menu_format, pass_chat_data=True)],
            MENU_LENGTH: [CallbackQueryHandler(handle_menu_length, pass_chat_data=True)]
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
