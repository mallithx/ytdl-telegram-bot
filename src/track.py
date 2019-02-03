#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Standard modules """
import logging
import subprocess
import json

""" Local modules """
import config

""" 3th party modules """

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)

class Track:

    def __init__(self, url):
        self.url = url

    def getinfo(self, done, error):
        """ Get info (--print-json) of given url """
        try:
            process = subprocess.check_output(['youtube-dl', '-s', self.url, '--print-json'])
            info = json.loads(process.decode('utf8'))

            # done
            log.debug('Successfully get info of "%s"' % self.url)
            done(info)

        except subprocess.CalledProcessError as e:
            log.error('Failed to get info of "%s"' % self.url)
            error(e)

    def download(self, done, error, ext='mp3'):
        """ Download best audio in given format and send it to telegram client """
        try:
            process = subprocess.check_output(['youtube-dl', self.url, '--print-json', '-f bestaudio', '-x', '--audio-format', ext, '--id'])
            data = json.loads(process.decode('utf8'))

            _id = data['id']
            self.filename = '%s.%s' % (_id, ext) # button data is limited to 64 bytes

            # done
            log.debug('Successfully downloaded "%s"' % self.filename)
            done()

        except subprocess.CalledProcessError as e:
            log.error('Failed to download "%s"' % self.filename)
            error(e)

    def delete(self, done, error):
        """ Delete audio file from disk """
        try:
            process = subprocess.check_output(['rm', '-f', self.filename])
            
            # done
            log.debug('Successfully deleted "%s"' % self.filename)
            done()

        except subprocess.CalledProcessError as e:
            log.error('Failed to delete "%s"' % self.filename)
            error(e)
        