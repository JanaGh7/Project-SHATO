# client_record_and_send.py
import sounddevice as sd
import requests
import numpy as np

SERVER = "http://127.0.0.1:8000/transcribe"
samplerate = 16000
duration = 8

print("Recording for", duration, "seconds...")
rec = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
sd.wait()
audio = rec.squeeze().astype('float32').tolist()

resp = requests.post(SERVER, json={"audio_arr": audio, "samplerate": samplerate})
print("Server response:", resp.status_code, resp.text)
