import youtube_dl

opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'tmp/%(id)s.%(ext)s',
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }
    ]
}

with youtube_dl.YoutubeDL(opts) as ydl:
    try:
        info = ydl.download(['https://youtu.be/NPv6HlLs7CI'])
    except youtube_dl.utils.DownloadError as e:
        print('Failed to download file')
