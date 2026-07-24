import asyncio
import logging
from typing import List, Optional
from aiogram import types


TEXT_THINKING_STEPS = [
    "🧠 <b>SMART AI ASSISTANT</b>\n━━━━━━━━━━━━━━━━━━━\n<i>⚡ AI កំពុងវិភាគ និងយល់ពីសំណួររបស់អ្នក... (1/3)</i>",
    "🧠 <b>SMART AI ASSISTANT</b>\n━━━━━━━━━━━━━━━━━━━\n<i>✨ AI កំពុងស្វែងរកទិន្នន័យ & រៀបចំចម្លើយ... (2/3)</i>",
    "🧠 <b>SMART AI ASSISTANT</b>\n━━━━━━━━━━━━━━━━━━━\n<i>💎 AI កំពុងផ្ទៀងផ្ទាត់ & រៀបចំអត្ថបទចម្លើយ... (3/3)</i>"
]

IMAGE_GEN_STEPS = [
    "🎨 <b>AI IMAGE GENERATOR</b>\n━━━━━━━━━━━━━━━━━━━\n<i>✨ AI កំពុងវិភាគ និងបង្កើន Prompt (1/3)...</i>",
    "🎨 <b>AI IMAGE GENERATOR</b>\n━━━━━━━━━━━━━━━━━━━\n<i>🌌 AI កំពុង Render Ultra HD Canvas (2/3)...</i>",
    "🎨 <b>AI IMAGE GENERATOR</b>\n━━━━━━━━━━━━━━━━━━━\n<i>💎 AI កំពុងរៀបចំ Color, Lighting & Resolution (3/3)...</i>"
]

VISION_THINKING_STEPS = [
    "🖼 <b>IMAGE ANALYSIS</b>\n━━━━━━━━━━━━━━━━━━━\n<i>👁 AI កំពុងស្កែន និងវិភាគរូបភាព (1/2)...</i>",
    "🖼 <b>IMAGE ANALYSIS</b>\n━━━━━━━━━━━━━━━━━━━\n<i>💡 AI កំពុងអានអត្ថបទ និងរៀបចំការពិពណ៌នា (2/2)...</i>"
]

VOICE_THINKING_STEPS = [
    "🎙️ <b>VOICE NOTE ANALYSIS</b>\n━━━━━━━━━━━━━━━━━━━\n<i>🎧 កំពុងបំផ្លាស់ប្តូរ Voice Frequency (1/2)...</i>",
    "🎙️ <b>VOICE NOTE ANALYSIS</b>\n━━━━━━━━━━━━━━━━━━━\n<i>✨ AI កំពុងបកប្រែ និងវិភាគខ្លឹមសារ (2/2)...</i>"
]

ENHANCE_THINKING_STEPS = [
    "✨ <b>ENHANCING HD QUALITY</b>\n━━━━━━━━━━━━━━━━━━━\n<i>🔍 កំពុងស្កែន និងស្វែងរកចំណុចស្រពិចស្រពិល (1/3)...</i>",
    "✨ <b>ENHANCING HD QUALITY</b>\n━━━━━━━━━━━━━━━━━━━\n<i>⚡ កំពុងទាញយក Super-Resolution Lanczos Filter (2/3)...</i>",
    "✨ <b>ENHANCING HD QUALITY</b>\n━━━━━━━━━━━━━━━━━━━\n<i>💎 កំណត់ Detail, Contrast & Ultra Sharpness (3/3)...</i>"
]


def get_doc_thinking_steps(filename: str) -> List[str]:
    return [
        f"📄 <b>DOCUMENT ANALYSIS</b>\n━━━━━━━━━━━━━━━━━━━\n<i>🔍 កំពុងស្កែនខ្លឹមសារ និង Code នៃ {filename} (1/2)...</i>",
        f"📄 <b>DOCUMENT ANALYSIS</b>\n━━━━━━━━━━━━━━━━━━━\n<i>🧠 AI កំពុងវិភាគ និងរៀបចំការសង្ខេប (2/2)...</i>"
    ]


def get_code_thinking_steps(language: str) -> List[str]:
    return [
        f"⚡ <b>CODE RUNNER ({language.upper()})</b>\n━━━━━━━━━━━━━━━━━━━\n<i>⚙️ កំពុងរៀបចំ Sandbox Environment (1/2)...</i>",
        f"⚡ <b>CODE RUNNER ({language.upper()})</b>\n━━━━━━━━━━━━━━━━━━━\n<i>🚀 កំពុង Execute Code (2/2)...</i>"
    ]


class DynamicThinkingAnimation:
    """
    Context manager / async task that smoothly animates loading & thinking messages in-place
    in Telegram with animated steps and icons.
    """
    def __init__(self, message: types.Message, steps: List[str], interval: float = 1.0):
        self.message = message
        self.steps = steps
        self.interval = interval
        self.loading_msg: Optional[types.Message] = None
        self._task: Optional[asyncio.Task] = None
        self._stopped = False

    async def start() -> types.Message:
        """Starts animation task and returns sent loading message."""
        initial_text = self.steps[0] if self.steps else "🧠 <b>SMART AI ASSISTANT</b>\n━━━━━━━━━━━━━━━━━━━\n<i>✨ AI កំពុងរៀបចំចម្លើយ...</i>"
        try:
            self.loading_msg = await self.message.reply(initial_text, parse_mode="HTML")
        except Exception:
            self.loading_msg = await self.message.answer(initial_text, parse_mode="HTML")
            
        if len(self.steps) > 1:
            self._task = asyncio.create_task(self._animate())
        return self.loading_msg

    async def _animate(self):
        step_idx = 0
        total_steps = len(self.steps)
        try:
            while not self._stopped:
                await asyncio.sleep(self.interval)
                if self._stopped or not self.loading_msg:
                    break
                step_idx = (step_idx + 1) % total_steps
                try:
                    await self.loading_msg.edit_text(self.steps[step_idx], parse_mode="HTML")
                except Exception:
                    pass
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.debug(f"Animation loop end: {e}")

    async def stop(self):
        """Stops the animation loop cleanly without deleting loading message."""
        self._stopped = True
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def stop_and_delete(self):
        """Stops animation loop and deletes loading message."""
        await self.stop()
        if self.loading_msg:
            try:
                await self.loading_msg.delete()
            except Exception:
                pass

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop_and_delete()

