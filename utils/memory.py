import logging
from typing import Dict, List, Any, Optional
from services.db_service import DatabaseService

class ConversationMemory:
    """
    Hybrid Conversation Memory Store for Telegram AI Bot.
    Uses MySQL database ('smart_ai_assistant') for persistence with an in-memory cache fallback.
    """
    def __init__(self, max_history: int = 20, db_service: Optional[DatabaseService] = None):
        self.max_history = max_history
        self.db_service = db_service
        self._store: Dict[int, List[Dict[str, str]]] = {}

    async def add_user_message_async(self, user_id: int, content: str, message_type: str = "text") -> None:
        """
        Record a user message asynchronously in both MySQL and local in-memory cache.
        """
        # Save to local cache
        self.add_user_message(user_id, content)

        # Save to MySQL if database is connected
        if self.db_service and self.db_service.is_connected:
            await self.db_service.save_message(
                telegram_id=user_id,
                role="user",
                content=content,
                message_type=message_type
            )

    async def add_assistant_message_async(
        self, 
        user_id: int, 
        content: str, 
        message_type: str = "text", 
        model_used: str = "gemini-3.6-flash"
    ) -> None:
        """
        Record an assistant message asynchronously in both MySQL and local in-memory cache.
        """
        # Save to local cache
        self.add_assistant_message(user_id, content)

        # Save to MySQL if database is connected
        if self.db_service and self.db_service.is_connected:
            await self.db_service.save_message(
                telegram_id=user_id,
                role="model",
                content=content,
                message_type=message_type,
                model_used=model_used
            )

    async def get_history_async(self, user_id: int) -> List[Dict[str, str]]:
        """
        Retrieve recent conversation turns for user from MySQL DB (or fallback to local cache).
        """
        if self.db_service and self.db_service.is_connected:
            db_history = await self.db_service.get_history(user_id, limit=self.max_history)
            if db_history:
                # Sync local store cache
                self._store[user_id] = db_history
                return db_history

        return self.get_history(user_id)

    async def clear_history_async(self, user_id: int) -> bool:
        """
        Clears user history from both MySQL DB and in-memory cache.
        """
        cleared_cache = self.clear_history(user_id)
        cleared_db = False

        if self.db_service and self.db_service.is_connected:
            cleared_db = await self.db_service.clear_history(user_id)

        return cleared_cache or cleared_db

    # -------------------------------------------------------------
    # SYNCHRONOUS FALLBACK METHODS
    # -------------------------------------------------------------
    def add_user_message(self, user_id: int, content: str) -> None:
        if user_id not in self._store:
            self._store[user_id] = []
        self._store[user_id].append({"role": "user", "content": content})
        self._trim(user_id)

    def add_assistant_message(self, user_id: int, content: str) -> None:
        if user_id not in self._store:
            self._store[user_id] = []
        self._store[user_id].append({"role": "model", "content": content})
        self._trim(user_id)

    def get_history(self, user_id: int) -> List[Dict[str, str]]:
        return self._store.get(user_id, [])

    def clear_history(self, user_id: int) -> bool:
        if user_id in self._store:
            del self._store[user_id]
            logging.info(f"Cleared memory cache for user {user_id}")
            return True
        return False

    def _trim(self, user_id: int) -> None:
        if user_id in self._store and len(self._store[user_id]) > self.max_history:
            self._store[user_id] = self._store[user_id][-self.max_history:]
