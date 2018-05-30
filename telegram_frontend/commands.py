#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging

""" Local modules """
import config
from core.core import WavesSpreadBot

""" 3th party modules """
from telegram import *

log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)

def handle_status(bot, update):
    log.debug('Handeling incoming command: /status')

    wsb = WavesSpreadBot.getInstance()

    update.message.reply_text('Waves Spread Bot is <b>{}</b>\n\n{} : {}\n{} : {}'.format(
                '\n ==> running' if wsb.getStatus() else 'not running',
                'UP'.ljust(10, '.'), wsb.getTotalUpTime(),
                'LAST'.ljust(10, '.'), wsb.getLastUpTime()
                ), parse_mode=ParseMode.HTML)

def handle_menu(bot, update):
    log.debug('Handeling incoming command: /menu')

    keyboard = [[InlineKeyboardButton('status', callback_data='status')], [InlineKeyboardButton('start', callback_data='start')], [InlineKeyboardButton('stop', callback_data='stop')]]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    update.message.reply_text('Select an action:', reply_markup=reply_markup)

def handle_start(bot, update):
    log.debug('Handeling incoming command /start')

    wsb = WavesSpreadBot.getInstance()
    wsb.start()


def handle_stop(bot, update):
    log.debug('Handeling incoming command /stop')

    wsb = WavesSpreadBot.getInstance()
    wsb.stop()


def handle_help(bot, update):
    log.debug('Handeling incoming command /help')
    update.message.reply_text("Use /status to test this bot.\nVersion 0.3")
