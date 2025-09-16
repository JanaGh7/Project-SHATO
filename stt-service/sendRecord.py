import sounddevice as sd
import soundfile as sf
import requests

SERVER = "http://127.0.0.1:5001/transcribe"
samplerate = 16000
duration = 5
filename = "recorded.wav"

print(f"🎙️ Recording {duration} seconds...")
rec = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="float32")
sd.wait()

# Save to file
sf.write(filename, rec, samplerate)
print(f"✅ Saved recording to {filename}")

# Send to STT service
with open(filename, "rb") as f:
    resp = requests.post(SERVER, files={"file": f})

print("📝 Transcription:", resp.json())
