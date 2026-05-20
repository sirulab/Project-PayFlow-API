from features.payments.ecpay_service import generate_check_mac_value

def test_read_docs(client):
    response = client.get("/docs")
    assert response.status_code == 200

def test_ecpay_checksum_generation(monkeypatch):
    # 模擬環境變數
    monkeypatch.setenv("ECPAY_HASH_KEY", "pwFHCqoQZGmho4w6")
    monkeypatch.setenv("ECPAY_HASH_IV", "EkRm7iFT261dpeov")
    
    mock_params = {
        "MerchantID": "3002607",
        "MerchantTradeNo": "ORDER_TEST_123",
        "TotalAmount": 100,
        "TradeDesc": "Test Item"
    }
    
    mac_value = generate_check_mac_value(mock_params)
    
    assert isinstance(mac_value, str)
    assert len(mac_value) == 64
    assert mac_value.isupper()
