import websockets
import asyncio
import json
from dotenv import dotenv_values

access_code = dotenv_values(".env")

print(type(access_code['DEEPGRAM_ACCESS_CODE']))

async def listen():
    try:
        async with websockets.connect('wss://api.deepgram.com/v1/listen',
        # Remember to replace the YOUR_DEEPGRAM_API_KEY placeholder with your Deepgram API Key
        extra_headers = { 'Authorization': f"Token {str(access_code['DEEPGRAM_ACCESS_CODE'])}" }) as ws:
            # If the request is successful, print the request ID from the HTTP header
            print('🟢 Successfully opened connection')
            print(f'Request ID: {ws.response_headers["dg-request-id"]}')
            await ws.send(json.dumps({
                'type': 'CloseStream'
            }))
    except websockets.exceptions.InvalidStatusCode as e:
        # If the request fails, print both the error message and the request ID from the HTTP headers
        print(f'🔴 ERROR: Could not connect to Deepgram! {e.headers.get("dg-error")}')
        print(f'🔴 Please contact Deepgram Support with request ID {e.headers.get("dg-request-id")}')


asyncio.get_event_loop().run_until_complete(listen())