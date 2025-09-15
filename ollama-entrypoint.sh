#!/bin/sh

# Start Ollama server in background
echo "Starting Ollama server..."
ollama serve &

# Wait for server to be ready
echo "Waiting for Ollama server to start..."
sleep 5

# Check if phi3:mini already exists
if ollama list | grep -q "phi3:mini"; then
    echo "Model phi3:mini already available, skipping pull."
else
    echo "Pulling phi3:mini model..."
    ollama pull phi3:mini
fi

# Keep the container running
echo "Ollama is ready and serving models..."
wait