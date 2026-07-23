import asyncio
import logging
from typing import List, Optional
from aiogram import types


TEXT_THINKING_STEPS = [
    "🤖 <b>AI កំពុងគិត...</b>\n<i>🧠 1/3 វិភាគសំណួររបស់អ្នក...</i>",
    "🤖 <b>AI កំពុងគិត...</b>\n<i>⚡ 2/3 ស្វែងរកទិន្នន័យ និងរៀបចំចម្លើយ...</i>",
    "🤖 <b>AI កំពុងគិត...</b>\n<i>✨ 3/3 ផ្ទៀងផ្ទាត់ និងសរសេរអត្ថបទចម្លើយ...</i>"
]

IMAGE_GEN_STEPS = [
    "🎨 <b>កំពុងបង្កើតរូបភាព AI កម្រិត Ultra HD...</b>\n<i>✨ 1/3 AI កំពុងវិភាគ និងបង្កើន Prompt...</i>",
    "🎨 <b>កំពុងបង្កើតរូបភាព AI កម្រិត Ultra HD...</b>\n<i>🌌 2/3 AI កំពុង Render 8K Canvas...</i>",
    "🎨 <b>កំពុងបង្កើតរូបភាព AI កម្រិត Ultra HD...</b>\n<i>💎 3/3 AI កំពុងរៀបចំ Color, Lighting & HD Resolution...</i>"
]

VISION_THINKING_STEPS = [
    "🔍 <b>កំពុងវិភាគរូបភាព...</b>\n<i>👁 1/2 AI កំពុងមើល និងស្កែនរូបភាព...</i>",
    "🔍 <b>កំពុងវិភាគរូបភាព...</b>\n<i>💡 2/2 AI កំពុងអានអត្ថបទ និងរៀបចំការពិពណ៌នា...</i>"
]

VOICE_THINKING_STEPS = [
    "🎙️ <b>កំពុងស្តាប់សារសំឡេង...</b>\n<i>🎧 1/2 កំពុងបំផ្លាស់ប្តូរ Voice Frequency...</i>",
    "🎙️ <b>កំពុងស្តាប់សារសំឡេង...</b>\n<i>✨ 2/2 AI កំពុងបកប្រែ និងវិភាគខ្លឹមសារ...</i>"
]

ENHANCE_THINKING_STEPS = [
    "✨ <b>កំពុងធ្វើឲ្យរូបភាពច្បាស់ (Enhancing HD Quality)...</b>\n<i>🔍 1/3 កំពុងស្កែន និងស្វែងរកចំណុចស្រពិចស្រពិល...</i>",
    "✨ <b>កំពុងធ្វើឲ្យរូបភាពច្បាស់ (Enhancing HD Quality)...</b>\n<i>⚡ 2/3 កំពុងទាញយក Super-Resolution Lanczos & Unsharp Mask...</i>",
    "✨ <b>កំពុងធ្វើឲ្យរូបភាពច្បាស់ (Enhancing HD Quality)...</b>\n<i>💎 3/3 កំពុងកំណត់ Detail, Contrast & Ultra Sharpness...</i>"
]


def get_doc_thinking_steps(filename: str) -> List[str]:
    return [
        f"📄 <b>កំពុងអាន {filename}...</b>\n<i>🔍 1/2 កំពុងស្កែនខ្លឹមសារ និង Code...</i>",
        f"📄 <b>កំពុងអាន {filename}...</b>\n<i>🧠 2/2 AI កំពុងវិភាគ និងរៀបចំការសង្ខេប...</i>"
    ]


def get_code_thinking_steps(language: str) -> List[str]:
    return [
        f"⚡ <b>កំពុងដំណើរការកូដ {language}...</b>\n<i>⚙️ 1/2 កំពុងរៀបចំ Sandbox Environment...</i>",
        f"⚡ <b>កំពុងដំណើរការកូដ {language}...</b>\n<i>🚀 2/2 កំពុង Execute Code...</i>"
    ]


class DynamicThinkingAnimation:
    """
    Context manager / async task that smoothly animates loading & thinking messages in-place
    in Telegram with animated steps and icons.
    """
    def __init__(self, message: types.Message, steps: List[str], interval: float = 1.3):
        self.message = message
        self.steps = steps
        self.interval = interval
        self.loading_msg: Optional[types.Message] = None
        self._task: Optional[asyncio.Task] = None
        self._stopped = False

    async def __aenter__(self):
        try:
            initial_text = self.steps[0] if self.steps else "🤖 <b>AI កំពុងគិត...</b>"
            self.loading_msg = await self.message.reply(initial_text, parse_mode="HTML")
            
            if len(self.steps) > 1:
                self._task = asyncio.create_task(self._animate())
        except Exception as e:
            logging.warning(f"Could not initialize dynamic loading animation: {e}")
        return self

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

    async def stop_and_delete(self):
        self._stopped = True
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self.loading_msg:
            try:
                await self.loading_msg.delete()
            except Exception:
                pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop_and_delete()
