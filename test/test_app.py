import asyncio

from telethon import TelegramClient, events

import config

TEST_URLS = [
    'https://www.youtube.com/watch?v=t-f-gq1gD3A'
]

client = TelegramClient('test/test_session', config.TEST_API_ID, config.TEST_API_HASH)
async def main():
    await client.send_message(config.TEST_BOT_USERNAME, TEST_URLS[0])   

with client:    
    client.loop.run_until_complete(main())