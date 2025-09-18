from fastapi import FastAPI, HTTPException, Response
from schema import LLMRequest
import requests

app = FastAPI(title="LLM Brain")

LLM_SERVICE_URL = "http://llm-service:8000/generate_command"  # LLM service endpoint
VALIDATOR_SERVICE_URL = "http://validation-service:8000/execute_command"  # Validator service endpoint
TTS_URL = "http://tts-service:8000/tts"  # TTS service endpoint


@app.post("/process")
async def process_text(data: LLMRequest, response: Response):
    # Step 1: Call the LLM service
    try:
        llm_resp = requests.post(LLM_SERVICE_URL, json={"input_text": data.input_text})
        llm_resp.raise_for_status()
        raw_text = llm_resp.text
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"LLM service request failed: {e}")

    # Log the raw LLM output for debugging
    print("[LLM-RAW-OUTPUT]", raw_text)

    # Step 2: Send raw LLM text to Validator
    try:
        validator_resp = requests.post(VALIDATOR_SERVICE_URL, json={"raw_text": raw_text})
        status_code = validator_resp.status_code
        result = validator_resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Validator service request failed: {e}")

    # Step 3: Handle TTS based on validator status
    try:
        if status_code in (200, 360):
            tts_text = result.get("verbal_response", "")
        elif status_code in (400, 401):
            tts_text = "the llm didn't work properly, please try again"
            result["verbal_response"] = tts_text  # overwrite with static message
        else:
            tts_text = ""

        if tts_text:
            tts_resp = requests.post(TTS_URL, json={"text": tts_text})
            tts_resp.raise_for_status()
            result["audio_base64"] = tts_resp.json().get("audio_base64")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"TTS service request failed: {e}")

    # Preserve validator's status code
    response.status_code = status_code
    return result


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000)
