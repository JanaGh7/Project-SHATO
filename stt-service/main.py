import numpy as np
import soundfile as sf
import io
from fastapi import FastAPI, UploadFile, File
from transformers import WhisperProcessor, WhisperForConditionalGeneration

app = FastAPI()

# Load Whisper model once
processor = WhisperProcessor.from_pretrained("openai/whisper-tiny", language="en", task="translate")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")
forced_ids = processor.get_decoder_prompt_ids(language="en", task="translate")
model.config.forced_decoder_ids = forced_ids

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Read WAV file
    audio_bytes = await file.read()
    audio, samplerate = sf.read(io.BytesIO(audio_bytes), dtype="float32")

    # Ensure mono
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    inputs = processor(audio, sampling_rate=samplerate, return_tensors="pt")
    predicted_ids = model.generate(inputs["input_features"])
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

    return {"transcription": transcription[0]}
