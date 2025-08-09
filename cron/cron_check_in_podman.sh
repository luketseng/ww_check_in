#!/usr/bin/env bash
set -euo pipefail

# WW auto check-in script (Podman)
# - Works on macOS/Linux/WSL
# - Default container command is 'podman'. Override via env PODMAN_CMD=podman-wsl on WSL.
# - Runs a container with project bind-mounted

# Required variables (override via env or before the command in crontab):
#   PROJECT_DIR: path to project in current OS (e.g., /home/you/ww_check_in)
#   IMAGE: container image tag (default: ww-check-in:offline-v1)
#   HEADLESS: true/false (default: true)
# Optional:
#   NAME: container name for daemon mode (default: wwci)
#   MODE: run | daemon | exec (default: run)
#   RUN_SCRIPT: script to run inside container when MODE=exec (default: ww_check_in.py)
#   PODMAN_CMD: container CLI (default: podman). Use 'podman-wsl' on WSL if configured.

PROJECT_DIR="${PROJECT_DIR:-$HOME/ww_check_in}"
IMAGE="${IMAGE:-ww-check-in:offline-v1}"
HEADLESS="${HEADLESS:-true}"
NAME="${NAME:-wwci}"
MODE="${MODE:-run}"
RUN_SCRIPT="${RUN_SCRIPT:-ww_check_in.py}"
PODMAN_CMD="${PODMAN_CMD:-podman}"

LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/cron_check_in_wsl_podman_$(date +%Y%m%d_%H%M%S).log"

{
  echo "=== WSL Podman auto check-in started $(date) ==="
  echo "PROJECT_DIR=$PROJECT_DIR"
  echo "IMAGE=$IMAGE"
  echo "MODE=$MODE"
  echo "PODMAN_CMD=$PODMAN_CMD"

  cd "$PROJECT_DIR"

  case "$MODE" in
    run)
      # One-shot container
      "$PODMAN_CMD" run --rm \
        --env-file ./.env \
        -e HEADLESS="$HEADLESS" \
        -v "$PROJECT_DIR:/app" \
        -v "$PROJECT_DIR/logs:/app/logs" \
        "$IMAGE"
      rc=$?
      ;;
    daemon)
      # Ensure daemon is up
      if ! "$PODMAN_CMD" ps --format '{{.Names}}' | grep -q "^$NAME$"; then
        "$PODMAN_CMD" run -d --name "$NAME" \
          --env-file ./.env \
          -e HEADLESS="$HEADLESS" \
          -v "$PROJECT_DIR:/app" \
          -v "$PROJECT_DIR/logs:/app/logs" \
          "$IMAGE" sleep infinity
      fi
      # Exec the job in the running container
      "$PODMAN_CMD" exec "$NAME" bash -lc "python3 /app/$RUN_SCRIPT"
      rc=$?
      ;;
    exec)
      # Exec into existing container NAME
      "$PODMAN_CMD" exec "$NAME" bash -lc "python3 /app/$RUN_SCRIPT"
      rc=$?
      ;;
    *)
      echo "Invalid MODE: $MODE"; rc=2
      ;;
  esac

  if [ ${rc:-1} -eq 0 ]; then
    echo "=== WSL Podman auto check-in succeeded $(date) ==="
  else
    echo "=== WSL Podman auto check-in failed $(date) (rc=${rc:-1}) ==="
  fi
  echo
} >>"$LOG_FILE" 2>&1


