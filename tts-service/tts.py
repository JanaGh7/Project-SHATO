from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel 
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan 
import torch 
import soundfile as sf 
import base64
from io import BytesIO

app = FastAPI(title="TTS Service") 

# Load models once when the service starts 
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts") 
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts") 
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan") 

# Dummy voice embedding 
speaker_embedding = torch.randn(1, 512)  # neutral voice

class TTSRequest(BaseModel): 
    text: str
    
@app.post("/tts") 
def generate_tts(request: TTSRequest): 
    try: 
        inputs = processor(text=request.text, return_tensors="pt") 
        speech = model.generate_speech(inputs["input_ids"], speaker_embedding, vocoder=vocoder) 

        buffer = BytesIO()
        sf.write(buffer, speech.numpy(), samplerate=16000, format="WAV")
        audio_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {"status": "success", "audio_base64": audio_base64}
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))
    