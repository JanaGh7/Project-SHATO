"""
app.py - LLM Brain FastAPI skeleton with dummy mapping logic.

This single-file example includes:
- Pydantic models for request/response (with validation constraints)
- A small set of parsing helpers that convert natural-language text -> one of three commands
  (move_to, rotate, start_patrol). These are dummy heuristics you will later replace with an LLM.
- A /predict POST endpoint that returns a validated response_model
- A /health GET endpoint

Run locally:
    pip install -r requirements.txt
    uvicorn app:app --reload

Example requests (using curl):
    curl -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" \
      -d '{"input_text": "move to x=10 y=20"}'

    curl -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" \
      -d '{"input_text": "rotate clockwise 90 degrees"}'

    curl -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" \
      -d '{"input_text": "start patrol on route A at fast speed repeat 2 times"}'

Notes:
- This file is intentionally self-contained so your teammates can run and test the API quickly.
- Next steps: replace the parsing helpers with your quantized LLM call and keep the same endpoint/schema.
"""

from fastapi import FastAPI, HTTPException
from schema import *
from schema import LLMRequest, LLMResponse
from llm import parse_command
from robot_validator import validate_command  # import the validation function


app = FastAPI(title="LLM Brain")


@app.post("/process", response_model=LLMResponse)
async def process_text(data: LLMRequest):
    # Step 1: Call the LLM
    result = parse_command(data.input_text)

    # Step 2: Validate the LLM response using robot_validator
    try:
        validated_params = validate_command(result)
        result.command_params = validated_params
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}


# Run with: uvicorn app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
