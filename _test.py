import logging
import subprocess
from io import BytesIO

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
        if self.binary_data is not None:
            print('Skipping download because binary_data is already present.')
            return

        resp = subprocess.check_output(['youtube-dl', \
            '-f bestaudio', \
            '-q', # quiet \ 
            '-o', '-', # stdout \
            self.url])

        self.binary_data = resp

    def cut_audio(self, start=0, end=0):
        p = subprocess.Popen(['ffmpeg', \
            '-i', 'pipe:0', \
            '-ss', start, # quiet \ 
            '-to', end, \
            '-f', 'mp3', \
            '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        stdout = p.communicate(input=BytesIO(self.binary_data).read())[0]
        print(stdout)



audio = AudioFile('https://www.youtube.com/watch?v=hHT_hEuTtxg')
print('Audio file created')
audio.download()
print('Audio file downloaded')
audio.cut_audio(start='00:00:05', end='00:00:10')
print('Audio file cutted')



