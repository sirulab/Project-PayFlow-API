# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app
from features.payments.ecpay_service import generate_check_mac_value
import os

client = TestClient(app)

# 測試 1: 確保 API 伺服器能正常啟動且路由存在
def test_read_docs():
    response = client.get("/docs")
    assert response.status_code == 200

# 測試 2: 測試綠界金流的 CheckMacValue 雜湊演算法是否正確
def test_ecpay_checksum_generation(monkeypatch):
    # Mock (模擬) 環境變數，避免依賴真實的 .env 檔案
    monkeypatch.setenv("ECPAY_HASH_KEY", "pwFHCqoQZGmho4w6")
    monkeypatch.setenv("ECPAY_HASH_IV", "EkRm7iFT261dpeov")
    
    mock_params = {
        "MerchantID": "3002607",
        "MerchantTradeNo": "ORDER_TEST_123",
        "TotalAmount": 100,
        "TradeDesc": "Test Item"
    }
    
    # 執行你的演算法
    mac_value = generate_check_mac_value(mock_params)
    
    # 斷言：確保產出的字串是 SHA256 加密後的大寫字串
    assert isinstance(mac_value, str)
    assert len(mac_value) == 64 # SHA256 長度為 64
    assert mac_value.isupper() # 必須全大寫