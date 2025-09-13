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
        llm_response = LLMResponse(**result)
        validated_params = validate_command(llm_response)
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
