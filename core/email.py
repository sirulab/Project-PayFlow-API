import os
import aiosmtplib
from email.message import EmailMessage

async def send_email_notification(order_id: int, amount: int):
    smtp_host = os.getenv("MAIL_HOST")
    smtp_port = int(os.getenv("MAIL_PORT", 587))
    smtp_user = os.getenv("MAIL_USER")
    smtp_password = os.getenv("MAIL_PASSWORD")
    mail_from = os.getenv("MAIL_FROM")
    mail_to = os.getenv("MAIL_TO")

    message = EmailMessage()
    message["From"] = mail_from
    message["To"] = mail_to
    message["Subject"] = f"訂單確認：您的訂單 #{order_id} 已經成功付款！"
    
    html_content = f"""
    <html>
        <body>
            <h2>感謝您的購買！</h2>
            <p>您的訂單 <strong>#{order_id}</strong> 處理完成。</p>
            <p>付款金額：<strong>${amount} TWD</strong></p>
        </body>
    </html>
    """
    message.add_alternative(html_content, subtype="html")

    try:
        await aiosmtplib.send(
            message, hostname=smtp_host, port=smtp_port,
            username=smtp_user, password=smtp_password, start_tls=True,
        )
        print(f" [郵件系統] 成功寄出付款確認信 #{order_id}")
    except Exception as e:
        print(f" [郵件系統] 寄出失敗: {str(e)}")