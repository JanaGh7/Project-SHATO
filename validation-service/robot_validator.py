from schema import *
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging, json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Robot Validator")

# Validation function (for api.py)
def validate_command(payload: LLMResponse, raw_output: dict = None):
    """
    Validate a robot command. Returns (validated_params, error_message or None).
    """
    try:
        # Ensure command_params is a dict
        params_data = payload.command_params
        if isinstance(params_data, BaseModel):
            params_data = params_data.model_dump()

        if payload.command == "move_to":
            params = MoveToParams(**params_data)
        elif payload.command == "rotate":
            params = RotateParams(**params_data)
        elif payload.command == "start_patrol":
            params = StartPatrolParams(**params_data)
        else:
            return None, f"Invalid command '{payload.command}'"

        validated = params.model_dump()
        return validated, None

    except ValidationError as ve:
        # Collect error messages
        errors = []
        for err in ve.errors():
            loc = err["loc"]
            if "missing" in err["type"]:
                errors.append(f"Missing required key '{loc[-1]}'")
            elif "extra_forbidden" in err["type"]:
                errors.append(f"Unexpected key '{loc[-1]}'")
            else:
                errors.append(f"{err['msg']}")
        return None, "; ".join(errors)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/execute_command")
async def execute_command(request: Request):
    """
    Validator endpoint.
    """
    thing = await request.json()
    raw_text = thing.get("raw_text")
    if isinstance(raw_text, str):
        payload = json.loads(raw_text)
    else:
        payload = raw_text

    try:
        # Try parsing into LLMResponse (will fail if JSON schema is totally wrong)
        llm_payload = LLMResponse(**payload)
        # Extra guard: if command is missing or null → treat as invalid command
        if not llm_payload.command or (llm_payload.command not in ['move_to', 'rotate', 'start_patrol']):
            status_message = "[ROBOT-VALIDATOR-ERROR] Invalid command. Reason: Command is missing or invalid"
            response = payload.copy()
            response["status_message"] = status_message
            return JSONResponse(status_code=360, content=response)
        
    except Exception:
        # Case 3: JSON is invalid
        return JSONResponse(
            status_code=400,
            content={
                "status_message": "[LLM-VALIDATOR-ERROR]: the LLM couldn't generate a correct json. please try again"
            }
        )

    # Case 1 & 2: JSON valid, now validate params
    validated, error = validate_command(llm_payload, raw_output=payload)

    if error is None:
        # Case 1: success
        status_message = (
            f"[ROBOT-VALIDATOR-SUCCESS] Validated command '{llm_payload.command}' "
            f"with params {json.dumps(validated)}"
        )
        response = llm_payload.model_dump()
        response["command_params"] = validated
        response["status_message"] = status_message
        return JSONResponse(status_code=200, content=response)

    else:
        # Case 2: valid JSON but missing/extra/invalid params
        status_message = (
            f"[ROBOT-VALIDATOR-ERROR] Invalid command '{llm_payload.command}'. Reason: {error}"
        )
        response = llm_payload.model_dump()
        response["status_message"] = status_message
        return JSONResponse(status_code=360, content=response)
