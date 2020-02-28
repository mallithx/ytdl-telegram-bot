#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Config Template

	PLEASE NOTE: You must rename this file to 'config.py' otherwise it will not work

"""
""" Standard modules """
import logging

""" (MANDATORY) Bot Token """
BOT_TOKEN = ''

""" (OPTIONAL) Development """
LOG_LEVEL = logging.DEBUG

""" (OPTIONAL) Telegram chat id to receive error reports from users """
SERVICE_ACCOUNT_CHAT_ID = ''

""" (OPTIONAL) Testing """
TEST_API_ID = 12345
TEST_API_HASH = 'get it from https://my.telegram.org'
TEST_BOT_USERNAME = 'my_bot_username'