# -------------------------
# Stage 1: Builder
# -------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# System dependencies needed for pip packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

# -------------------------
# Stage 2: Final
# -------------------------
FROM python:3.11-slim

WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    espeak-ng \
    libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /usr/local /usr/local
# Copy your service code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "tts:app", "--host", "0.0.0.0", "--port", "8000"]
