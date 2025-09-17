import requests
import base64

url = "http://127.0.0.1:8000/tts"
data = {"text": "one two three four five six 1 2 3 4 5 6"}

response = requests.post(url, json=data).json()
audio_bytes = base64.b64decode(response["audio_base64"])

with open("output.wav", "wb") as f:
    f.write(audio_bytes)

print("Saved output.wav. Play it in any audio player.")
