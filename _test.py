import youtube_dl

opts = {
    'format': 'bestaudio/best',
    'outtmpl': '-'
}

with youtube_dl.YoutubeDL(opts) as ydl:
    try:
        info = ydl.download(['https://www.youtube.com/watch?v=zk1QNXTGldQ'])
    except youtube_dl.utils.DownloadError as e:
        print('Failed to download file')

print()