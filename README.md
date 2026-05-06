# Project-PayFlow-API

Project-PayFlow-API 是一個輕量級的微型電商與金流整合後端 API 系統。
實作現代非同步與事件驅動架構的核心概念：
從建立商品 (Product)、產生訂單 (Order) 並自動串接綠界支付 (ECPay)，到接收 Webhook 處理付款狀態，以及非同步扣除庫存與寄發 Email 通知。

### 核心功能 (Core Features)

* **純 API 驅動設計**：提供 RESTful API 端點進行商品與訂單的建立，並利用 `FastAPI` 搭配 `python-multipart` 處理來自綠界 Webhook 的表單資料 (Form Data) 回傳。
* **第三方金流整合 (ECPay)**：系統自動生成金流檢查碼 (CheckMacValue) 並回傳自動導向的 HTML 表單；同時提供 Webhook 端點 (`/webhooks/ecpay`) 驗證綠界回傳的簽章並處理訂單狀態流轉。
* **事件驅動與非同步處理**：內建非同步事件匯流排 (`EventBus`)，當綠界回報付款成功 (`PAYMENT_SUCCESS`) 時，系統會在背景自動扣除資料庫庫存，避免阻塞主執行緒。
* **自動化 Email 通知**：整合 `aiosmtplib` 套件，在訂單付款成功並完成庫存扣除後，非同步發送 HTML 格式的訂單確認電子郵件給消費者。
* **高安全性配置管理**：利用 `python-dotenv` 安全地從 `.env` 檔案載入系統敏感資訊，如綠界 API 金鑰 (HashKey/HashIV)、主機網址以及 SMTP 郵件伺服器的帳密配置。

### 技術棧 (Tech Stack)

* **核心框架**：Python 13.3k, astAPI
* **資料庫 ORM**：SQLModel
* **非同步通訊與寄信**：asyncio, aiosmtplib
* **環境變數管理**：python-dotenv

### 資料表模型

本專案採用輕量級的關聯式資料庫設計：

1. `Product`: 儲存可供購買的商品資訊（包含名稱 `name`、價格 `price` 與庫存 `stock`）。
2. `Order`: 紀錄消費者的購買請求（包含關聯的 `product_id`、付款狀態 `status`、總金額 `amount` 與建立時間 `created_at`）。

### 資料夾結構

```text
Project-PayFlow-API/
├── main.py                 
├── core/                   
│   ├── database.py         
│   ├── celery_app.py       # Celery & Redis 連線
│   └── email.py            # SMTP郵件寄送
├── features/              
│   ├── products/
│   │   ├── router.py       
│   │   └── models.py       
│   ├── orders/
│   │   ├── router.py       
│   │   ├── service.py      
│   │   └── models.py       
│   └── payments/           
│       ├── router.py         # Webhook 路由
│       ├── ecpay_service.py  # 綠界加密與參數計算
│       └── tasks.py          # Celery 背景任務 (扣庫存、寄信)
├── tests/                  
├── main.py                 
├── docker-compose.yml      
├── Dockerfile              
├── requirements.txt        
└── .env                    

```

### 本地端開發設定

請依照以下步驟在本地環境中運行本 API 專案：

* **1. 複製專案與建立虛擬環境**

```bash
git clone https://github.com/sirulab/Project-PayFlow-API.git
cd Project-PayFlow-API
python -m venv venv

# 啟動虛擬環境 (Windows)
venv\Scripts\activate
```

* **2. 安裝依賴套件**

本專案依賴 FastAPI、SQLModel 與非同步寄信等套件，請執行以下指令進行安裝：

```bash
pip install -r requirements.txt
```

* **3. 設定環境變數**

在專案根目錄建立 `.env` 檔案，並填入以下必要資訊：

