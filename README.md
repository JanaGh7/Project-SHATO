# Project-SHATO
MIA AI Training'26 Final Project: This project aims to transform SHATO, an autonomous robot, into an intelligent,  voice-controlled assistant.

## Robot Validator Service

This service validates robot commands against a strict schema.  
It ensures only known commands with correct parameters are accepted, and logs success/error messages.

---

### How to Run

1. Clone this repository:
   ```bash
   git clone https://github.com/JanaGh7/Project-SHATO.git
   cd Project-SHATO
   ```

2. Install dependencies:
  ```bash
   pip install -r requirements.txt
  ```
3. Start the service:
   ```bash
   uvicorn robot_validator:app --reload --port 9004
   ```

4. Open the API docs in your browser:
   http://127.0.0.1:9004/docs

5. Test:
   valid example:
   {
  "command": "move_to",
  "command_params": {"x": 5, "y": 7},
  "verbal_response": "Moving now"
}
