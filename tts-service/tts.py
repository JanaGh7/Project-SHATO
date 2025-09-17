from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from TTS.api import TTS
import base64
from io import BytesIO
import soundfile as sf

app = FastAPI(title="Coqui TTS Service")

tts_model = None

@app.on_event("startup")
def load_model():
    global tts_model
    tts_model = TTS(model_name="tts_models/en/ljspeech/vits--neon", progress_bar=False, gpu=False)
    tts_model.synthesizer.tts_config["use_phonemes"] = False
    tts_model.synthesizer.tts_config["phonemizer"] = None

class TTSRequest(BaseModel):
    text: str

@app.post("/tts")
def generate_tts(request: TTSRequest):
    try:
        wav = tts_model.tts(request.text)
        buffer = BytesIO()
        sf.write(buffer, wav, samplerate=22050, format="WAV")
        buffer.seek(0)
        audio_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        return {"status": "success", "audio_base64": audio_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
