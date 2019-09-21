#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging
import re

""" 3th party modules """
from telegram import *
from telegram.ext import * 

log = logging.getLogger(__name__)



def parse_url(msg):
    """ Extract url from message """
    match = re.search('(?P<url>https?://[^\s]+)', msg)

    if match:
        return match.group('url')
    else:
        log.error('No URL found in "%s"' % msg)

    return msg