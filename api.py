from fastapi import FastAPI, HTTPException
from schema import *
from schema import LLMRequest, LLMResponse
from llm import parse_command
from robot_validator import validate_command  # import the validation function
from pydantic import ValidationError
import requests

app = FastAPI(title="LLM Brain")
TTS_URL = "http://tts-service:8000/tts"  # points to your TTS container


@app.post("/process", response_model=LLMResponse)
async def process_text(data: LLMRequest):
    # Step 1: Call the LLM
    result = parse_command(data.input_text)

    # Log the raw LLM output for debugging
    print("[LLM-RAW-OUTPUT]", result)

    # Step 2: Validate the LLM response using robot_validator
    try:
        llm_response = LLMResponse(**result)
        validated_params = validate_command(llm_response)
        result["command_params"] = validated_params
        tts_resp = requests.post(TTS_URL, json={"text": llm_response.verbal_response})
        if tts_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="TTS service failed")
        # Add audio to result
        result["audio_base64"] = tts_resp.json().get("audio_base64")
        return result
    except (ValidationError, ValueError) as e:
        # Include full LLM output in the error for debugging
        error_msg = f"Validation failed: {e}\nFull LLM output: {result}"
        # print("[LLM-VALIDATION-ERROR]", error_msg)
        raise HTTPException(status_code=400, detail=error_msg)


@app.get("/health")
def health():
    return {"status": "ok"}


# Run with: uvicorn app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
