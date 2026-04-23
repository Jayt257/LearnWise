# ── Backend Dockerfile ────────────────────────────────────────
# Python 3.10-slim base matching local dev environment.
# No credentials baked in — all secrets injected via Render env vars.
# ─────────────────────────────────────────────────────────────
FROM python:3.10-slim

WORKDIR /app

# System dependencies:
#   gcc + libpq-dev  → compile psycopg2
#   ffmpeg           → required by openai-whisper for audio decoding
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (separate layer for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/

# Copy curriculum data (baked in as base layer;
# on Render, mount a Persistent Disk at /app/data so admin changes survive restarts)
COPY data/ ./data/

# Render injects $PORT at runtime (defaults to 8000 locally)
ENV PORT=8000
EXPOSE 8000

# Start Uvicorn using the injected PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
