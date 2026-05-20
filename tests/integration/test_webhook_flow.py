from fastapi.testclient import TestClient
from sqlmodel import Session
from unittest.mock import patch

from features.products.models import Product
from features.orders.models import Order

# Webhook 接收 + 時間差問題
def test_ecpay_webhook_success_and_log(client: TestClient, session: Session, caplog):
    """
    測試情境：綠界回傳付款成功 (RtnCode=1)，更新訂單狀態並call非同步任務
    """
    # 1. 準備假資料 (Arrange)
    product = Product(name="Test Chair", price=1000, stock=5)
    session.add(product)
    session.commit()
    
    order = Order(product_id=product.id, amount=1000, status="pending")
    session.add(order)
    session.commit()

    with patch("features.payments.router.verify_ecpay_checksum", return_value=True), \
         patch("features.payments.router.process_payment_success_task.delay") as mock_celery_delay:
        
        fake_webhook_data = {
            "CustomField1": str(order.id),
            "RtnCode": "1",
            "SimulatePaid": "0",
            "CheckMacValue": "FAKE_MAC_VALUE"
        }

        response = client.post("/webhooks/ecpay", data=fake_webhook_data)

        assert response.text == '"1|OK"'
        
        session.refresh(order)
        assert order.status == "paid"
        
        assert mock_celery_delay.called
        mock_celery_delay.assert_called_once_with(order.id)
        assert "付款完成，已推送任務至 Celery" in caplog.text


#  測試非同步任務: 扣庫存與寄信

def test_process_payment_success_task(session: Session, caplog):
    """
    測試情境：Celery 任務執行，正確扣除庫存+call寄信
    """
    from features.payments.tasks import process_payment_success_task

    product = Product(name="Test Chair", price=1000, stock=5)
    session.add(product)
    session.commit()
    
    order = Order(product_id=product.id, amount=1000, status="paid")
    session.add(order)
    session.commit()

    with patch("features.payments.tasks.send_email_notification") as mock_email, \
         patch("features.payments.tasks.engine", session.bind):
        
        result = process_payment_success_task(order.id)

        assert "處理成功" in result
        
        session.refresh(product)
        assert product.stock == 4
        assert "剩餘庫存 4" in caplog.text
        assert mock_email.called