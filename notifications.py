import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "debtsBack.settings")
django.setup()

import asyncio
import json
from typing import Dict, List

import aioredis
import websockets

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError


CONNECTIONS: Dict[str, List[websockets.WebSocketServerProtocol]] = {}

EVENT_CONNECTED = {'event': 'connection_established'}


def authenticate(raw_token: str) -> str:
    token = AccessToken(raw_token, verify=True)
    return token['user_id']


async def handler(websocket: websockets.WebSocketServerProtocol) -> None:
    raw_token = await websocket.recv()
    try:
        user_id = authenticate(raw_token)
    except TokenError as exc:
        error_message = str(exc)
        await websocket.send(error_message)

        await websocket.close()
        return
    else:
        await websocket.send(json.dumps(EVENT_CONNECTED))

    if not CONNECTIONS.get(user_id):
        CONNECTIONS[user_id] = [websocket]
    else:
        CONNECTIONS[user_id].append(websocket)

    try:
        await websocket.wait_closed()
    finally:
        CONNECTIONS[user_id].remove(websocket)


async def notify_events():
    redis = aioredis.from_url("redis://127.0.0.1:6379/1")
    pubsub = redis.pubsub()
    await pubsub.subscribe("events")
    async for message in pubsub.listen():
        if message["type"] != "message":
            continue

        payload = message['data'].decode()
        events = json.loads(payload)
        print(events)
        for event in events:
            user_id = event['user_id']
            event_data = event['data']
            if user_websockets := CONNECTIONS.get(user_id):
                websockets.broadcast(user_websockets, json.dumps(event_data))


async def main():
    async with websockets.serve(handler, 'localhost', 8888):
        await notify_events()


if __name__ == '__main__':
    asyncio.run(main())
