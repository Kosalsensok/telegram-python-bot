import base64
import hashlib
import hmac
import logging
import time
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
    amount: str = "1.00"
) -> Tuple[str, str, dict]:
    """
    Creates transaction ID, request timestamp, and parameters for ABA PayWay Checkout HTML form.
    """
    req_time = datetime.now().strftime("%Y%m%d%H%M%S")
    chat_str = str(chat_id)[-6:]
    time_str = str(int(time.time()))[-8:]
    tran_id = f"D{chat_str}{time_str}"  # Pure alphanumeric (A-Z, 0-9), max 15 chars (ABA PayWay strict rule)
    
    # Store pending transaction state
    pending_donations[tran_id] = {
        "chat_id": chat_id,
        "amount": amount,
        "time": req_time
    }

    clean_server_url = server_url.rstrip("/")
    success_url = f"{clean_server_url}/payment_success?tran_id={tran_id}"
    continue_success_url_b64 = base64.b64encode(success_url.encode('utf-8')).decode('utf-8')
    return_params_b64 = base64.b64encode(f"chat_id={chat_id}".encode('utf-8')).decode('utf-8')

    hash_val = generate_aba_hash(
        req_time=req_time,
        merchant_id=merchant_id,
        tran_id=tran_id,
        amount=amount,
        payment_option="abapay",
        continue_success_url=continue_success_url_b64,
        return_params=return_params_b64,
        public_key=public_key
    )

    form_data = {
        "req_time": req_time,
        "merchant_id": merchant_id,
        "tran_id": tran_id,
        "amount": amount,
        "payment_option": "abapay",
        "hash": hash_val,
        "continue_success_url": continue_success_url_b64,
        "return_params": return_params_b64,
        "payway_url": payway_url
    }

    return tran_id, req_time, form_data
