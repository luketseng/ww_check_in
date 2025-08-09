#!/bin/bash

echo "=================================================="
echo "WW Check-in System - Mac Local Setup"
echo "=================================================="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add Homebrew to PATH
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    echo "✅ Homebrew found"
fi

# Install ChromeDriver
echo "🔧 Installing ChromeDriver..."
brew install --cask chromedriver

# Check ChromeDriver installation
if command -v chromedriver &> /dev/null; then
    echo "✅ ChromeDriver installed successfully"
    echo "🧪 ChromeDriver Version: $(chromedriver --version)"
else
    echo "❌ ChromeDriver installation failed"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install selenium==4.15.2 python-dotenv==1.0.0 schedule==1.2.0

# Create logs directory
mkdir -p logs

# Set up .env file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your credentials"
fi

echo "=================================================="
echo "✅ Mac local setup completed!"
echo "=================================================="
echo "Next steps:"
echo "1. Edit .env file with your login credentials"
echo "2. Run: ./run_local.sh"
echo "=================================================="