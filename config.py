import os
import sys
from dotenv import load_dotenv

if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper().strip()
BOT_DISPLAY_NAME: str = os.getenv("BOT_DISPLAY_NAME", "Smart AI Assistant").strip()
RENDER_EXTERNAL_URL: str = os.getenv("RENDER_EXTERNAL_URL", "https://telegram-python-bot-yt64.onrender.com").strip()

SHOW_USER_COUNT_IN_BOT_NAME: bool = os.getenv("SHOW_USER_COUNT_IN_BOT_NAME", "true").lower() in ("true", "1", "t", "yes")

try:
    PROFILE_UPDATE_INTERVAL_MINUTES: int = int(os.getenv("PROFILE_UPDATE_INTERVAL_MINUTES", "5"))
except ValueError:
    PROFILE_UPDATE_INTERVAL_MINUTES = 5

try:
    MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
except ValueError:
    MAX_HISTORY_MESSAGES = 20

try:
    MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
except ValueError:
    MAX_IMAGE_SIZE_MB = 10

# MySQL Connection Configurations
MYSQL_HOST: str = os.getenv("MYSQL_HOST", "127.0.0.1").strip()
try:
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
except ValueError:
    MYSQL_PORT = 3306
MYSQL_USER: str = os.getenv("MYSQL_USER", "root").strip()
MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "").strip()
MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "smart_ai_assistant").strip()
USE_DATABASE: bool = os.getenv("USE_DATABASE", "true").lower() in ("true", "1", "t", "yes")
DATABASE_PATH: str = os.getenv("DATABASE_PATH", "./data/database.sqlite")

# Parse admin user IDs
admin_ids_raw = os.getenv("ADMIN_USER_IDS", "").strip()
ADMIN_USER_IDS = []
if admin_ids_raw:
    for uid in admin_ids_raw.split(","):
        uid_clean = uid.strip()
        if uid_clean.isdigit():
            ADMIN_USER_IDS.append(int(uid_clean))

STATS_PUBLIC: bool = os.getenv("STATS_PUBLIC", "true").lower() in ("true", "1", "t", "yes")

# Validate required variables
if not BOT_TOKEN or "YourTelegramBotToken" in BOT_TOKEN or "your_telegram_bot_token" in BOT_TOKEN:
    print("❌ Error: BOT_TOKEN is not properly set in .env file.")
    sys.exit(1)

if not GEMINI_API_KEY or "YourGeminiApiKey" in GEMINI_API_KEY or "your_gemini_api_key" in GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY is not properly set in .env file.")
    sys.exit(1)
