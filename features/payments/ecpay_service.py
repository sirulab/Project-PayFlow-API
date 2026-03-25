import os
import hashlib
import urllib.parse
import datetime

def generate_check_mac_value(params: dict) -> str:
    sorted_params = sorted(params.items())
    raw_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    hash_key, hash_iv = os.getenv("ECPAY_HASH_KEY"), os.getenv("ECPAY_HASH_IV")
    full_string = f"HashKey={hash_key}&{raw_string}&HashIV={hash_iv}"
    encoded_string = urllib.parse.quote_plus(full_string).lower()
    
    fixed_string = (
        encoded_string.replace("%2d", "-").replace("%5f", "_").replace("%2e", ".")
        .replace("%21", "!").replace("%2a", "*").replace("%28", "(").replace("%29", ")")
    )
    return hashlib.sha256(fixed_string.encode('utf-8')).hexdigest().upper()

def create_ecpay_params(order_id: int, amount: int, item_name: str):
    host = os.getenv("HOST_URL")
    params = {
        "MerchantID": os.getenv("ECPAY_MERCHANT_ID"),
        "MerchantTradeNo": f"ORDER{order_id}T{int(datetime.datetime.now().timestamp())}",
        "MerchantTradeDate": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
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