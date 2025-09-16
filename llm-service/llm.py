from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import os

app = FastAPI(title="LLM Service")

SYSTEM_PROMPT = """
You are a robot control system. Your task is to convert any input text instruction into a JSON object that matches this schema exactly:

{
    "command": "<command_name>",           # string: "move_to", "rotate", or "start_patrol"
    "command_params": {                    # object with parameters depending on the command
        ...
    },
    "verbal_response": "<text>"            # string describing what the robot will do
}

Command-specific rules for command_params:

1. "move_to":
   - x: float (coordinate X)
   - y: float (coordinate Y)

2. "rotate":
   - angle: float (degrees to rotate)
   - direction: "clockwise" or "counter-clockwise" only

3. "start_patrol":
   - route_id: string (any string identifier for the route)
   - speed: string (e.g., "slow", "medium", "fast")
   - repeat_count: integer >=1 or -1 (optional, default = 1)

Additional rules:
- Output must be **strict JSON only**, no extra text, no explanations.
- Use **double quotes** for all keys and string values.
- Include all required fields. Optional fields may be omitted if default values apply.
- Ensure numeric fields are numbers, not strings with text.
- Never include fields that are not in the schema.
- Always produce a "verbal_response" describing what the robot will do in natural language.
- if there are any missing parameter, fill it with "null" and don't add anything else.
- There is always a verbal response, describing what the robot will do in natural language. all the schemas include it.
- repeat_count must always be a non-negative integer (0 = never run, 1 = run once, 2 = run twice, etc.). Never output negative numbers.
- for the route_id, read the input and provide a string to describe the route_id. the input might not be ixplicit.
for example: if the input said the first rout, then the id is 1.
Example 1:
Input: "Move the robot to coordinates X=5, Y=10"
Output:
{
    "command": "move_to",
    "command_params": {"x": 5, "y": 10},
    "verbal_response": "Moving to coordinates X: 5, Y: 10"
}

Example 2:
Input: "Start patrol route 3 at slow speed twice"
Output:
{
    "command": "start_patrol",
    "command_params": {"route_id": "3", "speed": "slow", "repeat_count": 2},
    "verbal_response": "Initiating patrol route 3 at a slow pace with two repeats."
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