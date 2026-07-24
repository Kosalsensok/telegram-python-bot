import unittest
import asyncio
from services.image_gen_service import ImageGenService, parse_aspect_ratio

class TestImageGenService(unittest.TestCase):
    """
    Unit test suite for AI Image Generation service.
    """

    def test_parse_aspect_ratio(self):
        ratio_key, w, h, clean = parse_aspect_ratio("16:9 a cool logo")
        self.assertEqual(ratio_key, "16:9")
        self.assertEqual(w, 1280)
        self.assertEqual(h, 720)
        self.assertEqual(clean, "a cool logo")

    def test_image_generation_fallback(self):
        async def run_test():
            service = ImageGenService()
            img_bytes, prompt, seed, cache_id = await service.generate_image("logo e lms cool", width=512, height=512)
            self.assertIsNotNone(img_bytes)
            self.assertGreater(len(img_bytes), 3000)
            self.assertTrue(cache_id.startswith("img_"))

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
