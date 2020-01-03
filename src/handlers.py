#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import subprocess
import logging
import datetime
import os

""" 3th party modules """
from telegram import *
from telegram.ext import * 
import youtube_dl

""" Local modules """
import src.utils
import src.history

log = logging.getLogger(__name__)



def StartCommandHandler():

    def handler(bot, update):
        update.message.reply_text(
            text='<strong>Audio Downloader</strong>\n<i>v2019.06.19</i>\nhttps://github.com/pthuencher/python-telegram-bot-audio-downloader\n\n<strong>Share a link or enter a URL to download audio file.</strong>\n\nyoutube.com \u2714\nsoundcloud.com \u2714\n\nUse /update to fetch most recent youtube-dl /version.', 
            parse_mode=ParseMode.HTML)

    return CommandHandler('start', handler)

def VersionCommandHandler():

    def handler(bot, update):
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

    return CommandHandler('version', handler)

def UpdateCommandHandler():

    def handler(bot, update):
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

    return CommandHandler('update', handler)


def HistoryCommandHandler():

    def handler(bot, update):
        history = src.history.get_history()

        if history is None:
            update.message.reply_text(
                text='<i>No history available</i>',
                parse_mode=ParseMode.HTML)
        else:
            update.message.reply_text(
                text='<i>last %d downloads</i>\n%s' % (history.count('\n'), history),
                parse_mode=ParseMode.HTML)


    return CommandHandler('history', handler)



