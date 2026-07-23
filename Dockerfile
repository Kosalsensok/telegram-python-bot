# Production Dockerfile for Telegram AI Bot (Python 3.11)
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies, Khmer Unicode, and Math Fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-noto-core \
    fonts-noto-extra \
    fonts-noto-ui-core \
    fonts-khmeros \
    fonts-lmodern \
    gcc \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY . .

# Expose Web Server Port (Health Check & Keep-Alive)
EXPOSE 8080

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Start Bot
CMD ["python", "main.py"]
