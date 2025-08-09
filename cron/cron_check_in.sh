#!/bin/bash

# WW auto check-in script - for crontab use
# Set environment variables and working directory

# Set script directory
SCRIPT_DIR="/Users/zane/git/ww_check_in"
cd "$SCRIPT_DIR"

# Set Python path
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Set log file
LOG_FILE="$SCRIPT_DIR/logs/cron_check_in_$(date +%Y%m%d_%H%M%S).log"

# Create log directory
mkdir -p "$SCRIPT_DIR/logs"

# Log start time
echo "=== Auto check-in started $(date) ===" >> "$LOG_FILE"

# Run check-in script
python3 "$SCRIPT_DIR/test_check_in_complete.py" >> "$LOG_FILE" 2>&1

# Log end time and result
if [ $? -eq 0 ]; then
    echo "=== Auto check-in succeeded $(date) ===" >> "$LOG_FILE"
else
    echo "=== Auto check-in failed $(date) ===" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"