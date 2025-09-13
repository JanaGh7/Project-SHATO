from schema import *
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Robot Validator")

# Validation function (for api.py)
def validate_command(payload: LLMResponse):
    try:
        if payload.command == "move_to":
            params = MoveToParams(**payload.command_params)
            validated = params.model_dump()
        elif payload.command == "rotate":
            params = RotateParams(**payload.command_params)
            validated = params.model_dump()
        elif payload.command == "start_patrol":
            params = StartPatrolParams(**payload.command_params)
            validated = params.model_dump()
        else:
            raise ValueError(f"Invalid command. Unknown command name '{payload.command}'")

        logger.info(f"[ROBOT-VALIDATOR-SUCCESS] Validated command '{payload.command}' with params {validated}")
        return validated

    except ValidationError as ve:
        errors = []
        for err in ve.errors():
            if err["type"] == "missing":
                errors.append(f"Missing required key '{err['loc'][0]}'")
            elif err["type"] == "extra_forbidden":
                errors.append(f"Unexpected key '{err['loc'][0]}'")
            elif "repeat_count" in str(err["loc"]):
                errors.append(f"{err['msg']}")
        msg = "; ".join(errors) if errors else str(ve)
        logger.error(f"[ROBOT-VALIDATOR-ERROR] {msg}")
        raise ValueError(msg)

# FastAPI endpoints (kept for independent testing)
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/execute_command")
def execute_command(payload: LLMResponse):
    try:
        validated = validate_command(payload)
        return {"status": "validated", "command": payload.command, "params": validated}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
