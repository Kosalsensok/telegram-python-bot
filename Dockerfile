# Production Dockerfile for Telegram AI Bot (Python 3.11 + Node.js 20)
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies, Node.js 20, Khmer Unicode, and Math Fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
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
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy package files and install Node dependencies
COPY package*.json ./
RUN npm ci --omit=dev || npm install

# Copy python requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files and build TypeScript assets
COPY . .
RUN npm run build

# Expose Web Server Ports
EXPOSE 8080 3000

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Start Bot 24/7 Engine
CMD ["python", "main.py"]
