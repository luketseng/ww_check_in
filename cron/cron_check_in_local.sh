#!/usr/bin/env bash
set -euo pipefail

# WW auto check-in script (LOCAL, no containers)
# - Designed for Linux/macOS cron
# - Uses Python from PATH and runs project script directly

# Resolve script directory and project directory (parent of this script)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Prefer a fixed default project path if it exists; fallback to script's parent
DEFAULT_PROJECT_DIR="/Users/zane/git/ww_check_in"
if [ -d "$DEFAULT_PROJECT_DIR" ]; then
  PROJECT_DIR="${PROJECT_DIR:-$DEFAULT_PROJECT_DIR}"
else
  PROJECT_DIR="${PROJECT_DIR:-$(cd "$SCRIPT_DIR/.." && pwd)}"
fi

# Choose the Python entry script (default: ww_check_in.py)
RUN_SCRIPT="${RUN_SCRIPT:-ww_check_in.py}"

# PATH setup (adjust if your Python is installed elsewhere)
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Logs
mkdir -p "$PROJECT_DIR/logs"
LOG_FILE="$PROJECT_DIR/logs/cron_check_in_local_$(date +%Y%m%d_%H%M%S).log"

# Prefer .env values over inherited environment unless explicitly disabled
export PREFER_DOTENV="${PREFER_DOTENV:-true}"

# Chrome and ChromeDriver configuration
export CHROME_BINARY="${CHROME_BINARY:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
export USE_WEBDRIVER_MANAGER="${USE_WEBDRIVER_MANAGER:-true}"

# Optional punch argument can be provided via env PUNCH or first CLI arg
PUNCH="${PUNCH:-${1:-}}"

{
  echo "=== Local auto check-in started $(date) ==="
  echo "PROJECT_DIR=$PROJECT_DIR"
  echo "RUN_SCRIPT=$RUN_SCRIPT"
  echo "HEADLESS=${HEADLESS:-true}"
  echo "PREFER_DOTENV=${PREFER_DOTENV}"
  if [ -n "$PUNCH" ]; then echo "PUNCH=$PUNCH"; fi

  cd "$PROJECT_DIR"
  if [ -n "$PUNCH" ]; then
    HEADLESS=${HEADLESS:-true} python3 "$RUN_SCRIPT" "$PUNCH"
  else
    HEADLESS=${HEADLESS:-true} python3 "$RUN_SCRIPT"
  fi
  rc=$?

  if [ $rc -eq 0 ]; then
    echo "=== Local auto check-in succeeded $(date) ==="
  else
    echo "=== Local auto check-in failed $(date) (rc=$rc) ==="
  fi
  echo
} >>"$LOG_FILE" 2>&1
