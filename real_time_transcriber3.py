from deepgram import Deepgram
import asyncio
from dotenv import dotenv_values
import pyaudio
import time
import json
import base64
import numpy as np

# Setting up the Deepgram API Key
access_code = dotenv_values(".env")
print(access_code['DEEPGRAM_ACCESS_CODE'])

# Set the audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 3200

current_timestamp = time.time()
target_timestamp = current_timestamp + 10
deepgram = Deepgram(access_code['DEEPGRAM_ACCESS_CODE'])

# Create the PyAudio audio stream
audio_stream = pyaudio.PyAudio().open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

# WebSocket connection function
async def connect_and_stream_audio():
    try:
        deepgramLive = await deepgram.transcription.live({'punctuate': True, 'interim_results': False, 'language': 'en-US', 'encoding': 'linear16'})
    except Exception as e:
        print(f'Could not open socket: {e}')
        return

    deepgramLive.registerHandler(deepgramLive.event.CLOSE, lambda c: print(f'Connection closed with code {c}.'))
    # Listen for any transcripts received from Deepgram and write them to the console
    deepgramLive.registerHandler(deepgramLive.event.TRANSCRIPT_RECEIVED, print)
    print('WebSocket connection established')

    try:
        while True:
            await asyncio.sleep(0.1)
            audio_data = audio_stream.read(CHUNK)
            audio_data_linear16 = (np.frombuffer(audio_data, dtype=np.int16) * 32767).astype(np.int16)
            audio_data_linear16 = base64.b64encode(audio_data_linear16)
            # print(audio_data_linear16)
            deepgramLive.send(audio_data_linear16)

            # deepgramLive.send(json.dumps({'type': 'KeepAlive'}))

    except KeyboardInterrupt:
        pass

    # await deepgramLive.finish()
    audio_stream.stop_stream()
    audio_stream.close()
    print(time.time() - current_timestamp)

# Run the WebSocket connection and audio streaming
asyncio.run(connect_and_stream_audio())
