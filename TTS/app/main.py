from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
import soundfile as sf
import uuid

app = FastAPI(title="TTS Service")

# Load models once when the service starts
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

# Dummy voice embedding
speaker_embedding = torch.randn(1, 512)

class TTSRequest(BaseModel):
    text: str

@app.post("/tts")
def generate_tts(request: TTSRequest):
    try:
        inputs = processor(text=request.text, return_tensors="pt")
        speech = model.generate_speech(inputs["input_ids"], speaker_embedding, vocoder=vocoder)

        filename = f"output_{uuid.uuid4().hex}.wav"
        sf.write(filename, speech.numpy(), samplerate=16000)

        return {"status": "success", "file": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
