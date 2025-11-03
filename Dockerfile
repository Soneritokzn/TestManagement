# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (optional: for building wheels)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code
COPY . .

# Create required folders if they don't exist
RUN mkdir -p /app/instance /app/exports /app/uploads

EXPOSE 5000

# Use gunicorn in production
# App entrypoint is app:app (Flask app object)
CMD ["gunicorn", "-w", "3", "-k", "gthread", "--threads", "2", "--timeout", "60", "-b", "0.0.0.0:5000", "app:app"]

