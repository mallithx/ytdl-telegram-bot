#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging
import re
import os
import uuid
import glob

""" 3th party modules """
import youtube_dl

WORKDIR = 'tmp'

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
    match = re.search('^[0-9]{2}:[0-9]{2}:[0-9]{2}-[0-9]{2}:[0-9]{2}:[0-9]{2}$', length)
    if match:
        l = length.split('-')
        if length_to_msec(l[1]) < length_to_msec(l[0]):
            return False
        else:
            return True

    return False

def length_to_msec(length):
    v = [int(x) for x in length.split(':')]
    return v[0]*60*60*1000 + v[1]*60*1000 + v[2]*1000

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

def get_download(url, preferred_format, length, progress_hooks=[]):
    if preferred_format == 'video': preferred_format = 'bestvideo+bestaudio/best'
    elif preferred_format == 'audio': preferred_format = 'bestaudio/best'

    filename = os.path.join(WORKDIR, str(uuid.uuid4()))
    opts = {
        'logger': logging.getLogger('youtube-dl'),
        'outtmpl': filename,
        'verbose': True,
        'format': preferred_format,
        'forceid': True,
        'progress_hooks': progress_hooks
    }

    # load audio information
    with youtube_dl.YoutubeDL(opts) as ydl:
        log.debug('Downloading with opts:\n%r' % opts)
        ydl.download([url])
        log.info('Downloaded file %s' % filename)

    filename = glob.glob(filename + '*') # workaround for unexpected extensions amend by youtube-dl
    return filename[0]

def remove_file(filename):
    try:
        os.remove(filename)
        log.info('Removed file %s' % filename)
    except:
        log.error('Failed to remove file %s' % filename)
