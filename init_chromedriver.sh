#!/bin/bash
set -e

# Install the correct version of chromedriver for ARM64
echo "🔧 Installing chromedriver for ARM64 architecture..."
# Use a more recent version that supports ARM64
wget -q https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip -o chromedriver_linux64.zip && \
    mv -f chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

# Display installed Chrome/Chromium version
if command -v chromium-browser &> /dev/null; then
    echo "🧭 Chromium Version: $(chromium-browser --version)"
elif command -v google-chrome &> /dev/null; then
    echo "🧭 Chrome Version: $(google-chrome --version)"
else
    echo "⚠️  No Chrome/Chromium found"
fi

# Display installed ChromeDriver version
echo "🧪 ChromeDriver Version: $(chromedriver --version)"

echo "✅ ChromeDriver installation completed"