# Project-SHATO
MIA AI Training'26 Final Project: This project aims to transform SHATO, an autonomous robot, into an intelligent,  voice-controlled assistant.

## Project Folders and Their Roles

- **orchestrator-service**: Main FastAPI application that handles `/process` POST requests and `/health` checks. Connects the LLM output with the robot validator.  
- **validation-service**: Validates commands against a strict schema, logs successes and errors, and ensures only correct parameters are accepted.  
- **llm-service**: Interfaces with the language model (Ollama), parses natural language input into structured JSON commands.  
  - **schema.py**: Defines Pydantic models for command validation and response structure, ensuring type safety and strict parameter checks.
- **stt-service**: Speech to text model mapping user audio to written commands
- **tts-service**: Text to speech model mapping validation output to audio 
- **ui-service**: User interface for interaction
- Each of the services has its own:
  - *Dockerfile*: Builds the container with Python environment and dependencies.
  - *Requirements.txt*: Lists Python dependencies for the service.  
  - *README.md*: further explaining each service and how to install it independently
- **docker-compose.yml**: Orchestrates the multi-container setup including `ollama` and `llm-service`, exposing necessary ports and handling dependencies.  
- **ollama-entrypoint.sh**: Custom entrypoint script for the Ollama container that starts the server and pulls required models if missing.  

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
3. go to `localhost:7860` to open the UI where you can give voice or written commands and receive feedback
