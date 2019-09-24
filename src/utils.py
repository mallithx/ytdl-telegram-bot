#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging
import re
import os

""" 3th party modules """
import youtube_dl

log = logging.getLogger(__name__)



def parse_url(msg):
    """ Extract url from message """
    match = re.search('(?P<url>https?://[^\s]+)', msg)

    if match:
        return match.group('url')
    else:
        log.error('No URL found in "%s"' % msg)

    return msg

def size_ok(filename):
    size = os.path.getsize(filename)
    log.debug('File %s has a size of %d' % (filename, size))
    return size <= (1024 * 1024 * 50) # 50MB

def length_ok(length):
    return False

def get_info(url):
    opts = {
        'logger': logging.getLogger('youtube-dl'),
        'verbose': True,
        'format': 'bestvideo+bestaudio/best'
    }

    # load audio information
    with youtube_dl.YoutubeDL(opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)

    return info_dict

def get_download(url, ext, progress_hooks=[]):
    opts = {
        'logger': logging.getLogger('youtube-dl'),
        'outtmpl': 'tmp_audio',
        'verbose': True,
        'format': 'bestvideo+bestaudio/best',
        'forceid': True,
        'progress_hooks': progress_hooks,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': ext,
            'preferredquality': '192',
        }]
    }

    # load audio information
    with youtube_dl.YoutubeDL(opts) as ydl:
        log.debug('Downloading with opts:\n%r' % opts)
        ydl.download([url])
        filename = 'tmp_audio.%s' % ext
        log.info('Downloaded file %s' % filename)
        return filename

def remove_file(filename):
    try:
        os.remove(filename)
        log.info('Removed file %s' % filename)
    except:
        log.error('Failed to remove file %s' % filename)