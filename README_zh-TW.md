# WW 打卡系統（繁體中文）

本專案使用 Python + Selenium 自動化 WW HR 入口網站的登入與打卡。支援本機執行與 Podman 容器模式，也支援使用事先建好的離線映像（tar）檔啟動。

## 需求

- `.env` 檔（由 `env.example` 複製並填入帳密）
- Podman（若使用容器）
  - macOS: `brew install podman && podman machine init && podman machine start`
  - Windows/WSL: 建議使用 `podman-wsl` 包裝器；或使用 Windows Podman Machine
  - Linux: 透過套件管理器安裝

## 使用自訂映像 tar（離線）

1) 載入映像檔

- macOS/Linux:
```bash
podman load -i ww-check-in-offline-v1.tar
```
- WSL（使用 wrapper）:
```bash
podman-wsl load -i ww-check-in-offline-v1.tar
```

2) 掛載專案後執行（一次性）

```bash
# macOS/Linux
podman run --rm \
  --env-file ./.env \
  -e HEADLESS=${HEADLESS:-true} \
  -v "$PWD:/app" \
  -v "$PWD/logs:/app/logs" \
  ww-check-in:offline-v1

# WSL
podman-wsl run --rm \
  --env-file ./.env \
  -e HEADLESS=${HEADLESS:-true} \
  -v "$PWD:/app" \
  -v "$PWD/logs:/app/logs" \
  ww-check-in:offline-v1
```

3) 常駐測試（背景）

```bash
# macOS/Linux
podman run -d --name wwci \
  --env-file ./.env \
  -e HEADLESS=${HEADLESS:-true} \
  -v "$PWD:/app" \
  -v "$PWD/logs:/app/logs" \
  ww-check-in:offline-v1 sleep infinity

# 進入容器
podman exec -it wwci bash
```

在 WSL，將 `podman` 改為 `podman-wsl`。

## 環境設定（setup_env/）

- 本地（不使用容器）：
  - `setup_env/setup_linux_local.sh` 會安裝 Python 依賴（可用時安裝 chromedriver）。
  - 之後可直接執行：
    ```bash
HEADLESS=true python3 ww_check_in.py
# 或者
HEADLESS=true python3 test_check_in_complete_v2.py
    ```

- Podman：
  - macOS/Ubuntu：請先安裝 Podman；macOS 需啟動 Podman Machine。
  - WSL：建議使用 `podman-wsl` 包裝器（Linux 路徑用 overlay，/mnt 路徑自動用 vfs）。
  - 也可在可連網環境自行建置 image，再 `save/load` 至離線環境（見下方備註）。

## Cron 設定（cron/）

- 本地 cron：
  - 腳本：`cron/cron_check_in_local.sh`
  - 範例：`cron/crontab_setup_local.txt`
  - 範例（週一至週四 08:30）：
    ```cron
30 8 * * 1-4 PROJECT_DIR=/home/you/ww_check_in HEADLESS=true /home/you/ww_check_in/cron/cron_check_in_local.sh
    ```

- Podman cron：
  - 腳本：`cron/cron_check_in_podman.sh`
  - 範例：`cron/crontab_setup_podman.txt`
  - 一次性容器（mac/Linux）：
    ```cron
30 8 * * 1-4 PROJECT_DIR=/home/you/ww_check_in HEADLESS=true IMAGE=ww-check-in:offline-v1 /home/you/ww_check_in/cron/cron_check_in_podman.sh
    ```
  - 一次性容器（WSL，使用 wrapper）：
    ```cron
30 8 * * 1-4 PROJECT_DIR=/home/you/ww_check_in HEADLESS=true PODMAN_CMD=podman-wsl IMAGE=ww-check-in:offline-v1 /home/you/ww_check_in/cron/cron_check_in_podman.sh
    ```
  - 常駐模式：開機建立常駐容器，之後以 exec 方式在容器中執行（詳見檔案內容）。

## 直接執行（不使用容器）

先透過 `setup_env/setup_linux_local.sh` 建好環境，然後：
```bash
HEADLESS=true python3 ww_check_in.py
```

## 組態（.env）

- `WW_USERNAME`, `WW_PASSWORD`：登入帳密
- `HEADLESS=true|false`：是否使用無頭模式
- `LOG_LEVEL`, `LOG_FILE`：日誌設定
- Selenium/Driver：
  - `CHROMEDRIVER_PATH`：指定 chromedriver 路徑
  - `CHROME_BINARY`：指定 Chrome/Chromium 路徑
  - `USE_WEBDRIVER_MANAGER=true|false`：需要連網時自動下載對應 driver

## 備註：建置 / 匯出 / 載入（load）映像檔

- 在可連網機器建置：
```bash
podman build -t ww-check-in:offline-v1 .
```

- 匯出 tar：
```bash
podman save -o ww-check-in-offline-v1.tar ww-check-in:offline-v1
```

- 在目標機器載入：
```bash
podman load -i ww-check-in-offline-v1.tar
# WSL：podman-wsl load -i ww-check-in-offline-v1.tar
```

- 執行時請綁定專案目錄（如上所示），這樣修改程式不用重建映像。


