from schema import *
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
import logging

# Configure logging so only the message is printed (no timestamps, levels etc.)
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Robot Validator")


#just for checking if it works well
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/execute_command")
def execute_command(payload: LLMResponse):
    try:
        if payload.command == "move_to":
            try:
                params = MoveToParams(**payload.command_params)
                validated = params.model_dump() # dictionary with validated fields
            except ValidationError as ve:
                for err in ve.errors(): # catch missing or extra parameters
                    if err["type"] == "missing":
                        raise ValueError("Invalid params for 'move_to': Missing required key '%s'" % err["loc"][0])
                    if err["type"] == "extra_forbidden":
                        raise ValueError("Invalid params for 'move_to': Unexpected key '%s'" % err["loc"][0])
                raise ValueError("Invalid params for 'move_to': " + str(ve))

        elif payload.command == "rotate":
            try:
                params = RotateParams(**payload.command_params)
                validated = params.model_dump() # dictionary with validated fields
            except ValidationError as ve:
                for err in ve.errors(): # catch missing or extra parameters
                    if err["type"] == "missing":
                        raise ValueError("Invalid params for 'rotate': Missing required key '%s'" % err["loc"][0])
                    if err["type"] == "extra_forbidden":
                        raise ValueError("Invalid params for 'rotate': Unexpected key '%s'" % err["loc"][0])
                raise ValueError("Invalid params for 'rotate': " + str(ve))
            
        elif payload.command == "start_patrol":
            try:
                params = StartPatrolParams(**payload.command_params)
                validated = params.model_dump() # dictionary with validated fields
            except ValidationError as ve:
                for err in ve.errors(): # catch missing or extra parameters or invalid count value
                    if err["type"] == "missing":
                        raise ValueError("Invalid params for 'start_patrol': Missing required key '%s'" % err["loc"][0])
                    if err["type"] == "extra_forbidden":
                        raise ValueError("Invalid params for 'start_patrol': Unexpected key '%s'" % err["loc"][0])
                    if "repeat_count" in str(err["loc"]):
                        raise ValueError("Invalid params for 'start_patrol': " + err["msg"])
                raise ValueError("Invalid params for 'start_patrol': " + str(ve))
        else: # Invalid commend
            raise ValueError(f" Invalid command. Reason: unknown command name '{payload.command}'")

        # Success
        logger.info(
            f"[ROBOT-VALIDATOR-SUCCESS] Received and validated command: "
            f"'{payload.command}' with params {validated}"
        )

        return {
            "status": "validated",
            "command": payload.command,
            "params": validated
        }

    # Error
    except ValueError as e:
        logger.error(f"[ROBOT-VALIDATOR-ERROR] {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))