# WW 打卡系統使用說明

## 快速開始

### 方法 1：使用主腳本（推薦）

```bash
# 上班打卡
python test_check_in_complete.py Time-In

# 下班打卡
python test_check_in_complete.py Time-Out

# 自動判斷（根據當前時間）
python test_check_in_complete.py
```

### 方法 2：使用互動式腳本

```bash
# 互動模式
python run_check_in.py

# 直接指定參數
python run_check_in.py Time-In    # 上班打卡
python run_check_in.py Time-Out   # 下班打卡
python run_check_in.py auto       # 自動判斷
```

### 方法 3：使用專門腳本

```bash
# 上班打卡
python check_in_time_in.py

# 下班打卡
python check_in_time_out.py
```

## 參數說明

| 參數       | 說明     | 使用時機               |
| ---------- | -------- | ---------------------- |
| `Time-In`  | 上班打卡 | 早上到公司時           |
| `Time-Out` | 下班打卡 | 晚上離開公司時         |
| `auto`     | 自動判斷 | 讓系統根據時間自動選擇 |
| 無參數     | 自動判斷 | 預設行為               |

## 時間判斷邏輯

- **8:00-12:00**: 自動選擇 "Time-In" (上班打卡)
- **17:00-19:00**: 自動選擇 "Time-Out" (下班打卡)
- **其他時間**: 預設選擇 "Time-In"

## 使用範例

### 上班時

```bash
python test_check_in_complete.py Time-In
```

### 下班時

```bash
python test_check_in_complete.py Time-Out
```

### 讓系統自動判斷

```bash
python test_check_in_complete.py
```

### 互動式選擇

```bash
python run_check_in.py
# 然後選擇 1、2 或 3
```

## 注意事項

1. 確保已設定 `.env` 檔案中的帳號密碼
2. 腳本目前為模擬模式，不會實際執行打卡
3. 所有操作都會記錄詳細日誌
4. 支援動態 HTML 更新，會自動等待頁面載入完成

## 錯誤處理

如果遇到錯誤，腳本會：

1. 顯示詳細的錯誤訊息
2. 嘗試多種元素查找策略
3. 自動重試最多 3 次
4. 記錄完整的操作日誌
