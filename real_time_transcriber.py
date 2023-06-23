# Importing Necessary Packages

from deepgram import Deepgram

import asyncio
import aiohttp
from dotenv import dotenv_values
import json
from pvrecorder import PvRecorder
import struct
import time
import wave


# Setting up the Deepgram API Key
access_code = dotenv_values(".env")
print(access_code['DEEPGRAM_ACCESS_CODE'])

# Setting up the PvRecorder
recorder = PvRecorder(device_index=-1, frame_length=5120)


# Setting up the Websocket
async def main():
  # Initialize the Deepgram SDK
  deepgram = Deepgram(access_code['DEEPGRAM_ACCESS_CODE'])
  audio = []

  # Create a websocket connection to Deepgram
  # In this example, punctuation is turned on, interim results are turned off, and language is set to US English.
  try:
    deepgramLive = await deepgram.transcription.live({ 'punctuate': True, 'interim_results': False, 'language': 'en-US' })
  except Exception as e:
    print(f'Could not open socket: {e}')
    return

  # Listen for the connection to close
  deepgramLive.registerHandler(deepgramLive.event.CLOSE, lambda c: print(f'Connection closed with code {c}.'))

  # Listen for any transcripts received from Deepgram and write them to the console
  deepgramLive.registerHandler(deepgramLive.event.TRANSCRIPT_RECEIVED, print)

  current_timestamp = time.time()
  target_timestamp = current_timestamp + 10


  # Listen for the connection to open and send streaming audio from the URL to Deepgram
  recorder.start()
  while time.time() < target_timestamp:
    frame = recorder.read()
    audio.extend(frame)
  recorder.stop()
  recorder.delete()

  with wave.open('fullaudio.wav', 'w') as f:
    f.setparams((1, 2, 16000, 5120, "NONE", "NONE"))
    f.writeframes(struct.pack("h" * len(audio), *audio))
  with open('./fullaudio.wav', 'rb') as f:
            deepgramLive.send(f.readlines())
  await deepgramLive.finish()

  
  # Indicate that we've finished sending data by sending the customary zero-byte message to the Deepgram streaming endpoint, and wait until we get back the final summary metadata object
#   deepgramLive.send(struct.pack("h" * len(audio), *audio))

asyncio.run(main())