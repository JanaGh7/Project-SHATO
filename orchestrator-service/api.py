from fastapi import FastAPI, HTTPException
from schema import LLMRequest, LLMResponse
from pydantic import ValidationError
import requests

app = FastAPI(title="LLM Brain")

LLM_SERVICE_URL = "http://llm-service:8000/generate_command"  # LLM service endpoint
VALIDATOR_SERVICE_URL = "http://validation-service:8000/execute_command"  # Validator service endpoint
TTS_URL = "http://tts-service:8000/tts"  # TTS service endpoint


@app.post("/process", response_model=LLMResponse)
async def process_text(data: LLMRequest):
    # Step 1: Call the LLM service
    try:
        llm_resp = requests.post(LLM_SERVICE_URL, json={"input_text": data.input_text})
        if llm_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="LLM service failed")
        result = llm_resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"LLM service request failed: {e}")

    # Log the raw LLM output for debugging
    print("[LLM-RAW-OUTPUT]", result)

    # Step 2: Validate the LLM response via validator service
    try:
        validator_resp = requests.post(VALIDATOR_SERVICE_URL, json=result)
        if validator_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Validator service failed")
        validated_params = validator_resp.json().get("params")
        result["command_params"] = validated_params
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Validator service request failed: {e}")

    # Step 3: Call TTS service
    try:
        tts_resp = requests.post(TTS_URL, json={"text": result.get("verbal_response", "")})
        if tts_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="TTS service failed")
        result["audio_base64"] = tts_resp.json().get("audio_base64")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"TTS service request failed: {e}")

    return result


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000)
 