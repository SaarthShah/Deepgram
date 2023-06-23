# Importing Necessary Packages

from deepgram import Deepgram

import asyncio
from dotenv import dotenv_values
from pvrecorder import PvRecorder
import pyaudio
import time
import binascii
import wave
import struct


# Setting up the Deepgram API Key
access_code = dotenv_values(".env")
print(access_code['DEEPGRAM_ACCESS_CODE'])

# Set the audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

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
      deepgramLive = await deepgram.transcription.live({ 'punctuate': True, 'interim_results': False, 'language': 'en-US' })
    except Exception as e:
      print(f'Could not open socket: {e}')
      return
    
    deepgramLive.registerHandler(deepgramLive.event.CLOSE, lambda c: print(f'Connection closed with code {c}.'))
    # Listen for any transcripts received from Deepgram and write them to the console
    deepgramLive.registerHandler(deepgramLive.event.TRANSCRIPT_RECEIVED, print)
    print('WebSocket connection established')
    
    # Continuously stream audio data to Deepgram
    try:
      while True:          
        audio_data = audio_stream.read(CHUNK)
        with wave.open('fullaudio.wav', 'wb') as wav_file:
          wav_file.setparams((CHANNELS, 2, RATE, CHUNK, "NONE", "NONE"))
          wav_file.writeframes(audio_data)
          # Read the WAV file as binary data
        with open('fullaudio.wav', 'rb') as file:
          binary_data = file.readlines()
          # Send the binary data to deepgramLive
          deepgramLive.send(binary_data)
    except KeyboardInterrupt:
      pass

    await deepgramLive.finish()
    print(time.time() - current_timestamp)

# Run the WebSocket connection and audio streaming
asyncio.run(connect_and_stream_audio())
