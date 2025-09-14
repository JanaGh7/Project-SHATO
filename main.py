import numpy as np
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import WhisperProcessor, WhisperForConditionalGeneration

app = FastAPI()

# Load once at module import (faster for repeated requests)
processor = WhisperProcessor.from_pretrained(
    "openai/whisper-tiny",
    language="en",     
    task="translate"  
)
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")

# Force the decoder prompt so the model ALWAYS translates to English
forced_ids = processor.get_decoder_prompt_ids(language='en', task="translate")
model.config.forced_decoder_ids = forced_ids

class SttRequest(BaseModel):
    audio_arr: List[float]
    samplerate: int
    
@app.post("/transcribe")
def transcribe_audio(req: SttRequest):
    # convert list -> numpy float32
    audio = np.array(req.audio_arr, dtype=np.float32)
    if audio.ndim > 1:
        audio = audio.squeeze()

    # ask the processor to pad (so it returns an attention_mask), and return pytorch tensors
    inputs = processor(audio, sampling_rate=req.samplerate, return_tensors="pt")

    input_features = inputs["input_features"]

    predicted_ids = model.generate(input_features)

    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    return {"transcription": transcription[0]}
