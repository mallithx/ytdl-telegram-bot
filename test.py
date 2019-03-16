import logging
import subprocess

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class AudioFile:

    def __init__(self, url):
        self.url = url
        self.info = None
        self.binary_data = None

    def check_url(self):
        try:
            resp = subprocess.check_output(['youtube-dl', \
                '-sq', # simulate + quiet \ 
                self.url])

            return True
        except subprocess.CalledProcessError as e:
            log.error(e)
            return False


    def get_info(self):
        resp = subprocess.check_output(['youtube-dl', \
            '-sq', # simulate + quiet \ 
            '--get-title', \
            '--get-duration', \
            '--get-thumbnail', \
            self.url])

        info = resp.split(b'\n')
        self.info = {
            'title': info[0],
            'duration': info[2],
            'thumbnail': info[1]
        }
    
    def download(self):
        resp = subprocess.check_output(['youtube-dl', \
            '-q', # quiet \ 
            '-o', '-', # stdout \
            self.url])

        self.binary_data = resp



audio = AudioFile('https://www.dfgyoutube.com/watch?v=hHT_hEuTtxg')
audio.check_url()


