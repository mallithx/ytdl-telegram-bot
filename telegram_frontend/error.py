#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging

""" Local modules """
import config

""" 3th party modules """


log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)

def handle(bot, update, error):
    log.warning('Update "%s" caused error "%s"', update, error)
