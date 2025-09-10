from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError, field_validator, ConfigDict
from typing import Optional, Literal
import logging

# Configure logging so only the message is printed (no timestamps, levels etc.)
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Robot Validator")

# Define each command and its parameters
class MoveToParams(BaseModel):
    model_config = ConfigDict(extra="forbid") # Extra parameters are forbidden
    x: float
    y: float

class RotateParams(BaseModel):
    model_config = ConfigDict(extra="forbid") # Extra parameters are forbidden
    angle: float
    direction: Literal["clockwise", "counter-clockwise"] # Only allowed values

class StartPatrolParams(BaseModel):
    model_config = ConfigDict(extra="forbid") # Extra parameters are forbidden
    route_id: Literal["first_floor", "bedrooms", "second_floor"] # Only allowed values
    speed: Optional[Literal["slow", "medium", "fast"]] = "medium" # Only allowed values, default -> Medium
    repeat_count: Optional[int] = 1

    @field_validator("repeat_count")
    def check_repeat(cls, v):
        if v is None:
            return 1 # default value
        if v == -1 or v >= 1: # allowed values
            return v
        raise ValueError("repeat_count must be >=1 or -1")

class CommandPayload(BaseModel):
    command: str # Command itself (validated in code)
    command_params: dict # parameters
    verbal_response: str # text the robot will say

@app.post("/execute_command")
def execute_command(payload: CommandPayload):
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