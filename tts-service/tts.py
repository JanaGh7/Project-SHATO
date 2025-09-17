from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from TTS.api import TTS
import base64
from io import BytesIO
import soundfile as sf

app = FastAPI(title="Coqui TTS Service")

# Load model once
tts = TTS(model_name="tts_models/en/ljspeech/vits--neon", progress_bar=False, gpu=False)
tts.synthesizer.tts_config["use_phonemes"] = False
tts.synthesizer.tts_config["phonemizer"] = None
class TTSRequest(BaseModel):
    text: str

@app.post("/tts")
def generate_tts(request: TTSRequest):
    try:
        # Generate audio (numpy array)
        wav = tts.tts(request.text)

        # Write audio to memory buffer
        buffer = BytesIO()
        sf.write(buffer, wav, samplerate=22050, format="WAV")
        buffer.seek(0)

        # Encode as base64
        audio_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        return {"status": "success", "audio_base64": audio_base64}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
