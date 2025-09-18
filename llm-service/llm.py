from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import os

app = FastAPI(title="LLM Service")

SYSTEM_PROMPT = """
You are a robot control system. Your task is to convert any input text instruction into a JSON object that matches this schema exactly:

{
    "command": "<command_name>",           # string: "move_to", "rotate", "start_patrol" OR null
    "command_params": { ... } OR {},     # object with parameters OR {} if command is null
    "verbal_response": "<text>"            # string describing what the robot will do
}

Command-specific rules for command_params:

1. "move_to":
   - x: float (coordinate X) - REQUIRED
   - y: float (coordinate Y) - REQUIRED

2. "rotate":
   - angle: float (degrees to rotate) - REQUIRED
   - direction: "clockwise" or "counter-clockwise" only - REQUIRED

3. "start_patrol":
   - route_id: "first_floor", "bedrooms", "second_floor" only - REQUIRED
   - speed: "slow", "medium", "fast" only (optional, default: "medium")
   - repeat_count: integer >=1 or -1 for continues patrols (optional, default: 1)

CRITICAL RULES:
- If the user input DOES NOT match any of the three valid commands, set "command" to null and "command_params" to {}.
- If the user input matches a command but is missing required parameters or the parameters are invalid, set "command" to the intended command but set "command_params" to {}, and "vebral_response" should expalin what the user did wrong.
- There is ALWAYS a "verbal_response" that explains the situation to the user.
- Output must be **strict JSON only**, no extra text, no explanations.
- Use **double quotes** for all keys and string values.
- IF a parameter has a default value, you have to assign it if the user didn't specify.
- If the user didn't specify a route_id explicitly, treat it as a missing parameter and don't assume one. don't use default value. and say in the "verbal_response" that you can't start the patrol without a route_id
- If the user used wrong route_id, say in the "verbal_response" that the user should use a valid route_id and set "params" to {}
- IF user didn't specify any of the required params, set "command_params" to {} and say in the "verbal_response" that the user failed to inter something requried and say what was it.
- Don't say "I'm sorry" in the "verbal_response".

EXAMPLES OF ERROR HANDLING:

Example 1: Invalid command
Input: "Make me a sandwich"
Output:
{
    "command": null,
    "command_params": {},
    "verbal_response": "I'm sorry, I can only process move, rotate, or patrol commands. Please try again with a valid command."
}

Example 2: Missing required parameter
Input: "Move the robot to X=5"
Output:
{
    "command": "move_to",
    "command_params": {},
    "verbal_response": "I understand you want to move, but I need both X and Y coordinates. Please specify the Y coordinate."
}

Example 3: Valid command
Input: "Move the robot to coordinates X=5, Y=10"
Output:
{
    "command": "move_to",
    "command_params": {"x": 5, "y": 10},
    "verbal_response": "Moving to coordinates X: 5, Y: 10"
}

Example 4: Valid command with defaults
Input: "Start patrol on first floor"
Output:
{
    "command": "start_patrol",
    "command_params": {"route_id": "first_floor", "speed": "medium", "repeat_count": 1},
    "verbal_response": "Initiating patrol route first_floor at medium speed for 1 repeat."
}
"""

# Use environment variable for Docker Compose networking
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")


def extract_first_json(raw_output: str):
    stack = []
    start_idx = None
    for i, char in enumerate(raw_output):
        if char == '{':
            if not stack:
                start_idx = i
            stack.append('{')
        elif char == '}':
            stack.pop()
            if not stack and start_idx is not None:
                return raw_output[start_idx:i+1]  # full JSON block
    raise ValueError(f"No valid JSON found in model output:\n{raw_output}")


def parse_command(user_text: str):
    payload = {
        "model": "phi3:mini",
        "format": "json",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "stream": False
    }

    response = requests.post(f"{OLLAMA_URL}/api/chat", json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Ollama error {response.status_code}: {response.text}")

    data = response.json()
    raw_output = data.get("message", {}).get("content", "").strip()

    try:
        clean_json = extract_first_json(raw_output)
        return json.loads(clean_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}\nRaw output: {raw_output}")


class LLMRequest(BaseModel):
    input_text: str


@app.post("/generate_command")
async def generate_command(req: LLMRequest):
    try:
        result = parse_command(req.input_text)
        # Print to logs when running standalone
        print("[LLM-OUTPUT]", json.dumps(result, indent=2))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}