# WW Check-in System

自動化網頁打卡系統，使用 Python 和 Selenium 實現自動登入和打卡功能。

## 功能特色

- 🔐 自動登入系統
- ⏰ 可配置的工作時間（週一至週四，8:30 上班，18:00 下班）
- 📝 詳細的日誌記錄
- 🔧 可配置的環境變數
- 🐳 支援 Podman 容器化運行
- 💻 支援 Mac 本地運行

## 系統需求

### Podman 容器運行

- Podman 已安裝
- 網路連接（用於下載 Docker 映像）

### Mac 本地運行

- Python 3.9+
- Google Chrome 瀏覽器
- Homebrew（用於安裝 ChromeDriver）

## 快速開始

### 方法一：Mac 本地運行（推薦，無需網路限制）

1. **設置環境**

   ```bash
   ./setup_mac_local.sh
   ```

2. **配置登入資訊**

   ```bash
   # 編輯 .env 文件，填入你的帳號密碼
   nano .env
   ```

3. **運行系統**
   ```bash
   ./run_local.sh
   ```

### 方法二：Podman 容器運行

1. **設置環境**

   ```bash
   # 複製環境變數範例
   cp env.example .env

   # 編輯 .env 文件，填入你的帳號密碼
   nano .env
   ```

2. **建置並運行容器**
   ```bash
   ./run_with_podman.sh
   ```

## 配置說明

### 環境變數 (.env)

```bash
# 登入資訊
WW_USERNAME=your_username
WW_PASSWORD=your_password

# 工作時間配置
WORK_DAYS=1,2,3,4          # 週一到週四
WORK_START_TIME=08:30      # 上班時間
WORK_END_TIME=18:00        # 下班時間

# 日誌配置
LOG_LEVEL=INFO
LOG_FILE=logs/logs.txt

# 瀏覽器配置
HEADLESS=false             # true=無頭模式，false=顯示瀏覽器
IMPLICIT_WAIT=10           # 隱式等待時間（秒）
PAGE_LOAD_TIMEOUT=30       # 頁面載入超時（秒）
```

## 專案結構

```
ww_check_in/
├── ww_check_in.py          # 主程式
├── utils/
│   └── selenium_helper.py  # Selenium 輔助類
├── config/
│   └── schedule_config.py  # 排程配置
├── logs/                   # 日誌目錄
├── .env                    # 環境變數
├── env.example            # 環境變數範例
├── requirements.txt       # Python 依賴
├── setup_mac_local.sh     # Mac 本地設置腳本
├── run_local.sh           # Mac 本地運行腳本
├── run_with_podman.sh     # Podman 運行腳本
└── README.md              # 說明文件
```

## 開發狀態

### ✅ 已完成

- [x] 專案基礎架構
- [x] 環境變數配置
- [x] 日誌系統
- [x] Selenium 輔助類
- [x] 登入功能實現
- [x] Mac 本地運行支援
- [x] Podman 容器化支援

### 🔄 進行中

- [ ] 打卡功能實現（等待 HTML 元素）

### 📋 待開發

- [ ] 自動排程功能
- [ ] 錯誤處理和重試機制
- [ ] 通知功能
- [ ] 測試案例

## 故障排除

### 常見問題

1. **ChromeDriver 版本不匹配**

   - 本地運行：運行 `./setup_mac_local.sh` 重新安裝
   - 容器運行：重新建置容器

2. **網路連接問題**

   - 使用 Mac 本地運行方式，無需外部網路

3. **權限問題**

   - 確保腳本有執行權限：`chmod +x *.sh`

4. **登入失敗**
   - 檢查 `.env` 文件中的帳號密碼
   - 查看 `logs/logs.txt` 中的錯誤訊息

### 日誌查看

```bash
# 查看即時日誌
tail -f logs/logs.txt

# 查看完整日誌
cat logs/logs.txt
```

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 授權

本專案僅供學習和研究使用。
