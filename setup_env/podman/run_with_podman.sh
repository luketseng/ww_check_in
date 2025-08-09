#!/bin/bash

# WW Check-in System - Podman Runner Script

set -e

echo "=================================================="
echo "WW Check-in System - Podman Runner"
echo "=================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy env.example to .env and configure your credentials:"
    echo "cp env.example .env"
    echo "Then edit .env with your username and password"
    exit 1
fi

# Check if podman is available
if ! command -v podman &> /dev/null; then
    echo "❌ Podman not found!"
    echo "Please install Podman first (examples):"
    echo "- macOS:   brew install podman && podman machine init && podman machine start"
    echo "- Windows: winget install -e --id RedHat.Podman && podman machine init && podman machine start"
    echo "- Linux:   use your distro package manager"
    exit 1
fi

echo "✅ Podman found"
echo "✅ .env file found"

ACTION=${1:-run}

case "$ACTION" in
  build)
    echo ""; echo "Building container..."
    podman build -t ww-check-in .
    ;;
  run)
    echo ""; echo "Running WW Check-in System..."; echo "=================================================="
    podman run --rm \
      --env-file ./.env \
      -e HEADLESS=${HEADLESS:-true} \
      -v "$(pwd):/app" \
      -v "$(pwd)/logs:/app/logs" \
      ww-check-in
    ;;
  daemon)
    echo ""; echo "Starting container in background (sleep infinity)..."
    podman run -d --name wwci \
      --env-file ./.env \
      -e HEADLESS=${HEADLESS:-true} \
      -v "$(pwd):/app" \
      -v "$(pwd)/logs:/app/logs" \
      ww-check-in sleep infinity
    ;;
  *)
    echo "Usage: $0 [build|run|daemon]"; exit 1;
    ;;
esac

echo ""
echo "=================================================="
echo "WW Check-in System completed"
echo "Check logs/ww_check_in.log for details"
echo "=================================================="