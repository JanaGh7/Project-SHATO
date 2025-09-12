# orchestrator-api/app/models.py
from typing import Dict, Any, Literal
from pydantic import BaseModel, ConfigDict

class ValidatorPayload(BaseModel):
 
    model_config = ConfigDict(extra="forbid")  # reject any unknown fields

    # Only allowed commands
    command: Literal["move_to", "rotate", "start_patrol"]

    # Parameters (validated in robot-validator service, not here)
    command_params: Dict[str, Any]
