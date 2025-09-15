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
def validate_command(payload: LLMResponse, raw_output: dict = None):
    """
    Validate a robot command and log both success and errors.
    If raw_output is provided, it will be included in error logs.
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
            raise ValueError(f"Invalid command. Unknown command name '{payload.command}'")

        validated = params.model_dump()
        logger.info(f"[ROBOT-VALIDATOR-SUCCESS] Validated command '{payload.command}' with params {validated}")
        return validated

    except ValidationError as ve:
        errors = []
        for err in ve.errors():
            loc = err["loc"]
            if err["type"] == "missing":
                errors.append(f"Missing required key '{loc[-1]}'")
            elif err["type"] == "extra_forbidden":
                errors.append(f"Unexpected key '{loc[-1]}'")
            else:
                errors.append(f"{err['msg']}")
        msg = "; ".join(errors)

        # Prepare raw_output safely
        raw_output_str = raw_output if raw_output is not None else payload.model_dump()
        logger.error(f"[ROBOT-VALIDATOR-ERROR] Invalid command '{payload.command}'. Reason: {msg}")
        logger.error(f"[ROBOT-VALIDATOR-RAW-OUTPUT] Model output was:\n{raw_output_str}")

        raise ValueError(f"{msg}\nFull model output:\n{raw_output_str}")

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
