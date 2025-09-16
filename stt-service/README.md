steps to run independently

1. run : docker build -t stt-service ./stt-service
2. run : docker run --rm -p 5001:8000 stt-service
3. open new terminal
4. run : python3 stt-service/sendRecord.py
5. wait 5 seconds and see the result