def MainConversationHandler():

    # Conversation stages
    CHOOSE_FORMAT, CHOOSE_LENGTH, CHECKOUT = range(3)


    def handle_abort(bot, update, last_message_id=None):

        chat_id = update.message.chat_id
        msg_id = update.message.message_id

        bot.send_message(chat_id=chat_id, text='<i>aborted</i>', parse_mode=ParseMode.HTML)
        bot.delete_message(chat_id=chat_id, message_id=msg_id)

        if last_message_id:
            bot.delete_message(chat_id=chat_id, message_id=last_message_id)

        return ConversationHandler.END

    def handle_error(bot, update, last_message_id=None, error_message=None):

        chat_id = update.message.chat_id
        msg_id = update.message.message_id

        if error_message is None:
            error_message = 'An unspecified error occured! :('

        bot.send_message(chat_id=chat_id, text='<strong>error:</strong> <i>%s</i>' % error_message, parse_mode=ParseMode.HTML)
        #bot.delete_message(chat_id=chat_id, message_id=msg_id)

        if last_message_id:
            bot.delete_message(chat_id=chat_id, message_id=last_message_id)

        return ConversationHandler.END

    def handle_cancel(update, context):
        return handle_abort(context.bot, update)


    def handle_incoming_url(bot, update, chat_data):
        """ Handle incoming url """
        url = src.utils.parse_url(update.message.text)
        log.info('Incoming url "%s"' % url)

        bot.send_chat_action(update.message.chat_id, action=ChatAction.TYPING)

        try:
            info_dict = src.utils.get_info(url)
            chat_data['metadata'] = {
                'url': url,
                'title': info_dict['title'] if 'title' in info_dict else '',
                'performer': info_dict['creater'] if 'creater' in info_dict else info_dict['uploader'],
                'duration': str(datetime.timedelta(seconds=int(info_dict['duration']))) if 'duration' in info_dict else 'unknown',
                'thumb': info_dict['thumbnail'] if 'thumbnail' in info_dict else '',
            }
        except (youtube_dl.utils.DownloadError, youtube_dl.utils.ExtractorError) as e:
            return handle_error(bot, update, error_message='given url is invalid or from an unsupported source')


        # create format keyboard
        keyboard = [['wav', 'mp3'], ['abort']]

        bot.send_message(
            chat_id=update.message.chat_id, 
            text='<strong>%(title)-70s</strong>\n<i>by %(performer)s</i>' % chat_data['metadata'],
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))

        reply = update.message.reply_text(
            text='<i>** choose format **</i>', 
            parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))

        chat_data['url'] = url
        chat_data['info_dict'] = info_dict
        chat_data['last_message_id'] = reply.message_id

        return CHOOSE_FORMAT



    def handle_format_selection(bot, update, chat_data):

        ext = update.message.text
        msg = update.message
        chat_id = msg.chat_id


        if ext == 'abort': return handle_abort(bot, update, chat_data['last_message_id'])

        bot.send_chat_action(update.message.chat_id, action=ChatAction.TYPING)
        # remove previous messages
        bot.delete_message(chat_id=chat_id, message_id=chat_data['last_message_id'])
        bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        # send new message
        bot.send_message(chat_id=chat_id, 
            text='<strong>Format:</strong> <i>%s</i>' % ext, 
            parse_mode=ParseMode.HTML)

        # create format keyboard
        keyboard = [['abort', 'full']]

        reply = update.message.reply_text(
            '<i>** select start / end ** { HH:MM:SS-HH:MM:SS }</i>', 
            parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))

        chat_data['ext'] = ext
        chat_data['last_message_id'] = reply.message_id

        return CHOOSE_LENGTH



    def handle_length_selection(bot, update, chat_data):
        
        length = update.message.text
        msg = update.message
        chat_id = msg.chat_id

        if length == 'abort': return handle_abort(bot, update, chat_data['last_message_id'])

        if length != 'full':
            if not src.utils.length_ok(length):
                return handle_error(bot, update, error_message='could not extract length from given input')

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
            parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))

        chat_data['length'] = length
        chat_data['last_message_id'] = reply.message_id

        return CHECKOUT



    def handle_checkout(bot, update, chat_data):

        confirmed = update.message.text
        msg = update.message
        chat_id = msg.chat_id

        if confirmed == 'abort': return handle_abort(bot, update, chat_data['last_message_id'])

        # remove previous messages
        bot.delete_message(chat_id=chat_id, message_id=chat_data['last_message_id'])
        bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        # send new message
        status_msg = bot.send_message(chat_id=chat_id, text='<i>.. processing (1/2) ..</i>', parse_mode=ParseMode.HTML)
        bot.send_chat_action(update.message.chat_id, action=ChatAction.RECORD_AUDIO)

        # download audio
        try:
            filename = src.utils.get_download(chat_data['url'], chat_data['ext'])
        except youtube_dl.utils.DownloadError as e:
            return handle_error(bot, update, error_message='failed to download audio as .%s' % chat_data['ext'])


        # update status message
        bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
        status_msg = bot.send_message(chat_id=chat_id, text='<i>.. sending audio (2/2) ..</i>', parse_mode=ParseMode.HTML)
        bot.send_chat_action(update.message.chat_id, action=ChatAction.UPLOAD_AUDIO)


        if not src.utils.size_ok(filename):
            """ File NOT OK """
            # remove please wait message
            bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
            # remove tmp file from disk
            src.utils.remove_file(filename)
            return handle_error(bot, update, error_message='The audio file is too large (max. 50MB)')
        else:
            """ File OK """
            # open audio file for transfer    
            try:
                with open(filename, 'rb') as audio:
                    log.info('Start transferring file %s to client' % filename)
                    bot.send_audio(chat_id=chat_id, audio=audio, timeout=180, **chat_data['metadata'])
                    log.info('Finished transferring file %s' % filename)
            except FileNotFoundError as e:
                    return handle_error(bot, update, error_message='failed to send audio as .%s' % chat_data['ext'])

        # add download to history
        src.history.add_history(chat_data['url'])
        # remove please wait message
        bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
        # remove tmp file from disk
        src.utils.remove_file(filename)

        return ConversationHandler.END



    return ConversationHandler(
        entry_points=[MessageHandler(Filters.all, handle_incoming_url, pass_chat_data=True)],

        states={
            CHOOSE_FORMAT: [MessageHandler(Filters.all, handle_format_selection, pass_chat_data=True)],
            CHOOSE_LENGTH: [MessageHandler(Filters.all, handle_length_selection, pass_chat_data=True)],

            CHECKOUT: [MessageHandler(Filters.all, handle_checkout, pass_chat_data=True)]
        },

        fallbacks=[CommandHandler('cancel', handle_cancel)],
        run_async_timeout=999
    )
