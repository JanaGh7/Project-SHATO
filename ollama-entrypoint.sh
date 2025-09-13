#!/bin/sh

# Start Ollama server in background
echo "Starting Ollama server..."
ollama serve &

# Wait for server to be ready
echo "Waiting for Ollama server to start..."
sleep 5

# Check via API instead of filesystem
if curl -s http://localhost:11434/api/tags | grep -q '"name":"phi3:mini"'; then
    echo "phi3:mini model already exists."
else
    echo "Pulling phi3-mini model..."
    ollama pull phi3:mini
fi

# Keep the container running
echo "Ollama is ready and serving models..."
wait