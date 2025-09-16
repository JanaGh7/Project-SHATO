# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "robot_validator:app", "--host", "0.0.0.0", "--port", "8000"]
