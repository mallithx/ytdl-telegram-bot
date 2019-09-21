#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging

""" 3th party modules """
from telegram import *
from telegram.ext import * 

log = logging.getLogger(__name__)



def handler(bot, update, error):
    log.warning('Update "%s" caused error "%s"', update, error)