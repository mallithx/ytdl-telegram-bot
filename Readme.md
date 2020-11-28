<img src="preview.jpg" align="right" width="30%">

## ytdl-telegram-bot

This Telegram bot serves audio files from several sources e.g. YouTube and SoundCloud. 
Uses **_youtube-dl_** and **_python-telegram-bot_**. In the future this bot should be able to convert and cut the audio 
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
Request bot token from @BotFather. 
Modify **_config_template.py_** and rename to **_config.py_**.

## Run Application
```
python3 run.py [-h]
```
or
```
cp ytdl-telegram-bot.service /etc/systemd/system/
systemctl daemon-reload

systemctl start ytdl-telegram-bot.service
systemctl status ytdl-telegram-bot.service
```
