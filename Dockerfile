# 1. Use an official lightweight Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy requirements.txt first (so Docker can cache installs)
COPY requirements.txt .

# 4. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application code
COPY . .

# 6. Expose port 8000 (FastAPI default)
EXPOSE 8000

# 7. Run the FastAPI server with Uvicorn
CMD ["echo", "Specify a command with docker-compose override"]


# docker build -t llm-service .
# docker run -it -v $(pwd):/app -p 8000:8000 llm-service
