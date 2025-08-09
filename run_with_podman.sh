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
    echo "Please install Podman first:"
    echo "brew install podman"
    exit 1
fi

echo "✅ Podman found"
echo "✅ .env file found"

# Build the container
echo ""
echo "Building container..."
podman build -t ww-check-in .

if [ $? -eq 0 ]; then
    echo "✅ Container built successfully"
else
    echo "❌ Container build failed"
    exit 1
fi

# Run the container
echo ""
echo "Running WW Check-in System..."
echo "=================================================="

podman run --rm \
    -v "$(pwd):/app" \
    -v "$(pwd)/logs:/app/logs" \
    ww-check-in

echo ""
echo "=================================================="
echo "WW Check-in System completed"
echo "Check logs/ww_check_in.log for details"
echo "=================================================="