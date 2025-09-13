import requests
import json
import re

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
      "direction": "clockwise" | "counterclockwise"
  } OR {
      "route_id": str,
      "speed": str,
      "repeat_count": int
  },
  "verbal_response": str
}

Rules:
- Output ONLY valid JSON.
- Do not include explanations.
- Direction must be "clockwise" or "counterclockwise".

If you include anything outside a JSON object, the system will break.
"""

def parse_command(user_text: str):
    payload = {
        "model": "phi3:mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "stream": False
    }

    response = requests.post("http://ollama:11434/api/chat", json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Ollama error {response.status_code}: {response.text}")

    data = response.json()

    # New Ollama returns messages in choices
    raw_output = data.get("message", {}).get("content", "").strip()

    try:
        # Extract JSON inside curly braces
        match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in model output")

        clean_json = match.group(0)
        return json.loads(clean_json)

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}\nRaw output: {raw_output}")
