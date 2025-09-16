1. docker build -t validator-service ./validator-service
2. docker run --rm -p 8000:8000 validator-service
3. open new terminal
4. curl -X POST http://localhost:8000/execute_command -H "Content-Type: application/json" -d "{\"command\":\"move_to\",\"command_params\":{\"x\":1.0,\"y\":2.0},\"verbal_response\":\"Moving to point\"}"