import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from keyboards.inline import (
    get_welcome_inline_keyboard,
    get_donation_amount_keyboard,
    get_donation_qr_keyboard
)
from services.aba_payway import (
    request_aba_payway_purchase,
    create_donation_checkout_params,
    check_aba_payment_status,
    pending_donations
)

class TestDonationFlow(unittest.TestCase):

    def test_welcome_keyboard_donate_button(self):
        """Verify main welcome keyboard contains generic Donate button callback."""
        kb = get_welcome_inline_keyboard(lang="km")
        button_labels = [btn.text for row in kb.inline_keyboard for btn in row]
        button_callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row if btn.callback_data]
        
        self.assertTrue(any("បរិច្ចាគ" in label for label in button_labels))
        self.assertIn("cb_donate", button_callbacks)

    def test_donation_amount_keyboard_structure(self):
        """Verify donation amount selection keyboard contains presets and custom option."""
        kb = get_donation_amount_keyboard(lang="km")
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row if btn.callback_data]

        self.assertIn("donate_amt_2000", callbacks)
        self.assertIn("donate_amt_4000", callbacks)
        self.assertIn("donate_amt_20000", callbacks)
        self.assertIn("donate_amt_40000", callbacks)
        self.assertIn("donate_custom", callbacks)
        self.assertIn("cb_back_main", callbacks)

    def test_donation_qr_keyboard_structure(self):
        """Verify KHQR payment keyboard contains app deeplink and web checkout URLs."""
        open_app_url = "https://example.com/open_abapay?tran_id=D123456"
        checkout_url = "https://example.com/donate_checkout?tran_id=D123456"
        kb = get_donation_qr_keyboard(open_app_url=open_app_url, checkout_url=checkout_url, lang="km")

        urls = [btn.url for row in kb.inline_keyboard for btn in row if btn.url]
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row if btn.callback_data]

        self.assertIn(open_app_url, urls)
        self.assertIn(checkout_url, urls)
        self.assertIn("cb_donate", callbacks)
        self.assertIn("cb_back_main", callbacks)

    def test_aba_payway_checkout_params_dynamic_amount(self):
        """Verify ABA PayWay transaction creation records custom dynamic amounts."""
        chat_id = 999888
        amount = "5000"
        tran_id, req_time, form_data = create_donation_checkout_params(
            chat_id=chat_id,
            merchant_id="test_merchant",
            public_key="test_key",
            payway_url="https://checkout.sandbox.payway.com.kh/api/payment-gateway/v1/payments/purchase",
            server_url="https://test.server.com",
            amount=amount,
            first_name="TestUser"
        )

        self.assertIn(tran_id, pending_donations)
        self.assertEqual(pending_donations[tran_id]["amount"], "5000")
        self.assertEqual(form_data["amount"], "5000")
        self.assertEqual(form_data["merchant_id"], "test_merchant")

    def test_custom_amount_validation_logic(self):
        """Test regex cleaning and threshold validation for user custom amount input."""
        import re

        def validate_amount_input(raw_text: str):
            clean_num = re.sub(r'[^\d]', '', raw_text)
            if not clean_num or not clean_num.isdigit() or int(clean_num) < 1000:
                return None
            return clean_num

        self.assertEqual(validate_amount_input("5000"), "5000")
        self.assertEqual(validate_amount_input("10,000 ៛"), "10000")
        self.assertEqual(validate_amount_input("500 ៛"), None)
        self.assertEqual(validate_amount_input("invalid text"), None)

    def test_async_aba_payway_purchase(self):
        """Test async purchase request mock execution with custom amount."""
        async def run_test():
            with patch("aiohttp.ClientSession.post") as mock_post:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = {
                    "qrImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                    "abapay_deeplink": "abapay://qr?string=test",
                    "qrString": "000201010212..."
                }
                mock_post.return_value.__aenter__.return_value = mock_response

                res = await request_aba_payway_purchase(
                    chat_id=123456,
                    merchant_id="test_m",
                    public_key="test_k",
                    payway_url="https://checkout.sandbox.payway.com.kh/api/payment-gateway/v1/payments/purchase",
                    server_url="https://test.com",
                    amount="15000"
                )

                self.assertTrue(res["success"])
                self.assertEqual(res["amount"], "15000")
                self.assertTrue(res["qr_image"].startswith("data:image/png;base64"))

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
