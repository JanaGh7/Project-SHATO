# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app


# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy files
COPY . .

# Expose the port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "robot_validator:app", "--host", "0.0.0.0", "--port", "8000"]
