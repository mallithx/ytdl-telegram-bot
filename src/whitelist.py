#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging
import os

""" local modules """
import config

log = logging.getLogger(__name__)



def get():
    """ 
        Get last X urls from .history file
    """
    if not os.path.isfile(config.WHITELIST):
        return None

    with open(config.WHITELIST, 'r') as wl:
        return wl.read()

def add(uid):
    with open(config.WHITELIST, 'a') as wl:
        wl.write(uid + '\n')
        log.info('Added %s to whitelist' % uid)


