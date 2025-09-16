1. docker build -t tts-service ./tts-service
2. docker run --rm -p 8000:8000 tts-service
3. open new terminal
4. curl -X POST http://127.0.0.1:8000/tts -H "Content-Type: application/json" -d "{\"text\":\"Hello world\"}"