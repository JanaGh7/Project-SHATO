how to run?

1. if it's the first time, run : docker volume create ollama
2. docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama

3. if the output was you have a container with that name alreay,
    run docker ps. if you see the container active then it's okay, 
    if not then run docker start ollama.

3. docker run -d \
  --name llm-service \
  -p 5002:8000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  llm-service

5. open a new tap

6. curl -X POST http://localhost:8000/generate_command \
     -H "Content-Type: application/json" \
     -d '{"input_text": "Move the robot to X=5 Y=10"}'