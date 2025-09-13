import requests
import json
import re
import os

SYSTEM_PROMPT = """
You are a robot command parser.
You take natural language instructions and map them to a structured schema.

Schema:
{
  "command": "move_to | rotate | start_patrol",
  "command_params": {
      "x": int,
      "y": int
  } OR {
      "angle": int,
      "direction": "clockwise" | "counter-clockwise"
  } OR {
      "route_id": str,
      "speed": str,
      "repeat_count": int
  },
  "verbal_response": str
}

Rules:
- Output ONLY a single valid JSON object.
- Do not include explanations or text outside the JSON.
- Direction must be "clockwise" or "counter-clockwise".
- If unsure, pick valid defaults rather than inventing extra fields.
- in "verbal_response" say a verbal response the your input
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
