from features.products.models import Product
from features.orders.models import Order

def test_create_order_success(client, session, monkeypatch):
    """測試情境：庫存充足時，成功建立訂單並回傳綠界表單"""
    monkeypatch.setenv("HOST_URL", "http://testserver")
    monkeypatch.setenv("ECPAY_MERCHANT_ID", "3002607")

    product = Product(name="Gaming Mouse", price=1500, stock=10)
    session.add(product)
    session.commit()

    response = client.post(f"/orders/?product_id={product.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "訂單建立成功"
    assert "payment_info" in data
    
    order_id = data["order_id"]
    order_in_db = session.get(Order, order_id)
    assert order_in_db is not None
    assert order_in_db.amount == 1500
    assert order_in_db.status == "pending"


def test_create_order_out_of_stock_fails(client, session):
    """測試情境 (Edge Case)：商品庫存為 0 時"""
    
    product = Product(name="Gaming Mouse", price=1500, stock=0)
    session.add(product)
    session.commit()

    response = client.post(f"/orders/?product_id={product.id}")

    assert response.status_code == 400
    assert response.json()["detail"] == "庫存不足"
