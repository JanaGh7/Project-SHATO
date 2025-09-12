# Project-SHATO
MIA AI Training'26 Final Project: This project aims to transform SHATO, an autonomous robot, into an intelligent,  voice-controlled assistant.

## Robot Validator Service

This service validates robot commands against a strict schema.  
It ensures only known commands with correct parameters are accepted, and logs success/error messages.

## Orchestrator Service
This service is central nervous system. It routes data between LLM service and Robot Validator Service to ensure data is written exactly as the expected schema
---

### How to Run

1. Clone this repository:
   ```bash
   git clone https://github.com/JanaGh7/Project-SHATO.git
   cd Project-SHATO
   ```
2.Create a virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\activate    
```

3. Install dependencies:
  ```powershell
   pip install -r requirements.txt
  ```
4. Start the service:
For orchestrator:
py -m uvicorn app.main:app --reload --port 8100

For validator:
py -m uvicorn robot_validator:app --reload --port 8000

5.Open your browser and go to:

Orchestrator docs: http://127.0.0.1:8100/docs
Validator docs: http://127.0.0.1:8000/docs

6.You’ll see an interactive Swagger UI. From there:

Click on the POST /orchestrate endpoint (for orchestrator)

Click “Try it out”

Enter JSON in the body, for example:

{
  "command": "rotate",
  "command_params": { "angle": 90.0, "direction": "" }
}


Hit Execute and you’ll see the response directly.
