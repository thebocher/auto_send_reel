from io import BytesIO
import logging

import requests

from telethon import TelegramClient, events
from telethon.types import TypeInputPeer

from dotenv import load_dotenv

import os


load_dotenv()

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)

api_id = int(os.environ['API_ID']) 
api_hash = os.environ['API_HASH']

client = TelegramClient('name', api_id, api_hash)

owner = int(os.environ['OWNER'])

allowed_senders = [owner]


def get_video_file_from_instagram(url: str):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "dpr": "2",
        "pragma": "no-cache",
        "priority": "u=0, i",
        "sec-ch-prefers-color-scheme": "dark",
        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
        "sec-ch-ua-full-version-list": "\"Chromium\";v=\"128.0.6613.84\", \"Not;A=Brand\";v=\"24.0.0.0\", \"Google Chrome\";v=\"128.0.6613.84\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": "\"\"",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-ch-ua-platform-version": "\"13.2.0\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "viewport-width": "282",
        "cookie": "ds_user_id=2271272422; fbm_124024574287414=base_domain=.instagram.com; ig_did=66D4D3B0-6FB4-48F8-A70A-96C8CC52B615; mid=ZcLRSAAEAAEfH8noRuAey0-5A5dg; datr=HFTnZSzO5fRtAg8Iq_gem4nh; csrftoken=b9No9gDrcBaDQgKfN0WvP6ZUj17A9uLE; shbid=\"19732\\0542271272422\\0541756299586:01f76329bce88e339a7fff54452e63f53ff965ebce9bdaf3b14c582a2edd2cd089c726c0\"; shbts=\"1724763586\\0542271272422\\0541756299586:01f7f478327b4dd57e2663d284ff4810a18e1de094bf91e850d15d6cb0bfcf71c667ee9c\"; sessionid=2271272422%3A9xgNS5PoMlDQbs%3A17%3AAYdwbW0sagfsd29TzGkT-3khg6X39JevkP6eYzP8ooA0; oo=v1%7C3%3A1725014183; wd=282x754; rur=\"LDC\\0542271272422\\0541756555066:01f73d9e3b260d97f55696a8f4607447b9a0adf034fdb579b23e989e261ee66d88d96336\""
    }
    response = requests.get(
        url, 
        params={'__a': 1, '__d': 'dis'},
        headers=headers
    )
    json = response.json()
    video_url = max(
        *json['items'][0]['video_versions'],
        key=lambda v: v.get('height', 0)
    )['url']
    video_content = requests.get(video_url).content
    io = BytesIO(video_content)
    io.name = 'video.mp4'
    return io

@client.on(events.NewMessage())
async def handler(event: events.NewMessage.Event):
    peer: TypeInputPeer = await event.get_input_chat()
    peer_id = (
        getattr(peer, 'channel_id', None)
        or getattr(peer, 'chat_id', None)
        or peer.user_id
    )
    
    from_id = event.message.from_id
    sender_id = None

    if from_id:
        sender_id = from_id.user_id
    elif event.is_private:
        sender_id = owner
    else:
        sender_id = None
    
    logging.info(f'{peer_id} {sender_id} {event.message.message}')
    
    if sender_id not in allowed_senders:
        return
    
    text = event.message.message
    
    if text is None or not text.startswith('http'):
        return
    
    thread_id = event.message.reply_to_msg_id

    if sender_id == owner:
        await event.message.delete()
    
    file = get_video_file_from_instagram(text)
    
    await event.message.respond(file=file, reply_to=thread_id)


with client:
    client.run_until_disconnected()
    
# asyncio.run(main())