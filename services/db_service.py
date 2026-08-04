import logging
import asyncio
import time
from typing import List, Dict, Any, Optional
import aiomysql
import pymysql
import warnings

# Suppress MySQL Warnings about existing databases/tables
warnings.filterwarnings('ignore', category=pymysql.Warning)

class DatabaseService:
    """
    Asynchronous MySQL Database Service for Telegram AI Bot.
    Handles user management, chat history persistence, and usage stats in 'smart_ai_assistant'.
    Includes graceful auto-fallback if database connection fails.
    """
    def __init__(self, host: str, port: int, user: str, password: str, database: str = "smart_ai_assistant"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.pool: Optional[aiomysql.Pool] = None
        self.is_connected: bool = False
        self.in_memory_users: set = set()
        self.in_memory_messages_count: int = 0
        self.in_memory_user_stats: Dict[int, Dict[str, int]] = {}
        self.user_modes: Dict[int, str] = {}
        self.user_languages: Dict[int, str] = {}
        self._cached_global_stats: Optional[Dict[str, Any]] = None
        self._cached_global_stats_time: float = 0


    async def init_db(self) -> bool:
        """
        Initializes MySQL database 'smart_ai_assistant' and creates required tables.
        """
        try:
            # 1. Connect without selecting database to ensure DB creation
            conn = await asyncio.wait_for(
                aiomysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    connect_timeout=3,
                    autocommit=True
                ),
                timeout=3.0
            )
            async with conn.cursor() as cur:
                await cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{self.database}` "
                    f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                )
            conn.close()

            # 2. Create connection pool to the database
            self.pool = await asyncio.wait_for(
                aiomysql.create_pool(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    db=self.database,
                    charset="utf8mb4",
                    autocommit=True,
                    maxsize=25,
                    minsize=2,
                    connect_timeout=5

                ),
                timeout=3.0
            )

            # 3. Create tables if they do not exist
            async with self.pool.acquire() as conn_db:
                async with conn_db.cursor() as cur:
                    # Users table
                    try:
                        await cur.execute("""
                            CREATE TABLE IF NOT EXISTS users (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                telegram_id BIGINT UNIQUE NOT NULL,
                                username VARCHAR(255) NULL,
                                first_name VARCHAR(255) NULL,
                                last_name VARCHAR(255) NULL,
                                language_code VARCHAR(50) DEFAULT 'en',
                                active_mode VARCHAR(50) DEFAULT 'general',
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                INDEX idx_telegram_id (telegram_id)
                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                        """)
                    except Exception as e_tbl:
                        logging.warning(f"Note creating users table: {e_tbl}")

                    # Ensure columns exist for pre-existing tables created with different ORM/schema
                    alter_queries = [
                        "ALTER TABLE users ADD COLUMN telegramId BIGINT UNIQUE NULL;",
                        "ALTER TABLE users ADD COLUMN telegram_id BIGINT UNIQUE NULL;",
                        "ALTER TABLE users ADD COLUMN username VARCHAR(255) NULL;",
                        "ALTER TABLE users ADD COLUMN firstName VARCHAR(255) NULL;",
                        "ALTER TABLE users ADD COLUMN first_name VARCHAR(255) NULL;",
                        "ALTER TABLE users ADD COLUMN lastName VARCHAR(255) NULL;",
                        "ALTER TABLE users ADD COLUMN last_name VARCHAR(255) NULL;",
                        "ALTER TABLE users ADD COLUMN language VARCHAR(50) DEFAULT 'km';",
                        "ALTER TABLE users ADD COLUMN language_code VARCHAR(50) DEFAULT 'km';",
                        "ALTER TABLE users ADD COLUMN selectedMode VARCHAR(50) DEFAULT 'standard';",
                        "ALTER TABLE users ADD COLUMN active_mode VARCHAR(50) DEFAULT 'general';",
                        "ALTER TABLE users ADD COLUMN totalRequests INT DEFAULT 0;",
                        "ALTER TABLE users ADD COLUMN createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
                        "ALTER TABLE users ADD COLUMN updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;",
                        "ALTER TABLE users ADD COLUMN lastActiveAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;",
                        "ALTER TABLE users ADD COLUMN last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;"
                    ]
                    for alter_sql in alter_queries:
                        try:
                            await cur.execute(alter_sql)
                        except Exception:
                            pass

                    # Sync columns between Prisma camelCase schema and Python snake_case schema
                    sync_queries = [
                        "UPDATE users SET telegram_id = telegramId WHERE (telegram_id IS NULL OR telegram_id = 0) AND telegramId IS NOT NULL AND telegramId != 0;",
                        "UPDATE users SET telegramId = telegram_id WHERE (telegramId IS NULL OR telegramId = 0) AND telegram_id IS NOT NULL AND telegram_id != 0;",
                        "UPDATE users SET first_name = firstName WHERE first_name IS NULL AND firstName IS NOT NULL;",
                        "UPDATE users SET firstName = first_name WHERE firstName IS NULL AND first_name IS NOT NULL;",
                        "UPDATE users SET last_name = lastName WHERE last_name IS NULL AND lastName IS NOT NULL;",
                        "UPDATE users SET lastName = last_name WHERE lastName IS NULL AND last_name IS NOT NULL;",
                        "UPDATE users SET language_code = language WHERE language_code IS NULL AND language IS NOT NULL;",
                        "UPDATE users SET language = language_code WHERE language IS NULL AND language_code IS NOT NULL;",
                        "UPDATE users SET active_mode = selectedMode WHERE active_mode IS NULL AND selectedMode IS NOT NULL;",
                        "UPDATE users SET selectedMode = active_mode WHERE selectedMode IS NULL AND active_mode IS NOT NULL;",
                        "UPDATE users SET updatedAt = NOW() WHERE updatedAt IS NULL OR updatedAt = '0000-00-00 00:00:00';",
                        "UPDATE users SET createdAt = NOW() WHERE createdAt IS NULL OR createdAt = '0000-00-00 00:00:00';"
                    ]
                    for sync_sql in sync_queries:
                        try:
                            await cur.execute(sync_sql)
                        except Exception:
                            pass

                    # Messages / Chat history table
                    try:
                        await cur.execute("""
                            CREATE TABLE IF NOT EXISTS messages (
                                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                                telegram_id BIGINT NOT NULL,
                                role ENUM('user', 'model') NOT NULL,
                                message_type ENUM('text', 'image') DEFAULT 'text',
                                content TEXT NOT NULL,
                                model_used VARCHAR(100) DEFAULT 'gemini-3.6-flash',
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                INDEX idx_user_msg (telegram_id, id)
                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                        """)
                    except Exception as e_msg:
                        logging.error(f"Error creating messages table in MySQL: {e_msg}")

            self.is_connected = True
            logging.info(f"✅ Successfully connected to MySQL database '{self.database}'. Tables verified.")
            return True

        except Exception as e:
            logging.warning(f"⚠️ MySQL Connection/Initialization failed: {e}. Falling back to in-memory mode.")
            self.is_connected = False
            return False

    async def ensure_connected(self) -> bool:
        """
        Ensures MySQL connection pool is active. Automatically reconnects if closed or dropped.
        """
        if self.is_connected and self.pool and not self.pool._closed:
            return True
        logging.info("DatabaseService: Connection pool dropped or closed. Attempting auto-reconnect...")
        return await self.init_db()

    async def save_or_update_user(
        self, 
        telegram_id: int, 
        username: Optional[str] = None, 
        first_name: Optional[str] = None, 
        last_name: Optional[str] = None, 
        language_code: str = "km"
    ) -> None:
        """
        Saves new user or updates existing user profile in MySQL and in-memory cache.
        Populates both Prisma (camelCase) and Python (snake_case) column schemas.
        """
        if not telegram_id or telegram_id == 0:
            return
        self.in_memory_users.add(telegram_id)

        if not self.is_connected or not self.pool:
            return

        try:
            sql = """
                INSERT INTO users (
                    telegramId, telegram_id, username, firstName, first_name, 
                    lastName, last_name, language, language_code, updatedAt, lastActiveAt, last_active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), NOW())
                ON DUPLICATE KEY UPDATE
                    telegramId = IF(telegramId IS NULL OR telegramId = 0, VALUES(telegramId), telegramId),
                    telegram_id = IF(telegram_id IS NULL OR telegram_id = 0, VALUES(telegram_id), telegram_id),
                    username = VALUES(username),
                    firstName = VALUES(firstName),
                    first_name = VALUES(first_name),
                    lastName = VALUES(lastName),
                    last_name = VALUES(last_name),
                    language = VALUES(language),
                    language_code = VALUES(language_code),
                    updatedAt = NOW(),
                    lastActiveAt = NOW(),
                    last_active = NOW();
            """
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, (
                        telegram_id, telegram_id,
                        username,
                        first_name, first_name,
                        last_name, last_name,
                        language_code, language_code
                    ))
        except Exception as e:
            try:
                sql_fb = """
                    INSERT INTO users (telegram_id, username, first_name, last_name, language_code)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        username = VALUES(username),
                        first_name = VALUES(first_name),
                        last_name = VALUES(last_name),
                        language_code = VALUES(language_code);
                """
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(sql_fb, (telegram_id, username, first_name, last_name, language_code))
            except Exception as e_fb:
                logging.error(f"Error updating user {telegram_id} in MySQL: {e_fb}")

    async def save_message(
        self, 
        telegram_id: int, 
        role: str, 
        content: str, 
        message_type: str = "text", 
        model_used: str = "gemini-3.6-flash"
    ) -> None:
        """
        Saves a chat message turn (user or model) to MySQL database and in-memory counter asynchronously without blocking.
        """
        self.in_memory_messages_count += 1
        if telegram_id:
            if telegram_id not in self.in_memory_user_stats:
                self.in_memory_user_stats[telegram_id] = {"total_messages": 0, "text_count": 0, "image_count": 0}
            if role == "user":
                self.in_memory_user_stats[telegram_id]["total_messages"] += 1
                if message_type == "image":
                    self.in_memory_user_stats[telegram_id]["image_count"] += 1
                else:
                    self.in_memory_user_stats[telegram_id]["text_count"] += 1

        if not self.is_connected or not self.pool:
            return

        async def _async_save():
            try:
                sql = """
                    INSERT INTO messages (telegram_id, role, message_type, content, model_used)
                    VALUES (%s, %s, %s, %s, %s);
                """
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(sql, (telegram_id, role, message_type, content, model_used))
            except Exception as e:
                logging.error(f"Error saving message for user {telegram_id} in MySQL: {e}")

        asyncio.create_task(_async_save())

    async def get_history(self, telegram_id: int, limit: int = 20) -> List[Dict[str, str]]:
        """
        Retrieves recent conversation history turns from MySQL database.
        """
        if not self.is_connected or not self.pool:
            return []

        try:
            sql = """
                SELECT role, content FROM (
                    SELECT role, content, id FROM messages 
                    WHERE telegram_id = %s OR telegram_id = %s
                    ORDER BY id DESC LIMIT %s
                ) sub ORDER BY id ASC;
            """
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, (telegram_id, telegram_id, limit))
                    rows = await cur.fetchall()
                    return [{"role": r[0], "content": r[1]} for r in rows]
        except Exception as e:
            logging.error(f"Error fetching history for user {telegram_id} from MySQL: {e}")
            return []

    async def clear_history(self, telegram_id: int) -> bool:
        """
        Clears conversation history messages for a user in MySQL database.
        """
        if not self.is_connected or not self.pool:
            return False

        try:
            sql = "DELETE FROM messages WHERE telegram_id = %s;"
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    affected = await cur.execute(sql, (telegram_id,))
                    return affected > 0
        except Exception as e:
            logging.error(f"Error clearing history for user {telegram_id} in MySQL: {e}")
            return False

    async def get_user_stats(self, telegram_id: int) -> Dict[str, Any]:
        """
        Retrieves user usage statistics from MySQL database or in-memory fallback.
        """
        in_mem_stat = self.in_memory_user_stats.get(telegram_id, {"total_messages": 0, "text_count": 0, "image_count": 0})
        if not self.is_connected or not self.pool:
            return in_mem_stat

        try:
            sql = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN message_type = 'text' THEN 1 ELSE 0 END) as text_msgs,
                    SUM(CASE WHEN message_type = 'image' THEN 1 ELSE 0 END) as image_msgs
                FROM messages WHERE telegram_id = %s AND role = 'user';
            """
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, (telegram_id,))
                    row = await cur.fetchone()
                    if row and row[0] is not None:
                        return {
                            "total_messages": max(row[0] or 0, in_mem_stat["total_messages"]),
                            "text_count": max(int(row[1] or 0), in_mem_stat["text_count"]),
                            "image_count": max(int(row[2] or 0), in_mem_stat["image_count"])
                        }
        except Exception as e:
            logging.error(f"Error fetching stats for user {telegram_id} from MySQL: {e}")
        return in_mem_stat

    async def get_global_stats(self) -> Dict[str, Any]:
        """
        Retrieves global system statistics dynamically from in-memory cache and MySQL.
        Guarantees that new users instantly update the active user count.
        """
        now = time.time()
        in_mem_users_cnt = len(self.in_memory_users)
        in_mem_msgs_cnt = self.in_memory_messages_count

        if not self._cached_global_stats:
            self._cached_global_stats = {
                "total_users": max(in_mem_users_cnt, 1),
                "total_messages": max(in_mem_msgs_cnt, 1)
            }
            self._cached_global_stats_time = now

        # Dynamically reflect in-memory changes instantly so new users are never missed
        self._cached_global_stats["total_users"] = max(self._cached_global_stats.get("total_users", 0), in_mem_users_cnt, 1)
        self._cached_global_stats["total_messages"] = max(self._cached_global_stats.get("total_messages", 0), in_mem_msgs_cnt, 1)

        if now - self._cached_global_stats_time >= 30:
            self._cached_global_stats_time = now
            if self.is_connected and self.pool:
                asyncio.create_task(self._refresh_global_stats_bg(in_mem_users_cnt, in_mem_msgs_cnt))

        return self._cached_global_stats


    async def _refresh_global_stats_bg(self, in_mem_users_cnt: int, in_mem_msgs_cnt: int):
        try:
            sql_users = "SELECT COUNT(*) FROM users;"
            sql_msgs = "SELECT COUNT(*) FROM messages;"
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql_users)
                    u_row = await cur.fetchone()
                    await cur.execute(sql_msgs)
                    m_row = await cur.fetchone()

                    db_users = u_row[0] if u_row else 0
                    db_msgs = m_row[0] if m_row else 0

                    self._cached_global_stats = {
                        "total_users": max(db_users, in_mem_users_cnt),
                        "total_messages": max(db_msgs, in_mem_msgs_cnt)
                    }
                    self._cached_global_stats_time = time.time()
        except Exception as e:
            logging.error(f"Error fetching global stats in background: {e}")

    async def close(self) -> None:
        """
        Closes MySQL database pool gracefully.
        """
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.is_connected = False
            logging.info("MySQL connection pool closed.")

    async def get_all_users(self) -> List[int]:
        """
        Retrieves all registered telegram_ids for admin broadcast.
        """
        if not self.is_connected or not self.pool:
            return []
            
        try:
            sql = "SELECT COALESCE(telegram_id, telegramId) FROM users WHERE COALESCE(telegram_id, telegramId) IS NOT NULL AND COALESCE(telegram_id, telegramId) != 0;"
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql)
                    rows = await cur.fetchall()
                    return [row[0] for row in rows]
        except Exception as e:
            logging.error(f"Error fetching all users from MySQL: {e}")
            return []

    async def get_recent_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves recent users for admin panel.
        """
        if not self.is_connected or not self.pool:
            return []
            
        try:
            sql = "SELECT COALESCE(telegram_id, telegramId), COALESCE(first_name, firstName), username, COALESCE(last_active, lastActiveAt) FROM users ORDER BY id DESC LIMIT %s;"
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, (limit,))
                    rows = await cur.fetchall()
                    return [
                        {
                            "telegram_id": row[0], 
                            "first_name": row[1], 
                            "username": row[2], 
                            "last_active": row[3]
                        } for row in rows
                    ]
        except Exception as e:
            logging.error(f"Error fetching recent users from MySQL: {e}")
            return []

    async def set_user_mode(self, telegram_id: int, mode: str) -> None:
        """
        Set active operating mode for a user in MySQL and in-memory cache asynchronously without blocking.
        """
        self.user_modes[telegram_id] = mode
        if not self.is_connected or not self.pool:
            return

        async def _async_update():
            try:
                sql = "UPDATE users SET active_mode = %s, selectedMode = %s WHERE telegram_id = %s OR telegramId = %s;"
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(sql, (mode, mode, telegram_id, telegram_id))
            except Exception as e:
                logging.error(f"Error updating active_mode for user {telegram_id} in MySQL: {e}")

        asyncio.create_task(_async_update())

    async def get_user_mode(self, telegram_id: int) -> str:
        """
        Retrieve active operating mode for a user from MySQL or in-memory cache.
        """
        if telegram_id in self.user_modes:
            return self.user_modes[telegram_id]

        if not self.is_connected or not self.pool:
            return "general"

        try:
            sql = "SELECT COALESCE(active_mode, selectedMode) FROM users WHERE telegram_id = %s OR telegramId = %s LIMIT 1;"
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, (telegram_id, telegram_id))
                    row = await cur.fetchone()
                    if row and row[0]:
                        self.user_modes[telegram_id] = row[0]
                        return row[0]
        except Exception as e:
            logging.error(f"Error fetching active_mode for user {telegram_id} from MySQL: {e}")

        return "general"

    async def set_user_language(self, telegram_id: int, lang: str) -> None:
        """
        Set active language for a user in MySQL and in-memory cache asynchronously without blocking.
        """
        self.user_languages[telegram_id] = lang
        if not self.is_connected or not self.pool:
            return

        async def _async_update():
            try:
                sql = "UPDATE users SET language_code = %s, language = %s WHERE telegram_id = %s OR telegramId = %s;"
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(sql, (lang, lang, telegram_id, telegram_id))
            except Exception as e:
                logging.error(f"Error updating language_code for user {telegram_id} in MySQL: {e}")

        asyncio.create_task(_async_update())

    async def get_user_language(self, telegram_id: int) -> str:
        """
        Retrieve active language for a user from MySQL or in-memory cache.
        """
        if telegram_id in self.user_languages:
            return self.user_languages[telegram_id]

        if not self.is_connected or not self.pool:
            return "km"

        try:
            sql = "SELECT COALESCE(language_code, language) FROM users WHERE telegram_id = %s OR telegramId = %s LIMIT 1;"
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, (telegram_id, telegram_id))
                    row = await cur.fetchone()
                    if row and row[0]:
                        self.user_languages[telegram_id] = row[0]
                        return row[0]
        except Exception as e:
            logging.error(f"Error fetching language_code for user {telegram_id} from MySQL: {e}")

        return "km"