```ini
HOST_URL=http://your-ngrok-url.com

# Email SMTP 設定
MAIL_HOST=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USER=fabc8bbb3dfc3e
MAIL_PASSWORD=a328101e0a82d9
MAIL_FROM=test@payflow.com
MAIL_TO=customer@example.com

# 綠界測試環境金鑰
# 官方測試參數: https://developersmock.ecpay.com.tw/?APIurl=https%3A%2F%2Fdevelopers.ecpay.com.tw%2F2864%2F -> 加密金鑰設定
ECPAY_MERCHANT_ID=3002607
ECPAY_HASH_KEY=pwFHCqoQZGmho4w6
ECPAY_HASH_IV=EkRm7iFT261dpevs

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

* **4. 設定 ngrok 內網穿透 (Webhook 測試必備)**

為了讓綠界金流能夠將付款狀態回傳給你的本地伺服器 (/webhooks/ecpay)，使用 ngrok 將本機的 8000 port 暴露到外網。
a. 下載並安裝 ngrok。
b. 開啟一個新的終端機視窗，執行以下指令：
```
ngrok http 8000
```
c. 終端機會顯示一段類似 https://a1b2-34-56-78-90.ngrok-free.app 的 ngrok 網址。

* **5. 設定環境變數**

a. 根據 .env 檔案，以及終端機顯示的 ngrok 網址填入 HOST_URL
b. uvicorn 伺服器與 ngrok 同時在運行: 前往 http://54.252.216.152/docs
c. 測試完整的「下單 -> 綠界付款 -> Webhook 接收 -> 自動寄信」的完整金流循環。

### AWS 測試環節與驗證步驟

目前系統運行於 AWS 測試機上。測試完整的「下單 -> 綠界付款 -> Webhook 接收 -> 自動寄信」的完整金流循環：

a. 打開瀏覽器前往：http://54.252.216.152/docs (Swagger UI)

b. 發起訂單

在 /orders 端點中輸入商品資訊下訂單，系統會回傳一組綠界表單參數與 CheckMacValue。

c. 本地端的test.html

```
<!-- 模擬前端跳轉 (POST) -->
<form action="https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5" method="POST">
    <!-- API 回傳的 綠界表單參數與 CheckMacValue 全部寫成 input -->
    <input type="hidden" name="MerchantID" value="3002607">
    <input type="hidden" name="MerchantTradeNo" value="ORDER14T1777891050">
    <input type="hidden" name="MerchantTradeDate" value="2026/05/04 18:37:30">
    <input type="hidden" name="PaymentType" value="aio">
    <input type="hidden" name="TotalAmount" value="1000">
    <input type="hidden" name="TradeDesc" value="Mini Ecommerce Order">
    <input type="hidden" name="ItemName" value="chair">
    <input type="hidden" name="ReturnURL" value="http://54.252.216.152/webhooks/ecpay">
    <input type="hidden" name="ChoosePayment" value="ALL">
    <input type="hidden" name="EncryptType" value="1">
    <input type="hidden" name="CustomField1" value="14">
    <input type="hidden" name="CheckMacValue" value="21D3828464BFA1AA831FA569D2B8A1EBF65F37BDE4D6196C91176A0678AD****">
    
    <input type="submit" value="模擬前端跳轉 (POST)">
</form>
```

d. (選用) 

若需檢查參數與 CheckMacValue 是否吻合，可使用綠界官方模擬前端檢查工具: https://developersmock.ecpay.com.tw/?APIurl=https%3A%2F%2Fdevelopers.ecpay.com.tw%2F2864%2F

e. 進行模擬付款

https://developers.ecpay.com.tw/2856/
使用綠界官方測試信用卡卡號（如 4311-9511-1111-1111）進行付款。

f. 等待與驗證
付款成功後，請等待約 10 分鐘。

g. 檢查 API 狀態：使用 GET /products 檢查庫存是否正確扣除。

h. 檢查信箱：登入 Mailtrap 檢查是否收到「付款成功確認信」。

### 待改進事項 (To-Do List)

[ ] 補齊測試截圖紀錄：將以下畫面的截圖補充進文件中，方便展示：

- Swagger UI 畫面
- 綠界信用卡輸入畫面
- 付款成功跳轉畫面
- 收到 Email 的截圖
- 產品庫存成功扣除的畫面
- AWS 終端機 (API + Worker) 的成功運作日誌 (Logs) 截圖。

[ ] 優化前端結帳體驗：目前需手動將 API 回傳的參數填入模擬前端跳轉 (POST)，未來應設計一個「自動帶入參數並跳轉 (Auto-Submit Form)」的簡易前端 HTML，點擊後直接導向綠界結帳頁面。

[ ] 釐清「10分鐘延遲」的原因：調查為什麼付款後需要等待近 10 分鐘才完成流程。需排查是綠界測試環境 Webhook 發送延遲、Celery Task Queue 處理設定，還是 Mailtrap 寄信的 Throttle 限制。
