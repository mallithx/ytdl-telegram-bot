#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging
import os


log = logging.getLogger(__name__)



def get_history(size=10):
    """ 
        Get last X urls from .history file
    """
    if not os.path.isfile('.history'):
        return None

    with open('.history', 'r') as history:
        return history.read()

def add_history(url):
    with open('.history', 'a') as history:
        history.write(url + '\n')
        log.info('Added %s to history' % url)

def clear_history(url):
    os.remove(url)
    log.info('Cleared history')


