import base64
import hashlib
import hmac
import logging
import time
import aiohttp
from datetime import datetime
from typing import Dict, Optional, Tuple

logger = logging.getLogger("ABAPaywayService")

# Storage in-memory for pending donations & completed transactions
pending_donations: Dict[str, dict] = {}
completed_donations: set = set()

def generate_aba_hash(
    req_time: str,
    merchant_id: str,
    tran_id: str,
    amount: str,
    items: str = "",
    shipping: str = "",
    firstname: str = "",
    lastname: str = "",
    email: str = "",
    phone: str = "",
    type_val: str = "",
    payment_option: str = "",
    continue_success_url: str = "",
    return_params: str = "",
    public_key: str = ""
) -> str:
    """
    Generates HMAC-SHA512 Signature Hash for ABA PayWay v1/v2 Payment Gateway.
    Concatenates string fields in exact sequence required by ABA PayWay specification.
    """
    str_to_hash = (
        str(req_time) + str(merchant_id) + str(tran_id) + str(amount) +
        str(items) + str(shipping) + str(firstname) + str(lastname) +
        str(email) + str(phone) + str(type_val) + str(payment_option) +
        str(continue_success_url) + str(return_params)
    )
    hashed = hmac.new(public_key.encode('utf-8'), str_to_hash.encode('utf-8'), hashlib.sha512).digest()
    return base64.b64encode(hashed).decode('utf-8')


def create_donation_checkout_params(
    chat_id: int,
    merchant_id: str,
    public_key: str,
    payway_url: str,
    server_url: str,
    amount: str = "2000",
    payment_option: str = ""
) -> Tuple[str, str, dict]:
    """
    Creates transaction ID, request timestamp, and parameters for ABA PayWay Checkout HTML form.
    """
    req_time = datetime.now().strftime("%Y%m%d%H%M%S")
    chat_str = str(chat_id)[-6:] if chat_id else "100000"
    time_str = str(int(time.time()))[-8:]
    tran_id = f"D{chat_str}{time_str}"  # Pure alphanumeric (A-Z, 0-9), max 15 chars (ABA PayWay strict rule)
    
    # Store pending transaction state
    pending_donations[tran_id] = {
        "chat_id": chat_id,
        "amount": amount,
        "time": req_time,
        "status": "pending",
        "created_at": time.time()
    }

    clean_server_url = server_url.rstrip("/")
    success_url = f"{clean_server_url}/payment_success?tran_id={tran_id}&chat_id={chat_id}"
    continue_success_url_b64 = base64.b64encode(success_url.encode('utf-8')).decode('utf-8')
    return_params_b64 = base64.b64encode(f"chat_id={chat_id}".encode('utf-8')).decode('utf-8')

    hash_val = generate_aba_hash(
        req_time=req_time,
        merchant_id=merchant_id,
        tran_id=tran_id,
        amount=amount,
        payment_option=payment_option,
        continue_success_url=continue_success_url_b64,
        return_params=return_params_b64,
        public_key=public_key
    )

    form_data = {
        "req_time": req_time,
        "merchant_id": merchant_id,
        "tran_id": tran_id,
        "amount": amount,
        "payment_option": payment_option,
        "hash": hash_val,
        "continue_success_url": continue_success_url_b64,
        "return_params": return_params_b64,
        "payway_url": payway_url
    }

    return tran_id, req_time, form_data


async def request_aba_payway_purchase(
    chat_id: int,
    merchant_id: str,
    public_key: str,
    payway_url: str,
    server_url: str,
    amount: str = "2000"
) -> dict:
    """
    Executes a direct server-side async HTTP POST to ABA PayWay purchase API endpoint.
    Retrieves and parses qrString, qrImage, and abapay_deeplink.
    """
    tran_id, req_time, form_data = create_donation_checkout_params(
        chat_id=chat_id,
        merchant_id=merchant_id,
        public_key=public_key,
        payway_url=payway_url,
        server_url=server_url,
        amount=amount
    )

    # Post data to ABA API
    post_payload = {
        "req_time": form_data["req_time"],
        "merchant_id": form_data["merchant_id"],
        "tran_id": form_data["tran_id"],
        "amount": form_data["amount"],
        "payment_option": form_data["payment_option"],
        "hash": form_data["hash"],
        "continue_success_url": form_data["continue_success_url"],
        "return_params": form_data["return_params"]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(payway_url, data=post_payload, timeout=15) as resp:
                status_code = resp.status
                if status_code == 200:
                    data = await resp.json()
                    qr_image = data.get("qrImage", "")
                    deeplink = data.get("abapay_deeplink", "")
                    qr_string = data.get("qrString", "")
                    status_info = data.get("status", {})

                    if tran_id in pending_donations:
                        pending_donations[tran_id].update({
                            "qr_image": qr_image,
                            "abapay_deeplink": deeplink,
                            "qr_string": qr_string,
                            "status": "active"
                        })

                    return {
                        "success": True,
                        "tran_id": tran_id,
                        "amount": amount,
                        "req_time": req_time,
                        "qr_image": qr_image,
                        "abapay_deeplink": deeplink,
                        "qr_string": qr_string,
                        "status_info": status_info,
                        "raw": data
                    }
                else:
                    text = await resp.text()
                    logger.error(f"ABA PayWay purchase request failed with HTTP {status_code}: {text}")
                    return {
                        "success": False,
                        "tran_id": tran_id,
                        "amount": amount,
                        "error": f"HTTP {status_code}"
                    }
    except Exception as e:
        logger.error(f"Exception during ABA PayWay purchase request: {e}")
        return {
            "success": False,
            "tran_id": tran_id,
            "amount": amount,
            "error": str(e)
        }

