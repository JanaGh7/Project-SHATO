# Use an official Python image
FROM python:3.11-slim
# -------------------------
# Stage 1: Builder
# -------------------------
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Copy requirements (we'll create a requirements.txt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    libopenblas-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

# -------------------------
# Stage 2: Final
# -------------------------
FROM python:3.11-slim

WORKDIR /app

# Copy the rest of the app
# Copy only installed packages
COPY --from=builder /usr/local /usr/local
COPY . .

# Expose the FastAPI default port
EXPOSE 8000

# Run the FastAPI server using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]