#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "Local Setup for macOS/Linux (without Podman)"
echo "=================================================="

OS_NAME="$(uname -s)" || OS_NAME=""

if [[ "$OS_NAME" == "Darwin" ]]; then
  echo "🔎 Detected macOS"
  if ! command -v brew >/dev/null 2>&1; then
    echo "❌ Homebrew not found. Please install from https://brew.sh then re-run."
    exit 1
  fi
  echo "📦 Installing ChromeDriver via Homebrew (requires Chrome.app)..."
  brew install --cask chromedriver || true
  echo "📦 Installing Python deps..."
  pip3 install -r requirements.txt
elif [[ "$OS_NAME" == "Linux" ]]; then
  echo "🔎 Detected Linux"
  # Optional: install Chromium/Chrome & chromedriver if available via apt (Ubuntu example)
  if command -v apt-get >/dev/null 2>&1; then
    echo "📦 Installing system packages (sudo required)..."
    sudo apt-get update -y
    # Try to install Chromium and chromedriver (versions may vary). If not available, skip.
    sudo apt-get install -y chromium-browser chromium-chromedriver || true
  fi
  echo "📦 Installing Python deps..."
  pip3 install -r requirements.txt
else
  echo "❌ Unsupported OS: $OS_NAME"
  exit 1
fi

mkdir -p logs
if [ ! -f .env ]; then
  cp -n env.example .env || true
  echo "📝 Created .env (please edit credentials)"
fi

echo "✅ Local setup completed. Run examples:"
echo "  HEADLESS=true python3 ww_check_in.py"
echo "  HEADLESS=true python3 test_check_in_complete_v2.py"


