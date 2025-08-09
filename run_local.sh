#!/bin/bash

echo "=================================================="
echo "WW Check-in System - Local Runner"
echo "=================================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please run setup_mac_local.sh first or create .env file manually"
    exit 1
fi

# Check if ChromeDriver is available
if ! command -v chromedriver &> /dev/null; then
    echo "❌ ChromeDriver not found!"
    echo "Please run setup_mac_local.sh first"
    exit 1
fi

echo "✅ Environment check passed"
echo "🧪 ChromeDriver Version: $(chromedriver --version)"

# Create logs directory if not exists
mkdir -p logs

echo "🚀 Starting WW Check-in System..."
echo "=================================================="

# Run the Python script
python3 ww_check_in.py

echo "=================================================="
echo "✅ Script execution completed"
echo "📋 Check logs/logs.txt for details"
echo "=================================================="