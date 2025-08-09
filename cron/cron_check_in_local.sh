#!/usr/bin/env bash
set -euo pipefail

# WW auto check-in script (LOCAL, no containers)
# - Designed for Linux/macOS cron
# - Uses Python from PATH and runs project script directly

# Resolve project directory (directory of this script by default)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$SCRIPT_DIR}"

# Choose the Python entry script (default: ww_check_in.py)
RUN_SCRIPT="${RUN_SCRIPT:-ww_check_in.py}"

# PATH setup (adjust if your Python is installed elsewhere)
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Logs
mkdir -p "$PROJECT_DIR/logs"
LOG_FILE="$PROJECT_DIR/logs/cron_check_in_local_$(date +%Y%m%d_%H%M%S).log"

{
  echo "=== Local auto check-in started $(date) ==="
  echo "PROJECT_DIR=$PROJECT_DIR"
  echo "RUN_SCRIPT=$RUN_SCRIPT"
  echo "HEADLESS=${HEADLESS:-true}"

  cd "$PROJECT_DIR"
  HEADLESS=${HEADLESS:-true} python3 "$RUN_SCRIPT"
  rc=$?

  if [ $rc -eq 0 ]; then
    echo "=== Local auto check-in succeeded $(date) ==="
  else
    echo "=== Local auto check-in failed $(date) (rc=$rc) ==="
  fi
  echo
} >>"$LOG_FILE" 2>&1


