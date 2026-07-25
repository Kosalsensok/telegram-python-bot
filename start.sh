#!/bin/bash
# High-Availability 24/7 Launcher Script for Smart AI Assistant Telegram Bot

echo "🚀 Starting Telegram AI Bot with 24/7 Auto-Restart..."

# Ensure virtualenv exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating python virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
fi

# Infinite loop supervisor for 24/7 continuous uptime
while true; do
    echo "⚡ Launching main.py..."
    .venv/bin/python main.py
    EXIT_CODE=$?
    echo "⚠️ Process exited with code $EXIT_CODE. Restarting in 3 seconds..."
    sleep 3
done
