# Project-SHATO
MIA AI Training'26 Final Project: This project aims to transform SHATO, an autonomous robot, into an intelligent,  voice-controlled assistant.

## Project Files and Their Roles

- **api.py**: Main FastAPI application that handles `/process` POST requests and `/health` checks. Connects the LLM output with the robot validator.  
- **robot_validator.py**: Validates commands against a strict schema, logs successes and errors, and ensures only correct parameters are accepted.  
- **llm.py**: Interfaces with the language model (Ollama), parses natural language input into structured JSON commands.  
- **schema.py**: Defines Pydantic models for command validation and response structure, ensuring type safety and strict parameter checks.  
- **Dockerfile**: Builds the `llm-service` container with Python environment and dependencies.  
- **docker-compose.yml**: Orchestrates the multi-container setup including `ollama` and `llm-service`, exposing necessary ports and handling dependencies.  
- **ollama-entrypoint.sh**: Custom entrypoint script for the Ollama container that starts the server and pulls required models if missing.  
- **requirements.txt**: Lists Python dependencies for the FastAPI service.  

---

The project provides a Docker setup so that all dependencies, models, and services are installed automatically.

### How to Run

1. Clone this repository:
   ```bash
   git clone https://github.com/JanaGh7/Project-SHATO.git
   cd Project-SHATO
   ```

2. Start the service:
   ```bash
   docker compose up --build
   ```
   when you close it. run the following command before starting again
   ```bash
   docker compose down
   ```
   
now you have 2 ports open,
   - llm-server on port 8000
   - ollama2 on port 11434

4. Keep the existing terminal open and start a new one

5. Run the following command to test:
   ```bash
   curl -X POST "http://localhost:8000/process"
   -H "Content-Type: application/json"
   -d '{
     "input_text": "move to coordinates x=5, y=7"
   }
   ```
what you write in the parameter of "input_text" is what the user will say to the robot.
to test any other command just write here what you will say to the robot.
