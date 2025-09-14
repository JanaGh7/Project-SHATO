#!/bin/sh

# Start Ollama server in background
echo "Starting Ollama server..."
ollama serve &

# Wait for server to be ready
echo "Waiting for Ollama server to start..."
sleep 5

ollama pull phi3:mini

# Keep the container running
echo "Ollama is ready and serving models..."
wait