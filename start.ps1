# Windows Powershell 24/7 Supervisor Script for Smart AI Assistant Telegram Bot

Write-Host "🚀 Starting Telegram AI Bot with 24/7 Auto-Restart..." -ForegroundColor Green

while ($true) {
    Write-Host "⚡ Launching main.py..." -ForegroundColor Cyan
    & .venv\Scripts\python.exe main.py
    Write-Host "⚠️ Process exited. Restarting in 3 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}
