import youtube_dl


ydl = youtube_dl.YoutubeDL()
with ydl:
    try:
        info = ydl.download(['https://www.youtube.com/watch?v=zk1QNXTGldQ'])
    except youtube_dl.utils.DownloadError as e:
        printf('Failed to download file')

print('Terminated with: ', info)