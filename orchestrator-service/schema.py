from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, Literal, Dict, Any

class LLMRequest(BaseModel):
    input_text: Optional[str]

class LLMResponse(BaseModel):
    command: Optional[Literal["move_to", "rotate", "start_patrol"]]
    command_params: Dict[str, Any]
    verbal_response: Optional[str]
    audio_base64: Optional[str] = None

