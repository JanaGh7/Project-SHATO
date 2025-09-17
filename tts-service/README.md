# For windows users:
Install Visual C++ Build Tools
Go to Microsoft C++ Build Tools
Download and run the installer.
Make sure to check “Desktop development with C++” and install all default options

#Install espeak-ng on Windows

Go to the espeak-ng GitHub releases page:https://github.com/espeak-ng/espeak-ng/releases
Download the latest Windows build:
Look for a file like -installer.msi if available.
If it’s an .msi, just install like normal software.
Add it to your PATH:
Press Win + R, type sysdm.cpl, and press Enter.
Go to Advanced → Environment Variables.

Under System variables, find Path, click Edit, then New, and paste the folder path where espeak-ng.exe lives (e.g., C:\espeak-ng\bin).
1. docker build -t tts-service ./tts-service
2. docker run --rm -p 8000:8000 tts-service
3. open new terminal
4. curl -X POST http://127.0.0.1:8000/tts -H "Content-Type: application/json" -d "{\"text\":\"Hello world\"}"
or run test.py