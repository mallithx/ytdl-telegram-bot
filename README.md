## Audio Downloader - Telegram Bot
Python based Telegram Bot that serves audio files from several web sources e.g. YouTube and Soundcloud. 
Uses **_youtube-dl_** and **_python-telegram-bot_**. In the future this Bot should be able to convert and cut the audio 
stream to a choosen format and length.

## Setup
#### **1. Install python-telegram-bot**
Follow installation instructions here: https://python-telegram-bot.org/
```
pip install python-telegram-bot
```

#### **2. Install youtube-dl**
Follow installation instructions here: https://ytdl-org.github.io/youtube-dl/index.html
```
pip install youtube_dl
```

#### **3. Set Bot-Token**
Modify **_config_template.py_** and rename to **_config.py_**.

## Run Application
```
python3 run.py
```
