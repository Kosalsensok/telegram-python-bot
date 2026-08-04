import unittest
import asyncio
import time
from typing import List
from unittest.mock import AsyncMock, MagicMock
from services.gemini_service import GeminiService
from services.db_service import DatabaseService
from utils.memory import ConversationMemory
from utils.user_throttling import UserThrottlingMiddleware
from aiogram.types import Message, User, Chat, CallbackQuery


class TestMultiUserConcurrency(unittest.IsolatedAsyncioTestCase):
    """
    Automated test suite simulating 50+ concurrent users sending simultaneous requests
    to ensure 100% smooth execution, non-blocking asynchronous operation, zero unhandled errors,
    and accurate rate limiting under heavy load.
    """

    async def test_50_concurrent_gemini_requests(self):
        """Simulate 50 concurrent users calling GeminiService simultaneously."""
        gemini = GeminiService(api_key="mock_key", primary_model="gemini-flash-lite-latest", max_concurrency=15)
        # Mock synchronous internal API call to return instant mock response
        gemini._sync_generate_content = MagicMock(return_value="សួស្តី! ខ្ញុំជា AI Assistant ឆ្លើយតបយ៉ាងរហ័ស។")

        start_time = time.time()
        tasks = []
        user_count = 50
        for i in range(user_count):
            user_id = 1000 + i
            tasks.append(gemini.generate_text_chat(
                user_prompt=f"សួរដំណឹង User {user_id}",
                history=[],
                mode="general"
            ))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time

        # Verify 100% success rate (no exceptions thrown)
        exceptions = [r for r in results if isinstance(r, Exception)]
        self.assertEqual(len(exceptions), 0, f"Exceptions occurred during concurrent Gemini calls: {exceptions}")
        self.assertEqual(len(results), user_count)
        for r in results:
            self.assertIn("សួស្តី!", r)

        print(f"\n✅ 50 Concurrent Gemini API calls completed in {elapsed:.3f} seconds ({user_count / elapsed:.1f} req/sec).")

    async def test_concurrent_user_tracking_and_memory(self):
        """Simulate 50 distinct users recording conversation history concurrently."""
        db_service = DatabaseService(host="127.0.0.1", port=3306, user="test", password="test")
        memory = ConversationMemory(max_history=10, db_service=db_service)

        tasks = []
        user_count = 50
        for i in range(user_count):
            user_id = 2000 + i
            tasks.append(memory.add_user_message_async(user_id, f"Hello from user {user_id}"))
            tasks.append(memory.add_assistant_message_async(user_id, f"Response to user {user_id}"))

        await asyncio.gather(*tasks)

        # Check each user memory cache has exactly 2 messages
        for i in range(user_count):
            user_id = 2000 + i
            history = memory.get_history(user_id)
            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]["content"], f"Hello from user {user_id}")
            self.assertEqual(history[1]["content"], f"Response to user {user_id}")

        print(f"✅ Concurrent memory tracking for {user_count} users verified successfully.")

    async def test_user_throttling_middleware(self):
        """Verify throttling middleware permits normal requests and throttles rapid spam."""
        middleware = UserThrottlingMiddleware(time_window=1.0, max_requests=2)
        mock_handler = AsyncMock(return_value="OK")

        def make_message(user_id: int):
            msg = MagicMock(spec=Message)
            msg.from_user = User(id=user_id, is_bot=False, first_name="Tester")
            msg.answer = AsyncMock()
            return msg

        user_a = 5001
        msg1 = make_message(user_a)
        msg2 = make_message(user_a)
        msg3 = make_message(user_a)

        # First 2 rapid calls allowed
        res1 = await middleware(mock_handler, msg1, {})
        res2 = await middleware(mock_handler, msg2, {})
        # 3rd rapid call throttled
        res3 = await middleware(mock_handler, msg3, {})

        self.assertEqual(res1, "OK")
        self.assertEqual(res2, "OK")
        self.assertIsNone(res3)
        msg3.answer.assert_called_once()  # Warning message sent to throttled user

        print("✅ UserThrottlingMiddleware rate limiting and spam protection verified.")


if __name__ == "__main__":
    unittest.main()
