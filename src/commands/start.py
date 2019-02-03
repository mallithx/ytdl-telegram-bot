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

def handle_start(bot, update, chat_data):
    log.debug('chat_data 1:\n{}'.format(chat_data))

    update.message.reply_text(
        text='<strong>How to start?</strong>\nshare a link !', 
        parse_mode=ParseMode.HTML)

