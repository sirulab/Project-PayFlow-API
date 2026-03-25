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
│   ├── event_bus.py        # 事件系統實作
│   └── email.py            # 郵件寄送邏輯
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
│       └── event_handlers.py # 處理支付成功後的庫存與郵件
├── templates/              
│   ├── index.html          
│   ├── payment_redirect.html 
│   └── order_status.html   
└── requirements.txt

```

### 本地端開發設定

請依照以下步驟在本地環境中運行本 API 專案：

### 1. 複製專案與建立虛擬環境

```bash
git clone https://github.com/sirulab/Project-PayFlow-API.git
cd Project-PayFlow-API
python -m venv venv

# 啟動虛擬環境 (Windows)
venv\Scripts\activate

```

### 2. 安裝依賴套件

本專案依賴 FastAPI、SQLModel 與非同步寄信等套件，請執行以下指令進行安裝：

```bash
pip install -r requirements.txt

```

### 3. 設定環境變數

在專案根目錄建立 `.env` 檔案，並填入以下必要資訊：

```ini
HOST_URL=http://your-ngrok-url.com

# Email SMTP 設定
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USER=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your_email@gmail.com
MAIL_TO=customer@example.com

# 綠界測試環境金鑰
ECPAY_MERCHANT_ID=3002607
ECPAY_HASH_KEY=pwFHCqoQZGmho4w6
ECPAY_HASH_IV=EkRm7iFT261dpeov

```

### 4. 設定 ngrok 內網穿透 (Webhook 測試必備)
為了讓綠界金流能夠將付款狀態回傳給你的本地伺服器 (/webhooks/ecpay)，你需要使用 ngrok 將本機的 8000 port 暴露到外網。
1. 下載並安裝 ngrok。
2. 開啟一個新的終端機視窗，執行以下指令：
```
ngrok http 8000
```
3. 終端機會顯示一段類似 https://a1b2-34-56-78-90.ngrok-free.app 的 Forwarding URL，請將其複製起來。

### 5. 設定環境變數
在專案根目錄建立 .env 檔案，並將剛剛複製的 ngrok 網址填入 HOST_URL，同時補上其他必要資訊：
```
# 將這裡替換為你的 ngrok HTTPS 網址 (結尾不要加斜線)
HOST_URL=https://a1b2-34-56-78-90.ngrok-free.app

# Email SMTP 設定 (測試寄信功能用)
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USER=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your_email@gmail.com
MAIL_TO=customer@example.com

# 綠界測試環境金鑰 (預設可直接使用測試帳號金鑰)
ECPAY_MERCHANT_ID=3002607
ECPAY_HASH_KEY=pwFHCqoQZGmho4w6
ECPAY_HASH_IV=EkRm7iFT261dpeov
```

完成上述設定後，確保 uvicorn 伺服器與 ngrok 同時在運行:
前往 http://127.0.0.1:8000/docs 
測試完整的「下單 -> 綠界付款 -> Webhook 接收 -> 自動寄信」的完整金流循環。

### 測試
綠屆金流官方提供的界接測試:

https://developers.ecpay.com.tw/2856/?gad_source=1&gad_campaignid=21331775467&gbraid=0AAAAADLSIOV1SGdFlGF-BNiZ02o_UXo03&gclid=CjwKCAjwjtTNBhB0EiwAuswYhgxvhH9wB3aWNSO277DRbLV7L6G3Q8gDgXPSCiv5YcuIFWrt2mFaSxoCpvgQAvD_BwE

1.測試信用卡

2.測試用的特店管理後台 https://vendor-stage.ecpay.com.tw/

3.測試收件email: chensiru.sjtu@gmail.com (儲存於環境變數中)
