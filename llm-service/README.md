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
   
5. docker build -t llm-service ./llm-service

6. docker run --rm -d \
  --name llm-service \
  -p 5002:8000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  llm-service

7. open a new tap

8. curl -X POST http://localhost:8000/generate_command \
     -H "Content-Type: application/json" \
     -d '{"input_text": "Move the robot to X=5 Y=10"}'
