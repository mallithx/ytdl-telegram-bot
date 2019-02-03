#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging

""" Local modules """
import config

""" 3th party modules """
from telegram import *
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)

class PleaseWaitMessage:

    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.msg = None

    def send(self):
        self.msg = self.bot.send_message(chat_id=self.chat_id, text='<i>... please wait ...</i>', parse_mode=ParseMode.HTML)

    def revoke(self):
        self.bot.delete_message(chat_id=self.chat_id, message_id=self.msg.message_id)