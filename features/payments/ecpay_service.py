import os
import hashlib
import urllib.parse
from datetime import datetime, timedelta, timezone

def generate_check_mac_value(params: dict) -> str:
    sorted_params = sorted(params.items())
    hash_key = os.getenv("ECPAY_HASH_KEY")
    hash_iv = os.getenv("ECPAY_HASH_IV")
    raw_string = "&".join([f"{k}={v}" for k, v in sorted_params])

    full_string = f"HashKey={hash_key}&{raw_string}&HashIV={hash_iv}"
    encoded_string = urllib.parse.quote_plus(full_string).lower()
    
    fixed_string = (
        encoded_string.replace("%2d", "-")
        .replace("%5f", "_")
        .replace("%2e", ".")
        .replace("%21", "!")
        .replace("%2a", "*")
        .replace("%28", "(")
        .replace("%29", ")")
        .replace("%20", "+")
    )
    return hashlib.sha256(fixed_string.encode('utf-8')).hexdigest().upper()

def create_ecpay_params(order_id: int, amount: int, item_name: str):
    host = os.getenv("HOST_URL")
    tz_taiwan = timezone(timedelta(hours=8))
    now_taiwan = datetime.now(tz_taiwan)
    
    params = {
        "MerchantID": os.getenv("ECPAY_MERCHANT_ID"),
        "MerchantTradeNo": f"ORDER{order_id}T{int(now_taiwan.timestamp())}",
        "MerchantTradeDate": now_taiwan.strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": amount,
        "TradeDesc": "Mini Ecommerce Order",
        "ItemName": item_name,
        "ReturnURL": f"{host}/webhooks/ecpay", 
        "ChoosePayment": "ALL",
        "EncryptType": 1,
        "CustomField1": str(order_id), 
    }

    params["CheckMacValue"] = generate_check_mac_value(params)
    return params

def verify_ecpay_checksum(params: dict) -> bool:
    test_params = params.copy()
    received_mac = test_params.pop("CheckMacValue", None)
    if not received_mac: return False
    return generate_check_mac_value(test_params) == received_mac
