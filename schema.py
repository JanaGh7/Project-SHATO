from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, Literal, Union

class LLMRequest(BaseModel):
    input_text: str

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

class LLMResponse(BaseModel):
    command: Literal["move_to", "rotate", "start_patrol"]
    command_params: Union[MoveToParams, RotateParams, StartPatrolParams]
    verbal_response: str
