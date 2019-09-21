#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import subprocess
import logging

""" 3th party modules """
from telegram import *
from telegram.ext import * 

log = logging.getLogger(__name__)



def handle_start(bot, update):
    """ Handle /start command """
    update.message.reply_text(
        text='<strong>Audio Downloader</strong>\n<i>v2019.06.19</i>\n\n<strong>Share a link or enter a URL to download audio file.</strong>\n\nyoutube.com \u2714\nsoundcloud.com \u2714\n\nUse /update to fetch most recent youtube-dl /version.', 
        parse_mode=ParseMode.HTML)




def handle_version(bot, update):
    """ Handle /version command """ 
    try:
        resp = subprocess.check_output(['youtube-dl', '--version'])
        version = resp.decode('utf-8')
        update.message.reply_text(
            text='<strong>youtube-dl:</strong> %s' % version,
            parse_mode=ParseMode.HTML)
    except subprocess.CalledProcessError as e:
        update.message.reply_text(
            text='<i>Failed to determine version of youtube-dl</i>\n%r' % e,
            parse_mode=ParseMode.HTML)	 




def handle_update(bot, update):
    """ Handle /update command """
    try:
        resp = subprocess.check_output(['pip', 'install', 'youtube-dl', '--upgrade'])
        resp = resp.decode('utf-8')
        update.message.reply_text(
            text=resp,
            parse_mode=ParseMode.HTML)
    except subprocess.CalledProcessError as e:
        update.message.reply_text(
            text='<i>Failed to update youtube-dl</i>\n%r' % e,
            parse_mode=ParseMode.HTML)