#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging

""" Local modules """
import config
from core.core import WavesSpreadBot

""" 3th party modules """


log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)

def handle_status(bot, update):
    log.debug('Handeling incoming command: /status')

    wsb = WavesSpreadBot.getInstance()

    update.message.reply_text('==========\n   Status   \n==========\n\nMore detailed status information will appear soon!\nStatus: {}'.format(wsb.getStatus()))

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
