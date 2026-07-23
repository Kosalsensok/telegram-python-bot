import os
# pyrefly: ignore [missing-import]
import aiosqlite
from config import DATABASE_PATH

def get_db_connection(db_path: str = DATABASE_PATH):
    """
    Creates and returns an async SQLite connection context manager.
    Ensures parent directories exist.
    """
    dir_name = os.path.dirname(db_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
        
    return aiosqlite.connect(db_path)
